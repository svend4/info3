#!/usr/bin/env python3
"""
Collective Intelligence Swarm
=============================

Множество агентов работают как рой (swarm intelligence).

Вдохновение из природы:
- 🐜 Муравьи: stigmergy (непрямая коммуникация через феромоны)
- 🐝 Пчёлы: waggle dance (обмен информацией)
- 🐦 Птицы: flocking (координация без лидера)
- 🐟 Рыбы: schooling (коллективная защита)

Ключевые концепты:
- Децентрализация: нет центрального контроллера
- Самоорганизация: паттерны возникают спонтанно
- Эмергентность: сложное поведение из простых правил
- Коллективная мудрость: группа умнее индивидуума
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict
from enum import Enum


class ConsensusMethod(Enum):
    """Методы достижения консенсуса"""
    VOTING = "voting"  # Голосование
    AVERAGING = "averaging"  # Усреднение
    STIGMERGY = "stigmergy"  # Феромоны (муравьи)
    LEADER_ELECTION = "leader_election"  # Выбор лидера
    QUORUM_SENSING = "quorum_sensing"  # Кворум (бактерии)


@dataclass
class Message:
    """Сообщение между агентами"""
    from_id: int
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl: int = 3  # Time to live (hops)


@dataclass
class Position:
    """Позиция агента в пространстве знаний"""
    x: float
    y: float

    def distance(self, other: 'Position') -> float:
        """Евклидово расстояние"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class LocalKnowledge:
    """Локальное знание агента"""
    topic: str
    facts: List[str] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class SearchResult:
    """Результат локального поиска"""
    agent_id: int
    answer: str
    confidence: float
    evidence: List[str] = field(default_factory=list)


class SwarmAgent:
    """
    Отдельный агент в рое

    Умеет:
    - Локальный поиск в своей области знаний
    - Коммуникация с соседями
    - Обновление beliefs на основе информации от соседей
    - Участие в консенсусе
    """

    def __init__(self, agent_id: int, position: Position):
        self.id = agent_id
        self.position = position
        self.knowledge: Dict[str, LocalKnowledge] = {}
        self.neighbors: List['SwarmAgent'] = []

        # Beliefs (уверенности) в разных ответах
        self.beliefs: Dict[str, float] = {}

        # Pheromone trails (для stigmergy)
        self.pheromones: Dict[str, float] = defaultdict(float)

        # Message buffer
        self.inbox: List[Message] = []

        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.searches_performed = 0

    def add_knowledge(self, topic: str, facts: List[str], confidence: float = 0.5):
        """Добавить локальное знание"""
        self.knowledge[topic] = LocalKnowledge(
            topic=topic,
            facts=facts,
            confidence=confidence
        )

    def local_search(self, query: str) -> Optional[SearchResult]:
        """
        Локальный поиск в своей области знаний

        Каждый агент знает только часть общей информации
        """
        self.searches_performed += 1
        query_lower = query.lower()

        # Поиск в локальных знаниях
        for topic, knowledge in self.knowledge.items():
            if topic.lower() in query_lower:
                # Найдено в локальных знаниях
                answer = " ".join(knowledge.facts[:2])  # Первые 2 факта
                return SearchResult(
                    agent_id=self.id,
                    answer=answer,
                    confidence=knowledge.confidence,
                    evidence=knowledge.facts
                )

        # Не найдено
        return None

    def communicate(self, message: Message):
        """Отправить сообщение соседям"""
        if message.ttl <= 0:
            return  # Message expired

        for neighbor in self.neighbors:
            # Создаём копию с уменьшенным TTL
            new_message = Message(
                from_id=self.id,
                content=message.content,
                timestamp=message.timestamp,
                ttl=message.ttl - 1
            )
            neighbor.receive_message(new_message)

        self.messages_sent += 1

    def receive_message(self, message: Message):
        """Получить сообщение"""
        self.inbox.append(message)
        self.messages_received += 1

        # Немедленная обработка
        self.integrate_knowledge(message)

    def integrate_knowledge(self, message: Message):
        """Интеграция знаний из сообщения"""
        if 'answer' in message.content and 'confidence' in message.content:
            answer = message.content['answer']
            confidence = message.content['confidence']

            # Обновление beliefs через Bayesian update
            if answer in self.beliefs:
                # Комбинация старого и нового belief
                old_belief = self.beliefs[answer]
                # Weighted average
                self.beliefs[answer] = 0.7 * old_belief + 0.3 * confidence
            else:
                self.beliefs[answer] = confidence * 0.5  # Осторожное принятие

    def update_beliefs(self):
        """Обновление beliefs на основе сообщений от соседей"""
        # Обработка всех сообщений в inbox
        for message in self.inbox:
            if 'pheromone' in message.content:
                # Stigmergy: следование за "феромонами"
                path = message.content['pheromone']
                strength = message.content.get('strength', 0.5)
                self.pheromones[path] += strength

        # Decay pheromones (испарение со временем)
        for path in self.pheromones:
            self.pheromones[path] *= 0.95  # 5% decay

        self.inbox = []  # Clear inbox

    def get_result(self) -> Optional[SearchResult]:
        """Получить текущий результат агента"""
        if not self.beliefs:
            return None

        # Выбрать ответ с наивысшим belief
        best_answer = max(self.beliefs, key=self.beliefs.get)
        best_confidence = self.beliefs[best_answer]

        return SearchResult(
            agent_id=self.id,
            answer=best_answer,
            confidence=best_confidence,
            evidence=[]
        )

    def deposit_pheromone(self, path: str, strength: float = 1.0):
        """Оставить феромон (stigmergy)"""
        self.pheromones[path] += strength


