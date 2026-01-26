#!/usr/bin/env python3
"""
Emergent Knowledge Synthesis
============================

Система синтеза нового знания через эмергентные процессы.

Ключевые концепции:
- Emergence: целое больше чем сумма частей
- Synthesis: создание нового знания из существующего
- Unexpected connections: неожиданные связи между концептами
- Pattern formation: спонтанное формирование паттернов
- Self-organization: самоорганизация знаний

Эмергентность означает, что новое знание возникает не через
прямое комбинирование, а через сложные взаимодействия,
которые порождают качественно новые свойства.
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
from collections import defaultdict


class EmergenceType(Enum):
    """Типы эмергентности"""
    WEAK = "weak"  # Слабая: предсказуема из компонентов
    STRONG = "strong"  # Сильная: непредсказуема, качественно новая


class SynthesisMethod(Enum):
    """Методы синтеза"""
    ANALOGICAL = "analogical"  # Аналогия между доменами
    COMPOSITIONAL = "compositional"  # Композиция концептов
    DIALECTICAL = "dialectical"  # Диалектический синтез (тезис-антитезис)
    CROSS_POLLINATION = "cross_pollination"  # Кросс-опыление идей
    SERENDIPITOUS = "serendipitous"  # Случайное открытие


@dataclass
class Concept:
    """Концепт в knowledge space"""
    id: str
    name: str
    domain: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relations: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    def similarity(self, other: 'Concept') -> float:
        """Семантическая схожесть"""
        if self.embedding and other.embedding:
            # Cosine similarity
            dot = sum(a * b for a, b in zip(self.embedding, other.embedding))
            mag1 = math.sqrt(sum(a * a for a in self.embedding))
            mag2 = math.sqrt(sum(b * b for b in other.embedding))
            if mag1 > 0 and mag2 > 0:
                return dot / (mag1 * mag2)

        # Fallback: property overlap
        shared_props = set(self.properties.keys()) & set(other.properties.keys())
        all_props = set(self.properties.keys()) | set(other.properties.keys())
        return len(shared_props) / len(all_props) if all_props else 0.0


@dataclass
class EmergentInsight:
    """Эмергентное знание"""
    id: str
    source_concepts: List[str]  # Исходные концепты
    synthesized_concept: str  # Новый концепт
    emergence_type: EmergenceType
    synthesis_method: SynthesisMethod
    novelty_score: float  # 0-1, насколько неожиданное
    confidence: float
    explanation: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "source_concepts": self.source_concepts,
            "synthesized_concept": self.synthesized_concept,
            "emergence_type": self.emergence_type.value,
            "synthesis_method": self.synthesis_method.value,
            "novelty_score": self.novelty_score,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "properties": self.properties,
            "created_at": self.created_at
        }


@dataclass
class InteractionPattern:
    """Паттерн взаимодействия между концептами"""
    pattern_type: str
    concepts: List[str]
    strength: float
    occurrences: int = 1


class KnowledgeSpace:
    """
    Пространство знаний для эмергентного синтеза

    Концепты организованы в многомерном пространстве,
    где близость = семантическая схожесть
    """

    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.interaction_patterns: List[InteractionPattern] = []
        self.emergent_insights: List[EmergentInsight] = []

    def add_concept(self, concept: Concept):
        """Добавить концепт"""
        self.concepts[concept.id] = concept

        # Автоматическое создание embedding если нет
        if concept.embedding is None:
            concept.embedding = self._generate_embedding(concept)

    def _generate_embedding(self, concept: Concept) -> List[float]:
        """Генерировать embedding для концепта"""
        # Простая эмуляция: хэш + случайность для стабильности
        random.seed(hash(concept.name + concept.domain))
        embedding = [random.gauss(0, 1) for _ in range(128)]

        # Нормализация
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def find_nearby_concepts(
        self,
        concept: Concept,
        max_distance: float = 0.5,
        max_results: int = 10
    ) -> List[Tuple[Concept, float]]:
        """Найти концепты поблизости в пространстве"""
        distances = []

        for other_id, other in self.concepts.items():
            if other_id != concept.id:
                similarity = concept.similarity(other)
                distance = 1.0 - similarity

                if distance <= max_distance:
                    distances.append((other, distance))

        distances.sort(key=lambda x: x[1])
        return distances[:max_results]

    def detect_interaction_patterns(self) -> List[InteractionPattern]:
        """Обнаружить паттерны взаимодействия"""
        patterns = []

        # Паттерн 1: Co-occurrence (концепты часто встречаются вместе)
        concept_pairs = defaultdict(int)
        for concept in self.concepts.values():
            for relation in concept.relations:
                if relation in self.concepts:
                    pair = tuple(sorted([concept.id, relation]))
                    concept_pairs[pair] += 1

        for (c1, c2), count in concept_pairs.items():
            if count > 1:
                patterns.append(InteractionPattern(
                    pattern_type="co_occurrence",
                    concepts=[c1, c2],
                    strength=min(1.0, count / 10.0),
                    occurrences=count
                ))

        # Паттерн 2: Similarity clusters (похожие концепты)
        for concept in list(self.concepts.values())[:20]:  # Limit для performance
            nearby = self.find_nearby_concepts(concept, max_distance=0.3, max_results=3)

            if len(nearby) >= 2:
                cluster = [concept.id] + [c.id for c, _ in nearby]
                patterns.append(InteractionPattern(
                    pattern_type="similarity_cluster",
                    concepts=cluster,
                    strength=sum(1.0 - d for _, d in nearby) / len(nearby),
                    occurrences=1
                ))

        self.interaction_patterns = patterns
        return patterns


class EmergentSynthesizer:
    """
    Синтезатор эмергентного знания

    Создает новое знание через:
    - Неожиданные комбинации концептов
    - Аналогии между доменами
    - Диалектический синтез
    - Случайные открытия (serendipity)
    """

    def __init__(self, knowledge_space: KnowledgeSpace, verbose: bool = False):
        self.knowledge_space = knowledge_space
        self.verbose = verbose
        self.synthesis_counter = 0

    def synthesize(
        self,
        method: Optional[SynthesisMethod] = None,
        num_insights: int = 3
    ) -> List[EmergentInsight]:
        """
        Синтезировать новые эмергентные знания

        Args:
            method: Метод синтеза (или случайный)
            num_insights: Количество insights для генерации

        Returns:
            Список эмергентных insights
        """
        if self.verbose:
            print(f"\n=== Emergent Synthesis ===")
            print(f"Method: {method.value if method else 'auto'}")
            print(f"Target insights: {num_insights}")

        insights = []

        for _ in range(num_insights):
            # Выбрать метод
            if method is None:
                method_choice = random.choice(list(SynthesisMethod))
            else:
                method_choice = method

            # Синтез
            if method_choice == SynthesisMethod.ANALOGICAL:
                insight = self._analogical_synthesis()
            elif method_choice == SynthesisMethod.COMPOSITIONAL:
                insight = self._compositional_synthesis()
            elif method_choice == SynthesisMethod.DIALECTICAL:
                insight = self._dialectical_synthesis()
            elif method_choice == SynthesisMethod.CROSS_POLLINATION:
                insight = self._cross_pollination()
            elif method_choice == SynthesisMethod.SERENDIPITOUS:
                insight = self._serendipitous_discovery()
            else:
                insight = self._compositional_synthesis()

            if insight:
                insights.append(insight)
                self.knowledge_space.emergent_insights.append(insight)

                if self.verbose:
                    print(f"\n✨ Emergent Insight #{len(insights)}:")
                    print(f"   {insight.synthesized_concept}")
                    print(f"   Method: {insight.synthesis_method.value}")
                    print(f"   Novelty: {insight.novelty_score:.2f}")
                    print(f"   Confidence: {insight.confidence:.2f}")

        return insights

    def _analogical_synthesis(self) -> Optional[EmergentInsight]:
        """
        Аналогический синтез

        Находит аналогию между концептами из разных доменов
        Пример: "Атом подобен солнечной системе"
        """
        concepts = list(self.knowledge_space.concepts.values())

        if len(concepts) < 2:
            return None

        # Выбрать два концепта из РАЗНЫХ доменов
        domains = set(c.domain for c in concepts)
        if len(domains) < 2:
            return None

        domain1, domain2 = random.sample(list(domains), 2)

        concepts_d1 = [c for c in concepts if c.domain == domain1]
        concepts_d2 = [c for c in concepts if c.domain == domain2]

        if not concepts_d1 or not concepts_d2:
            return None

        concept1 = random.choice(concepts_d1)
        concept2 = random.choice(concepts_d2)

        # Найти общие свойства
        common_props = set(concept1.properties.keys()) & set(concept2.properties.keys())

        # Генерировать аналогию
        self.synthesis_counter += 1
        synthesized = f"{concept1.name}_is_like_{concept2.name}"

        novelty_score = 0.7 + random.random() * 0.2  # 0.7-0.9
        confidence = len(common_props) / max(len(concept1.properties), len(concept2.properties), 1) * 0.8

        explanation = f"Аналогия: {concept1.name} ({domain1}) подобен {concept2.name} ({domain2})"
        if common_props:
            explanation += f" - общие свойства: {', '.join(list(common_props)[:3])}"

        return EmergentInsight(
            id=f"insight_{self.synthesis_counter}",
            source_concepts=[concept1.id, concept2.id],
            synthesized_concept=synthesized,
            emergence_type=EmergenceType.STRONG,
            synthesis_method=SynthesisMethod.ANALOGICAL,
            novelty_score=novelty_score,
            confidence=confidence,
            explanation=explanation,
            properties={
                "analogy_between": [domain1, domain2],
                "common_properties": list(common_props)
            }
        )

    def _compositional_synthesis(self) -> Optional[EmergentInsight]:
        """
        Композиционный синтез

        Комбинирует свойства двух концептов в новый концепт
        Пример: "Умный дом" = "Дом" + "AI"
        """
        concepts = list(self.knowledge_space.concepts.values())

        if len(concepts) < 2:
            return None

        # Выбрать два концепта
        concept1, concept2 = random.sample(concepts, 2)

        # Композиция
        self.synthesis_counter += 1
        synthesized = f"{concept1.name}_{concept2.name}"

        # Объединение свойств
        combined_props = {**concept1.properties, **concept2.properties}

        novelty_score = 0.5 + random.random() * 0.3  # 0.5-0.8
        confidence = 0.7 + random.random() * 0.2

        explanation = f"Композиция: {concept1.name} + {concept2.name} = {synthesized}"
        explanation += f" (объединение {len(combined_props)} свойств)"

        return EmergentInsight(
            id=f"insight_{self.synthesis_counter}",
            source_concepts=[concept1.id, concept2.id],
            synthesized_concept=synthesized,
            emergence_type=EmergenceType.WEAK,
            synthesis_method=SynthesisMethod.COMPOSITIONAL,
            novelty_score=novelty_score,
            confidence=confidence,
            explanation=explanation,
            properties=combined_props
        )

    def _dialectical_synthesis(self) -> Optional[EmergentInsight]:
        """
        Диалектический синтез (Гегель: тезис-антитезис-синтез)

        Находит противоположности и создает синтез
        Пример: "Централизация" vs "Децентрализация" = "Федерализм"
        """
        concepts = list(self.knowledge_space.concepts.values())

        if len(concepts) < 2:
            return None

        # Найти концепты с противоположными свойствами
        for _ in range(10):  # Попытки найти противоположности
            concept1, concept2 = random.sample(concepts, 2)

            # Проверить на противоположность
            opposite_count = 0
            for key in concept1.properties:
                if key in concept2.properties:
                    val1 = concept1.properties[key]
                    val2 = concept2.properties[key]

                    # Если значения противоположны
                    if isinstance(val1, str) and isinstance(val2, str):
                        opposites = [
                            ("high", "low"), ("fast", "slow"),
                            ("big", "small"), ("good", "bad"),
                            ("centralized", "decentralized")
                        ]
                        for opp1, opp2 in opposites:
                            if (opp1 in val1.lower() and opp2 in val2.lower()) or \
                               (opp2 in val1.lower() and opp1 in val2.lower()):
                                opposite_count += 1

            if opposite_count > 0:
                break

        # Диалектический синтез
        self.synthesis_counter += 1
        synthesized = f"synthesis_of_{concept1.name}_and_{concept2.name}"

        novelty_score = 0.8 + random.random() * 0.2  # 0.8-1.0 (высокая)
        confidence = 0.6 + random.random() * 0.2

        explanation = f"Диалектика: {concept1.name} (тезис) + {concept2.name} (антитезис) → {synthesized} (синтез)"

        return EmergentInsight(
            id=f"insight_{self.synthesis_counter}",
            source_concepts=[concept1.id, concept2.id],
            synthesized_concept=synthesized,
            emergence_type=EmergenceType.STRONG,
            synthesis_method=SynthesisMethod.DIALECTICAL,
            novelty_score=novelty_score,
            confidence=confidence,
            explanation=explanation,
            properties={"dialectical_synthesis": True}
        )

    def _cross_pollination(self) -> Optional[EmergentInsight]:
        """
        Кросс-опыление идей между доменами

        Переносит концепт из одного домена в другой
        Пример: "Swarm intelligence" из биологии в компьютерные науки
        """
        concepts = list(self.knowledge_space.concepts.values())
        domains = set(c.domain for c in concepts)

        if len(domains) < 2:
            return None

        # Выбрать источник и цель
        source_domain, target_domain = random.sample(list(domains), 2)

        source_concepts = [c for c in concepts if c.domain == source_domain]
        if not source_concepts:
            return None

        source_concept = random.choice(source_concepts)

        # Перенос в новый домен
        self.synthesis_counter += 1
        synthesized = f"{source_concept.name}_in_{target_domain}"

        novelty_score = 0.7 + random.random() * 0.25  # 0.7-0.95
        confidence = 0.65 + random.random() * 0.25

        explanation = f"Кросс-опыление: {source_concept.name} из {source_domain} → {target_domain}"

        return EmergentInsight(
            id=f"insight_{self.synthesis_counter}",
            source_concepts=[source_concept.id],
            synthesized_concept=synthesized,
            emergence_type=EmergenceType.STRONG,
            synthesis_method=SynthesisMethod.CROSS_POLLINATION,
            novelty_score=novelty_score,
            confidence=confidence,
            explanation=explanation,
            properties={
                "source_domain": source_domain,
                "target_domain": target_domain
            }
        )

    def _serendipitous_discovery(self) -> Optional[EmergentInsight]:
        """
        Случайное открытие (serendipity)

        Неожиданные открытия через случайные комбинации
        Пример: Пенициллин был открыт случайно
        """
        concepts = list(self.knowledge_space.concepts.values())

        if len(concepts) < 3:
            return None

        # Выбрать 2-4 случайных концепта
        num_concepts = random.randint(2, min(4, len(concepts)))
        selected_concepts = random.sample(concepts, num_concepts)

        # Случайная комбинация
        self.synthesis_counter += 1
        synthesized = "serendipitous_" + "_".join(c.name for c in selected_concepts)

        novelty_score = 0.85 + random.random() * 0.15  # 0.85-1.0 (очень высокая)
        confidence = 0.4 + random.random() * 0.3  # 0.4-0.7 (низкая уверенность)

        explanation = f"Случайное открытие: неожиданная комбинация {len(selected_concepts)} концептов"

        return EmergentInsight(
            id=f"insight_{self.synthesis_counter}",
            source_concepts=[c.id for c in selected_concepts],
            synthesized_concept=synthesized,
            emergence_type=EmergenceType.STRONG,
            synthesis_method=SynthesisMethod.SERENDIPITOUS,
            novelty_score=novelty_score,
            confidence=confidence,
            explanation=explanation,
            properties={"serendipitous": True, "concept_count": num_concepts}
        )


class EmergentKnowledgeSystem:
    """
    Полная система эмергентного синтеза знаний

    Объединяет knowledge space и synthesizer
    """

    def __init__(self, verbose: bool = False):
        self.knowledge_space = KnowledgeSpace()
        self.synthesizer = EmergentSynthesizer(self.knowledge_space, verbose=verbose)
        self.verbose = verbose

    def add_concept(self, concept: Concept):
        """Добавить концепт"""
        self.knowledge_space.add_concept(concept)

    def run_emergence_cycle(self, iterations: int = 3) -> List[EmergentInsight]:
        """
        Запустить цикл эмергенции

        1. Обнаружение паттернов взаимодействия
        2. Синтез новых insights
        3. Самоорганизация knowledge space
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"EMERGENCE CYCLE: {iterations} iterations")
            print(f"{'='*80}")

        all_insights = []

        for iteration in range(iterations):
            if self.verbose:
                print(f"\n--- Iteration {iteration + 1} ---")

            # 1. Обнаружение паттернов
            patterns = self.knowledge_space.detect_interaction_patterns()

            if self.verbose:
                print(f"Patterns detected: {len(patterns)}")

            # 2. Синтез
            insights = self.synthesizer.synthesize(method=None, num_insights=2)
            all_insights.extend(insights)

            # 3. Добавление insights обратно в knowledge space (самоорганизация)
            for insight in insights:
                # Превратить insight в концепт
                new_concept = Concept(
                    id=insight.id,
                    name=insight.synthesized_concept,
                    domain="emergent",
                    properties=insight.properties,
                    relations=insight.source_concepts
                )
                self.knowledge_space.add_concept(new_concept)

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"TOTAL EMERGENT INSIGHTS: {len(all_insights)}")
            print(f"{'='*80}")

        return all_insights

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        insights = self.knowledge_space.emergent_insights

        # Группировка по методам
        by_method = defaultdict(int)
        for insight in insights:
            by_method[insight.synthesis_method.value] += 1

        # Средняя novelty
        avg_novelty = sum(i.novelty_score for i in insights) / len(insights) if insights else 0.0

        # Средняя confidence
        avg_confidence = sum(i.confidence for i in insights) / len(insights) if insights else 0.0

        return {
            "total_concepts": len(self.knowledge_space.concepts),
            "total_insights": len(insights),
            "insights_by_method": dict(by_method),
            "avg_novelty_score": avg_novelty,
            "avg_confidence": avg_confidence,
            "interaction_patterns": len(self.knowledge_space.interaction_patterns)
        }


def demo():
    """Демонстрация emergent knowledge synthesis"""
    print("=" * 80)
    print("EMERGENT KNOWLEDGE SYNTHESIS - DEMO")
    print("=" * 80)

    system = EmergentKnowledgeSystem(verbose=True)

    # === ДОБАВЛЕНИЕ КОНЦЕПТОВ ===
    print("\n" + "=" * 80)
    print("ADDING CONCEPTS TO KNOWLEDGE SPACE")
    print("=" * 80)

    concepts = [
        # Technology domain
        Concept("c1", "AI", "technology", {
            "intelligence": "artificial",
            "learning": "machine",
            "speed": "fast"
        }, relations=["c2"]),

        Concept("c2", "Neural_Network", "technology", {
            "structure": "layered",
            "learning": "supervised",
            "complexity": "high"
        }, relations=["c1"]),

        # Biology domain
        Concept("c3", "Brain", "biology", {
            "structure": "layered",
            "intelligence": "natural",
            "complexity": "high"
        }, relations=["c4"]),

        Concept("c4", "Neuron", "biology", {
            "type": "cell",
            "function": "signal_transmission",
            "network": "connected"
        }, relations=["c3"]),

        # Physics domain
        Concept("c5", "Quantum", "physics", {
            "state": "superposition",
            "speed": "fast",
            "behavior": "probabilistic"
        }),

        # Social domain
        Concept("c6", "Swarm", "biology", {
            "organization": "decentralized",
            "intelligence": "collective",
            "behavior": "emergent"
        }),

        # Economics
        Concept("c7", "Market", "economics", {
            "organization": "decentralized",
            "behavior": "emergent",
            "complexity": "high"
        }),

        # Philosophy
        Concept("c8", "Consciousness", "philosophy", {
            "property": "emergent",
            "complexity": "high",
            "mystery": "deep"
        })
    ]

    for concept in concepts:
        system.add_concept(concept)
        print(f"Added: {concept.name} ({concept.domain})")

    # === EMERGENCE CYCLES ===
    print("\n" + "=" * 80)
    print("RUNNING EMERGENCE CYCLES")
    print("=" * 80)

    insights = system.run_emergence_cycle(iterations=3)

    # === ANALYSIS OF INSIGHTS ===
    print("\n" + "=" * 80)
    print("EMERGENT INSIGHTS ANALYSIS")
    print("=" * 80)

    print(f"\nTotal insights generated: {len(insights)}")

    # По типу эмергенции
    weak = [i for i in insights if i.emergence_type == EmergenceType.WEAK]
    strong = [i for i in insights if i.emergence_type == EmergenceType.STRONG]

    print(f"\nEmergence types:")
    print(f"  Weak emergence (predictable): {len(weak)}")
    print(f"  Strong emergence (novel): {len(strong)}")

    # По методу синтеза
    print(f"\nSynthesis methods used:")
    method_counts = defaultdict(int)
    for insight in insights:
        method_counts[insight.synthesis_method.value] += 1

    for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count}")

    # Топ insights по novelty
    print(f"\nTop 3 insights by novelty:")
    top_novel = sorted(insights, key=lambda x: x.novelty_score, reverse=True)[:3]
    for i, insight in enumerate(top_novel, 1):
        print(f"\n{i}. {insight.synthesized_concept}")
        print(f"   Novelty: {insight.novelty_score:.2f}")
        print(f"   Confidence: {insight.confidence:.2f}")
        print(f"   Method: {insight.synthesis_method.value}")
        print(f"   {insight.explanation}")

    # === STATISTICS ===
    print("\n" + "=" * 80)
    print("SYSTEM STATISTICS")
    print("=" * 80)

    stats = system.get_statistics()
    print(f"\nTotal concepts: {stats['total_concepts']}")
    print(f"Total emergent insights: {stats['total_insights']}")
    print(f"Avg novelty score: {stats['avg_novelty_score']:.2f}")
    print(f"Avg confidence: {stats['avg_confidence']:.2f}")
    print(f"Interaction patterns: {stats['interaction_patterns']}")

    # === PHILOSOPHICAL REFLECTION ===
    print("\n" + "=" * 80)
    print("PHILOSOPHICAL REFLECTION")
    print("=" * 80)

    print("""
Emergent Knowledge Synthesis demonstrates:

1. EMERGENCE
   - New knowledge arises from interaction of existing knowledge
   - "The whole is greater than the sum of its parts"
   - Qualitatively new properties emerge

2. SYNTHESIS METHODS
   - Analogical: Finding similarities across domains
   - Compositional: Combining properties
   - Dialectical: Thesis + Antithesis → Synthesis
   - Cross-Pollination: Ideas from one domain to another
   - Serendipitous: Unexpected discoveries

3. SELF-ORGANIZATION
   - Knowledge space reorganizes itself
   - Patterns form spontaneously
   - New concepts become part of the space

4. NOVELTY
   - Strong emergence: Unpredictable, truly novel
   - Weak emergence: Predictable from components

This is how scientific breakthroughs happen:
- Newton: Apple falling → Universal gravitation
- Einstein: Relativity from thought experiments
- Watson & Crick: DNA from X-ray patterns

Emergent synthesis is the essence of creativity and innovation.
    """)

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return system


if __name__ == "__main__":
    system = demo()