class SwarmIntelligence:
    """
    Рой агентов с коллективным интеллектом

    Принципы:
    - Децентрализация: нет центрального контроллера
    - Распределённость: знания распределены по агентам
    - Самоорганизация: структура возникает спонтанно
    - Эмергентность: сложное поведение из простых правил
    """

    def __init__(
        self,
        n_agents: int = 50,
        neighborhood_size: int = 5,
        consensus_method: ConsensusMethod = ConsensusMethod.VOTING,
        verbose: bool = False
    ):
        self.n_agents = n_agents
        self.neighborhood_size = neighborhood_size
        self.consensus_method = consensus_method
        self.verbose = verbose

        # Создание агентов
        self.agents: List[SwarmAgent] = []
        for i in range(n_agents):
            position = self._random_position()
            agent = SwarmAgent(i, position)
            self.agents.append(agent)

        # Установка связей между соседями
        self.connect_neighbors()

        # Statistics
        self.query_history: List[Dict[str, Any]] = []

    def _random_position(self) -> Position:
        """Случайная позиция в пространстве [0, 100] x [0, 100]"""
        return Position(
            x=random.uniform(0, 100),
            y=random.uniform(0, 100)
        )

    def connect_neighbors(self):
        """Установить связи между ближайшими соседями"""
        for agent in self.agents:
            # Найти k ближайших соседей
            distances = [
                (other, agent.position.distance(other.position))
                for other in self.agents
                if other.id != agent.id
            ]
            distances.sort(key=lambda x: x[1])

            # Подключить k ближайших
            agent.neighbors = [neighbor for neighbor, _ in distances[:self.neighborhood_size]]

        if self.verbose:
            avg_neighbors = sum(len(a.neighbors) for a in self.agents) / len(self.agents)
            print(f"Connected agents: avg {avg_neighbors:.1f} neighbors per agent")

    def distribute_knowledge(self, knowledge_base: Dict[str, List[str]]):
        """
        Распределить знания по агентам

        Каждый агент получает только часть общих знаний
        """
        topics = list(knowledge_base.keys())

        for agent in self.agents:
            # Каждый агент получает знание о 2-3 случайных темах
            agent_topics = random.sample(topics, min(random.randint(2, 3), len(topics)))

            for topic in agent_topics:
                facts = knowledge_base[topic]
                # Агент знает только часть фактов
                agent_facts = random.sample(facts, min(random.randint(1, 3), len(facts)))
                confidence = random.uniform(0.6, 0.9)

                agent.add_knowledge(topic, agent_facts, confidence)

        if self.verbose:
            total_knowledge = sum(len(a.knowledge) for a in self.agents)
            print(f"Distributed knowledge: {total_knowledge} topic assignments across {len(self.agents)} agents")

    def query(self, question: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Обработка запроса роем агентов

        Процесс:
        1. Broadcast вопроса всем агентам
        2. Локальный поиск каждым агентом
        3. Коммуникация между соседями (несколько раундов)
        4. Обновление beliefs
        5. Достижение консенсуса
        """
        if self.verbose:
            print(f"\n=== Swarm Query: '{question}' ===")
            print(f"Agents: {self.n_agents}, Iterations: {iterations}")

        # 1. Локальный поиск всеми агентами
        local_results: List[SearchResult] = []
        for agent in self.agents:
            result = agent.local_search(question)
            if result:
                local_results.append(result)

                # Инициализация beliefs
                agent.beliefs[result.answer] = result.confidence

        if self.verbose:
            print(f"Local search: {len(local_results)}/{self.n_agents} agents found results")

        # 2. Итерации коммуникации
        for iteration in range(iterations):
            if self.verbose:
                print(f"\nIteration {iteration + 1}:")

            # Каждый агент общается с соседями
            for agent in self.agents:
                # Если агент имеет belief, делится им
                if agent.beliefs:
                    best_answer = max(agent.beliefs, key=agent.beliefs.get)
                    confidence = agent.beliefs[best_answer]

                    message = Message(
                        from_id=agent.id,
                        content={
                            'answer': best_answer,
                            'confidence': confidence
                        },
                        ttl=2
                    )

                    agent.communicate(message)

            # Обновление beliefs
            for agent in self.agents:
                agent.update_beliefs()

            if self.verbose:
                active_agents = sum(1 for a in self.agents if a.beliefs)
                print(f"  Active agents: {active_agents}")

        # 3. Сбор результатов
        all_results = []
        for agent in self.agents:
            result = agent.get_result()
            if result:
                all_results.append(result)

        if not all_results:
            return {
                "answer": "No consensus reached",
                "confidence": 0.0,
                "consensus_method": self.consensus_method.value,
                "agents_responded": 0
            }

        # 4. Достижение консенсуса
        consensus = self.reach_consensus(all_results)

        # Запись в историю
        self.query_history.append({
            "query": question,
            "agents_responded": len(all_results),
            "consensus": consensus,
            "timestamp": datetime.now().isoformat()
        })

        return consensus

    def reach_consensus(self, results: List[SearchResult]) -> Dict[str, Any]:
        """
        Достижение консенсуса роем

        Методы:
        - Voting: голосование
        - Averaging: усреднение confidence
        - Stigmergy: следование за "феромонами"
        """
        if self.consensus_method == ConsensusMethod.VOTING:
            return self._voting_consensus(results)
        elif self.consensus_method == ConsensusMethod.AVERAGING:
            return self._averaging_consensus(results)
        elif self.consensus_method == ConsensusMethod.STIGMERGY:
            return self._stigmergy_consensus(results)
        else:
            return self._voting_consensus(results)

    def _voting_consensus(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Консенсус через голосование"""
        votes: Dict[str, float] = defaultdict(float)

        for result in results:
            # Weighted vote: голос весит пропорционально confidence
            votes[result.answer] += result.confidence

        if not votes:
            return {
                "answer": "No answer",
                "confidence": 0.0,
                "consensus_method": "voting",
                "agents_responded": len(results)
            }

        winner = max(votes, key=votes.get)
        total_votes = sum(votes.values())
        consensus_strength = votes[winner] / total_votes if total_votes > 0 else 0.0

        # Average confidence среди агентов, голосовавших за winner
        winner_confidences = [r.confidence for r in results if r.answer == winner]
        avg_confidence = sum(winner_confidences) / len(winner_confidences) if winner_confidences else 0.0

        return {
            "answer": winner,
            "confidence": avg_confidence,
            "consensus_strength": consensus_strength,
            "consensus_method": "voting",
            "vote_distribution": dict(votes),
            "agents_responded": len(results)
        }

    def _averaging_consensus(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Консенсус через усреднение"""
        # Группировка по ответам
        answer_groups: Dict[str, List[float]] = defaultdict(list)

        for result in results:
            answer_groups[result.answer].append(result.confidence)

        # Выбор ответа с наивысшим средним confidence
        avg_confidences = {
            answer: sum(confs) / len(confs)
            for answer, confs in answer_groups.items()
        }

        if not avg_confidences:
            return {
                "answer": "No answer",
                "confidence": 0.0,
                "consensus_method": "averaging",
                "agents_responded": len(results)
            }

        best_answer = max(avg_confidences, key=avg_confidences.get)
        best_confidence = avg_confidences[best_answer]

        return {
            "answer": best_answer,
            "confidence": best_confidence,
            "consensus_strength": len(answer_groups[best_answer]) / len(results),
            "consensus_method": "averaging",
            "agents_responded": len(results)
        }

    def _stigmergy_consensus(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Консенсус через stigmergy (феромоны)"""
        # Суммирование феромонов от всех агентов
        global_pheromones: Dict[str, float] = defaultdict(float)

        for agent in self.agents:
            for answer, strength in agent.beliefs.items():
                # Феромон пропорционален belief
                global_pheromones[answer] += strength

        if not global_pheromones:
            return {
                "answer": "No answer",
                "confidence": 0.0,
                "consensus_method": "stigmergy",
                "agents_responded": len(results)
            }

        # Strongest pheromone trail
        strongest = max(global_pheromones, key=global_pheromones.get)
        pheromone_strength = global_pheromones[strongest]

        # Normalize
        total_pheromone = sum(global_pheromones.values())
        normalized_strength = pheromone_strength / total_pheromone if total_pheromone > 0 else 0.0

        return {
            "answer": strongest,
            "confidence": min(1.0, pheromone_strength / len(self.agents)),
            "consensus_strength": normalized_strength,
            "consensus_method": "stigmergy",
            "pheromone_trails": dict(global_pheromones),
            "agents_responded": len(results)
        }

    def emergent_behavior(self) -> Dict[str, Any]:
        """
        Эмергентное поведение роя

        Паттерны, возникающие из взаимодействия агентов:
        - Самоорганизация в кластеры
        - Коллективное принятие решений
        - Адаптация к изменениям
        """
        # 1. Обнаружение кластеров агентов
        clusters = self.detect_clusters()

        # 2. Измерение connectivity
        connectivity = self.measure_connectivity()

        # 3. Diversity of beliefs
        belief_diversity = self.measure_belief_diversity()

        return {
            "clusters": clusters,
            "connectivity": connectivity,
            "belief_diversity": belief_diversity,
            "total_messages": sum(a.messages_sent for a in self.agents),
            "avg_searches": sum(a.searches_performed for a in self.agents) / len(self.agents)
        }

    def detect_clusters(self) -> List[List[int]]:
        """Обнаружение кластеров агентов"""
        # Простая кластеризация по позиции
        clusters = []
        visited = set()

        for agent in self.agents:
            if agent.id in visited:
                continue

            # Найти всех соседей в радиусе
            cluster = [agent.id]
            visited.add(agent.id)

            for other in self.agents:
                if other.id not in visited:
                    distance = agent.position.distance(other.position)
                    if distance < 20:  # Threshold
                        cluster.append(other.id)
                        visited.add(other.id)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    def measure_connectivity(self) -> float:
        """Измерить связность сети"""
        total_connections = sum(len(a.neighbors) for a in self.agents)
        max_connections = self.n_agents * (self.n_agents - 1)

        return total_connections / max_connections if max_connections > 0 else 0.0

    def measure_belief_diversity(self) -> float:
        """Измерить разнообразие beliefs"""
        unique_beliefs = set()

        for agent in self.agents:
            for belief in agent.beliefs:
                unique_beliefs.add(belief)

        return len(unique_beliefs) / max(1, len(self.agents))

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику роя"""
        return {
            "n_agents": self.n_agents,
            "neighborhood_size": self.neighborhood_size,
            "consensus_method": self.consensus_method.value,
            "total_queries": len(self.query_history),
            "total_messages_sent": sum(a.messages_sent for a in self.agents),
            "total_messages_received": sum(a.messages_received for a in self.agents),
            "avg_neighbors": sum(len(a.neighbors) for a in self.agents) / len(self.agents),
            "connectivity": self.measure_connectivity()
        }


def demo():
    """Демонстрация swarm intelligence"""
    print("=" * 80)
    print("COLLECTIVE INTELLIGENCE SWARM - DEMO")
    print("=" * 80)

    # === СОЗДАНИЕ РОЯ ===
    print("\n" + "=" * 80)
    print("CREATING SWARM")
    print("=" * 80)

    swarm = SwarmIntelligence(
        n_agents=30,
        neighborhood_size=5,
        consensus_method=ConsensusMethod.VOTING,
        verbose=True
    )

    # === РАСПРЕДЕЛЕНИЕ ЗНАНИЙ ===
    print("\n" + "=" * 80)
    print("DISTRIBUTING KNOWLEDGE")
    print("=" * 80)

    knowledge_base = {
        "5G": [
            "5G is the fifth generation of wireless technology",
            "5G provides high-speed connectivity up to 10 Gbps",
            "5G uses millimeter wave frequencies"
        ],
        "mmWave": [
            "mmWave operates at 30-300 GHz",
            "mmWave has poor penetration through walls",
            "mmWave provides very high bandwidth"
        ],
        "AI": [
            "AI stands for Artificial Intelligence",
            "AI can learn from data",
            "AI powers modern search engines"
        ],
        "Blockchain": [
            "Blockchain is a distributed ledger",
            "Blockchain provides high security",
            "Blockchain uses proof-of-work consensus"
        ]
    }

    swarm.distribute_knowledge(knowledge_base)

    # === SWARM QUERIES ===
    print("\n" + "=" * 80)
    print("SWARM QUERIES")
    print("=" * 80)

    queries = [
        "What is 5G?",
        "Tell me about mmWave",
        "What is AI?",
        "Explain Blockchain"
    ]

    for query in queries:
        result = swarm.query(query, iterations=3)

        print(f"\nQuery: {query}")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Consensus strength: {result['consensus_strength']:.2f}")
        print(f"Agents responded: {result['agents_responded']}")

    # === CONSENSUS METHODS COMPARISON ===
    print("\n" + "=" * 80)
    print("CONSENSUS METHODS COMPARISON")
    print("=" * 80)

    methods = [
        ConsensusMethod.VOTING,
        ConsensusMethod.AVERAGING,
        ConsensusMethod.STIGMERGY
    ]

    test_query = "What is 5G?"

    for method in methods:
        swarm.consensus_method = method
        result = swarm.query(test_query, iterations=3)

        print(f"\n{method.value.upper()}:")
        print(f"  Answer: {result['answer']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Consensus: {result['consensus_strength']:.2f}")

    # === EMERGENT BEHAVIOR ===
    print("\n" + "=" * 80)
    print("EMERGENT BEHAVIOR")
    print("=" * 80)

    emergent = swarm.emergent_behavior()

    print(f"\nClusters detected: {len(emergent['clusters'])}")
    for i, cluster in enumerate(emergent['clusters'], 1):
        print(f"  Cluster {i}: {len(cluster)} agents")

    print(f"\nConnectivity: {emergent['connectivity']:.2%}")
    print(f"Belief diversity: {emergent['belief_diversity']:.2f}")
    print(f"Total messages: {emergent['total_messages']}")
    print(f"Avg searches per agent: {emergent['avg_searches']:.1f}")

    # === STATISTICS ===
    print("\n" + "=" * 80)
    print("SWARM STATISTICS")
    print("=" * 80)

    stats = swarm.get_statistics()

    print(f"\nAgents: {stats['n_agents']}")
    print(f"Neighborhood size: {stats['neighborhood_size']}")
    print(f"Avg neighbors per agent: {stats['avg_neighbors']:.1f}")
    print(f"Total queries: {stats['total_queries']}")
    print(f"Messages sent: {stats['total_messages_sent']}")
    print(f"Messages received: {stats['total_messages_received']}")
    print(f"Network connectivity: {stats['connectivity']:.2%}")

    # === ADVANTAGES ===
    print("\n" + "=" * 80)
    print("SWARM INTELLIGENCE ADVANTAGES")
    print("=" * 80)

    print("""
Inspired by Nature:
  🐜 Ants: Stigmergy (indirect communication via pheromones)
  🐝 Bees: Waggle dance (location information sharing)
  🐦 Birds: Flocking (coordination without leader)
  🐟 Fish: Schooling (collective predator avoidance)

Key Advantages:
  ✓ Robustness: Failure of one agent is not critical
  ✓ Scalability: Easy to add more agents
  ✓ Emergence: Complex behavior from simple rules
  ✓ Decentralization: No single point of failure
  ✓ Collective Wisdom: Group is smarter than individual
  ✓ Self-Organization: Patterns arise spontaneously

Use Cases:
  - Distributed search across massive knowledge bases
  - Resilient systems that tolerate agent failures
  - Parallel processing of complex queries
  - Consensus building from diverse information sources
  - Adaptive systems that reorganize based on demand
    """)

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return swarm


if __name__ == "__main__":
    swarm = demo()
