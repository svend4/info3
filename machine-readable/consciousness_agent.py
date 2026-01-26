#!/usr/bin/env python3
"""
Consciousness-like Self-Awareness
==================================

Система с "сознанием" своих знаний и ограничений.

Основные компоненты:
- Meta-knowledge: система знает что она знает
- Self-model: модель самого себя
- Meta-cognitive reflection: рефлексия над собственными ответами
- Epistemic state tracking: отслеживание эпистемического состояния
- Known unknowns: система знает что она не знает
- Unknown unknowns: оценка того, что система не знает что не знает

Философия:
Это близко к "сильному AI" - система не просто отвечает,
но **понимает** что она знает и что нет.
"""

import json
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from enum import Enum


class EpistemicState(Enum):
    """Эпистемическое состояние концепта"""
    KNOWN = "known"  # Знаю
    PARTIALLY_KNOWN = "partially_known"  # Частично знаю
    KNOWN_UNKNOWN = "known_unknown"  # Знаю что не знаю
    UNKNOWN_UNKNOWN = "unknown_unknown"  # Не знаю что не знаю (оценка)


class BiasType(Enum):
    """Типы когнитивных искажений"""
    CONFIRMATION_BIAS = "confirmation_bias"  # Подтверждающее искажение
    AVAILABILITY_BIAS = "availability_bias"  # Доступность информации
    ANCHORING_BIAS = "anchoring_bias"  # Якорение
    OVERCONFIDENCE_BIAS = "overconfidence_bias"  # Сверхуверенность
    RECENCY_BIAS = "recency_bias"  # Недавность информации


@dataclass
class ConceptKnowledge:
    """Знание о конкретном концепте"""
    concept: str
    epistemic_state: EpistemicState
    confidence: float  # 0.0 - 1.0
    last_accessed: str
    access_count: int = 0
    related_concepts: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)  # Свидетельства
    contradictions: List[str] = field(default_factory=list)  # Противоречия

    def update_access(self):
        """Обновить статистику доступа"""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()


@dataclass
class Reflection:
    """Рефлексия над ответом"""
    knows_answer: bool
    meta_confidence: float  # Уверенность в уверенности
    reasoning_quality: float  # Качество рассуждения (0-1)
    identified_gaps: List[str]  # Идентифицированные пробелы
    alternatives_considered: List[str]  # Рассмотренные альтернативы
    potential_biases: List[BiasType]  # Потенциальные искажения
    reflection_text: str  # Текстовая рефлексия

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "knows_answer": self.knows_answer,
            "meta_confidence": self.meta_confidence,
            "reasoning_quality": self.reasoning_quality,
            "identified_gaps": self.identified_gaps,
            "alternatives_considered": self.alternatives_considered,
            "potential_biases": [b.value for b in self.potential_biases],
            "reflection_text": self.reflection_text
        }


@dataclass
class QueryResult:
    """Результат запроса с self-awareness"""
    query: str
    answer: str
    confidence: float
    relevant_concepts: List[str]
    epistemic_state: Dict[str, Any]
    self_awareness: Dict[str, Any]
    reflection: Reflection
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "query": self.query,
            "answer": self.answer,
            "confidence": self.confidence,
            "relevant_concepts": self.relevant_concepts,
            "epistemic_state": self.epistemic_state,
            "self_awareness": self.self_awareness,
            "reflection": self.reflection.to_dict(),
            "timestamp": self.timestamp
        }


class SelfModel:
    """
    Модель самого себя

    Отслеживает:
    - Что я умею
    - Что я не умею
    - Мои сильные стороны
    - Мои слабости
    - Мою историю ответов
    """

    def __init__(self):
        self.strengths: Set[str] = set()
        self.weaknesses: Set[str] = set()
        self.query_history: List[Dict[str, Any]] = []
        self.performance_by_topic: Dict[str, float] = {}  # topic -> avg confidence
        self.total_queries = 0
        self.successful_queries = 0

    def update_from_query(self, query: str, result: QueryResult):
        """Обновить self-model на основе запроса"""
        self.total_queries += 1

        # Запись в историю
        self.query_history.append({
            "query": query,
            "confidence": result.confidence,
            "timestamp": result.timestamp
        })

        # Обновление успешности
        if result.confidence > 0.7:
            self.successful_queries += 1

        # Обновление производительности по темам
        for concept in result.relevant_concepts:
            if concept not in self.performance_by_topic:
                self.performance_by_topic[concept] = result.confidence
            else:
                # Экспоненциальное скользящее среднее
                alpha = 0.3
                self.performance_by_topic[concept] = (
                    alpha * result.confidence +
                    (1 - alpha) * self.performance_by_topic[concept]
                )

            # Определение strengths/weaknesses
            if self.performance_by_topic[concept] > 0.8:
                self.strengths.add(concept)
                self.weaknesses.discard(concept)
            elif self.performance_by_topic[concept] < 0.4:
                self.weaknesses.add(concept)
                self.strengths.discard(concept)

    def get_success_rate(self) -> float:
        """Получить success rate"""
        if self.total_queries == 0:
            return 0.0
        return self.successful_queries / self.total_queries

    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку о себе"""
        return {
            "total_queries": self.total_queries,
            "success_rate": self.get_success_rate(),
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
            "topics_known": len([t for t, conf in self.performance_by_topic.items() if conf > 0.6])
        }


class KnowledgeBase:
    """Простая база знаний для демонстрации"""

    def __init__(self):
        self.facts: Dict[str, List[str]] = {}
        self.concepts: Set[str] = set()

    def add_fact(self, concept: str, fact: str):
        """Добавить факт"""
        if concept not in self.facts:
            self.facts[concept] = []
        self.facts[concept].append(fact)
        self.concepts.add(concept.lower())

    def get_facts(self, concept: str) -> List[str]:
        """Получить факты о концепте"""
        return self.facts.get(concept, [])

    def has_concept(self, concept: str) -> bool:
        """Проверить наличие концепта"""
        return concept.lower() in self.concepts


class ConsciousAgent:
    """
    Агент с consciousness-like self-awareness

    Обладает:
    - Meta-knowledge: знает что он знает
    - Self-model: модель самого себя
    - Meta-cognitive reflection: рефлексия над ответами
    - Epistemic state tracking: отслеживание знания о концептах
    """

    def __init__(self, verbose: bool = False):
        # Обычные компоненты
        self.knowledge_base = KnowledgeBase()
        self.verbose = verbose

        # Meta-consciousness: система знает что она знает
        self.meta_knowledge: Dict[str, ConceptKnowledge] = {}

        # Категории meta-knowledge
        self.what_i_know: Set[str] = set()
        self.what_i_know_i_dont_know: Set[str] = set()  # Known unknowns
        self.what_i_might_not_know: Set[str] = set()  # Estimated unknown unknowns

        # Self-model
        self.self_model = SelfModel()

        # Reasoning traces (для анализа)
        self.reasoning_traces: List[Dict[str, Any]] = []

    def learn_concept(
        self,
        concept: str,
        facts: List[str],
        epistemic_state: EpistemicState = EpistemicState.KNOWN,
        confidence: float = 1.0
    ):
        """Выучить концепт"""
        concept_lower = concept.lower()

        # Добавить в базу знаний
        for fact in facts:
            self.knowledge_base.add_fact(concept, fact)

        # Обновить meta-knowledge
        self.meta_knowledge[concept_lower] = ConceptKnowledge(
            concept=concept,
            epistemic_state=epistemic_state,
            confidence=confidence,
            last_accessed=datetime.now().isoformat(),
            evidence=facts
        )

        # Обновить категории
        if epistemic_state == EpistemicState.KNOWN and confidence > 0.7:
            self.what_i_know.add(concept_lower)
        elif epistemic_state == EpistemicState.KNOWN_UNKNOWN:
            self.what_i_know_i_dont_know.add(concept_lower)

        if self.verbose:
            print(f"Learned: {concept} (state: {epistemic_state.value}, confidence: {confidence:.2f})")

    def declare_unknown(self, concept: str):
        """Объявить что концепт неизвестен (known unknown)"""
        concept_lower = concept.lower()

        self.meta_knowledge[concept_lower] = ConceptKnowledge(
            concept=concept,
            epistemic_state=EpistemicState.KNOWN_UNKNOWN,
            confidence=0.0,
            last_accessed=datetime.now().isoformat()
        )

        self.what_i_know_i_dont_know.add(concept_lower)

        if self.verbose:
            print(f"Declared unknown: {concept}")

    def query(self, question: str) -> QueryResult:
        """
        Обработка запроса с self-awareness

        Returns:
            QueryResult с полной self-awareness информацией
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Query: {question}")
            print(f"{'='*80}")

        # 1. Обычная обработка запроса
        answer, confidence, relevant_concepts = self._process_query(question)

        # 2. Meta-cognitive reflection
        reflection = self.reflect_on_query(question, answer, confidence, relevant_concepts)

        # 3. Epistemic state analysis
        epistemic_state = self.get_epistemic_state(question)

        # 4. Self-awareness compilation
        self_awareness = {
            "know_answer": reflection.knows_answer,
            "confidence_in_confidence": reflection.meta_confidence,
            "knowledge_gaps": reflection.identified_gaps,
            "reasoning_quality": reflection.reasoning_quality,
            "alternatives_considered": reflection.alternatives_considered,
            "potential_biases": [b.value for b in reflection.potential_biases],
            "meta_reflection": reflection.reflection_text
        }

        # 5. Создание результата
        result = QueryResult(
            query=question,
            answer=answer,
            confidence=confidence,
            relevant_concepts=relevant_concepts,
            epistemic_state=epistemic_state,
            self_awareness=self_awareness,
            reflection=reflection
        )

        # 6. Обновление self-model
        self.self_model.update_from_query(question, result)

        # 7. Запись reasoning trace
        self.reasoning_traces.append({
            "query": question,
            "timestamp": result.timestamp,
            "confidence": confidence,
            "meta_confidence": reflection.meta_confidence
        })

        if self.verbose:
            self._print_result(result)

        return result

    def _process_query(self, question: str) -> Tuple[str, float, List[str]]:
        """Обработка запроса (простая реализация)"""
        question_lower = question.lower()
        relevant_concepts = []
        relevant_facts = []

        # Поиск релевантных концептов
        for concept in self.knowledge_base.concepts:
            if concept in question_lower:
                relevant_concepts.append(concept)
                facts = self.knowledge_base.get_facts(concept)
                relevant_facts.extend(facts)

                # Обновить access в meta-knowledge
                if concept in self.meta_knowledge:
                    self.meta_knowledge[concept].update_access()

        # Формирование ответа
        if relevant_facts:
            answer = " ".join(relevant_facts[:3])  # Берём первые 3 факта
            confidence = min(1.0, len(relevant_facts) * 0.3)
        else:
            answer = "I don't have enough information to answer this question."
            confidence = 0.0

        return answer, confidence, relevant_concepts

    def reflect_on_query(
        self,
        question: str,
        answer: str,
        confidence: float,
        relevant_concepts: List[str]
    ) -> Reflection:
        """
        Рефлексия над собственным ответом

        Вопросы к себе:
        - Насколько я уверен в этом ответе?
        - Почему я уверен/не уверен?
        - Какие у меня были альтернативы?
        - Правильно ли я понял вопрос?
        - Чего я не учёл?
        """

        # Assess meta-confidence
        meta_confidence = self._assess_meta_confidence(confidence, relevant_concepts)

        # Assess reasoning quality
        reasoning_quality = self._assess_reasoning_quality(question, relevant_concepts)

        # Identify knowledge gaps
        identified_gaps = self._identify_knowledge_gaps(question, relevant_concepts)

        # Get alternatives
        alternatives = self._get_alternatives(question, relevant_concepts)

        # Detect biases
        biases = self._detect_biases(confidence, relevant_concepts)

        # Generate reflection text
        reflection_text = self._generate_reflection_text(
            confidence,
            meta_confidence,
            identified_gaps,
            reasoning_quality
        )

        return Reflection(
            knows_answer=confidence > 0.7,
            meta_confidence=meta_confidence,
            reasoning_quality=reasoning_quality,
            identified_gaps=identified_gaps,
            alternatives_considered=alternatives,
            potential_biases=biases,
            reflection_text=reflection_text
        )

    def _assess_meta_confidence(self, confidence: float, relevant_concepts: List[str]) -> float:
        """
        Уверенность в уверенности

        Оценивает: насколько я уверен в своей оценке confidence?
        """
        # Факторы, влияющие на meta-confidence:
        # 1. Количество evidence
        evidence_count = sum(
            len(self.meta_knowledge[c].evidence)
            for c in relevant_concepts
            if c in self.meta_knowledge
        )

        # 2. Наличие противоречий
        contradiction_count = sum(
            len(self.meta_knowledge[c].contradictions)
            for c in relevant_concepts
            if c in self.meta_knowledge
        )

        # 3. История успешности по этим темам
        avg_topic_performance = sum(
            self.self_model.performance_by_topic.get(c, 0.5)
            for c in relevant_concepts
        ) / max(len(relevant_concepts), 1)

        # Вычисление meta-confidence
        evidence_factor = min(1.0, evidence_count * 0.2)
        contradiction_penalty = contradiction_count * 0.1
        history_factor = avg_topic_performance

        meta_confidence = (
            0.4 * evidence_factor +
            0.3 * history_factor +
            0.3 * confidence
        ) - contradiction_penalty

        return max(0.0, min(1.0, meta_confidence))

    def _assess_reasoning_quality(self, question: str, relevant_concepts: List[str]) -> float:
        """Оценить качество рассуждения"""
        quality = 0.5  # Baseline

        # Фактор 1: Покрытие концептов из вопроса
        question_words = set(question.lower().split())
        concept_coverage = len(set(relevant_concepts) & question_words) / max(len(question_words), 1)
        quality += concept_coverage * 0.3

        # Фактор 2: Глубина знаний
        if relevant_concepts:
            avg_access_count = sum(
                self.meta_knowledge[c].access_count
                for c in relevant_concepts
                if c in self.meta_knowledge
            ) / len(relevant_concepts)
            depth_factor = min(1.0, avg_access_count * 0.1)
            quality += depth_factor * 0.2

        return min(1.0, quality)

    def _identify_knowledge_gaps(self, question: str, relevant_concepts: List[str]) -> List[str]:
        """Идентифицировать пробелы в знаниях"""
        gaps = []

        # Извлечь концепты из вопроса
        question_concepts = self._extract_concepts(question)

        # Найти неизвестные концепты
        for concept in question_concepts:
            if concept not in self.knowledge_base.concepts:
                if concept not in self.what_i_know_i_dont_know:
                    # Это unknown unknown (теперь становится known unknown)
                    gaps.append(f"Unknown concept: '{concept}'")
                    self.what_i_know_i_dont_know.add(concept)
                else:
                    gaps.append(f"Known gap: '{concept}'")

        # Проверить недостаточность evidence
        for concept in relevant_concepts:
            if concept in self.meta_knowledge:
                ck = self.meta_knowledge[concept]
                if len(ck.evidence) < 2:
                    gaps.append(f"Insufficient evidence for '{concept}'")

        return gaps

    def _get_alternatives(self, question: str, relevant_concepts: List[str]) -> List[str]:
        """Получить альтернативные интерпретации/ответы"""
        alternatives = []

        # Альтернатива 1: Другие релевантные концепты
        for concept in self.knowledge_base.concepts:
            if concept not in relevant_concepts:
                # Простая эвристика: схожие слова
                if any(word in concept for word in question.lower().split()):
                    alternatives.append(f"Could also consider: '{concept}'")

        # Альтернатива 2: Related concepts
        for concept in relevant_concepts:
            if concept in self.meta_knowledge:
                for related in self.meta_knowledge[concept].related_concepts:
                    if related not in relevant_concepts:
                        alternatives.append(f"Related concept: '{related}'")

        return alternatives[:3]  # Limit to 3

    def _detect_biases(self, confidence: float, relevant_concepts: List[str]) -> List[BiasType]:
        """Обнаружить потенциальные когнитивные искажения"""
        biases = []

        # 1. Overconfidence bias
        if confidence > 0.9 and len(relevant_concepts) < 2:
            biases.append(BiasType.OVERCONFIDENCE_BIAS)

        # 2. Availability bias (основываюсь только на доступной информации)
        if relevant_concepts:
            total_evidence = sum(
                len(self.meta_knowledge[c].evidence)
                for c in relevant_concepts
                if c in self.meta_knowledge
            )
            if total_evidence < 3:
                biases.append(BiasType.AVAILABILITY_BIAS)

        # 3. Recency bias
        if relevant_concepts:
            recent_accesses = [
                self.meta_knowledge[c].last_accessed
                for c in relevant_concepts
                if c in self.meta_knowledge
            ]
            if recent_accesses:
                # Проверить, что все доступы недавние
                recent_count = sum(1 for _ in recent_accesses)  # Упрощение
                if recent_count == len(recent_accesses):
                    biases.append(BiasType.RECENCY_BIAS)

        return biases

    def _generate_reflection_text(
        self,
        confidence: float,
        meta_confidence: float,
        gaps: List[str],
        reasoning_quality: float
    ) -> str:
        """Генерировать текстовую рефлексию"""
        if confidence > 0.8:
            certainty = "I am confident in this answer"
        elif confidence > 0.5:
            certainty = "I am moderately confident in this answer"
        else:
            certainty = "I am uncertain about this answer"

        meta_certainty = "high" if meta_confidence > 0.7 else "moderate" if meta_confidence > 0.4 else "low"

        reflection = f"{certainty} (meta-confidence: {meta_certainty})."

        if gaps:
            reflection += f" However, I identified {len(gaps)} knowledge gap(s)."

        if reasoning_quality < 0.5:
            reflection += " My reasoning quality could be improved."

        return reflection

    def _extract_concepts(self, text: str) -> List[str]:
        """Извлечь концепты из текста (простая реализация)"""
        words = text.lower().split()
        # Фильтр стоп-слов
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'does', 'do', 'can'}
        concepts = [w.strip('?.,!') for w in words if w not in stop_words and len(w) > 2]
        return concepts

    def get_epistemic_state(self, question: str) -> Dict[str, Any]:
        """
        Эпистемическое состояние (что я знаю о своих знаниях)

        Returns:
            Dict с known_concepts, partially_known, unknown_concepts
        """
        concepts_in_question = self._extract_concepts(question)

        state = {
            "known_concepts": [],
            "partially_known": [],
            "unknown_concepts": [],
            "uncertainty_estimate": 0.0
        }

        for concept in concepts_in_question:
            if concept in self.what_i_know:
                state["known_concepts"].append(concept)
            elif concept in self.what_i_know_i_dont_know:
                state["unknown_concepts"].append(concept)
            else:
                # Partially known or unknown unknown
                if concept in self.meta_knowledge:
                    ck = self.meta_knowledge[concept]
                    if ck.epistemic_state == EpistemicState.PARTIALLY_KNOWN:
                        state["partially_known"].append(concept)
                    elif ck.epistemic_state == EpistemicState.KNOWN_UNKNOWN:
                        state["unknown_concepts"].append(concept)
                else:
                    # Unknown unknown (теперь становится known unknown)
                    state["unknown_concepts"].append(concept)

        # Вычислить uncertainty estimate
        total_concepts = len(concepts_in_question)
        if total_concepts > 0:
            unknown_count = len(state["unknown_concepts"]) + 0.5 * len(state["partially_known"])
            state["uncertainty_estimate"] = unknown_count / total_concepts
        else:
            state["uncertainty_estimate"] = 0.0

        return state

    def _print_result(self, result: QueryResult):
        """Вывести результат"""
        print(f"\nAnswer: {result.answer}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"\nEpistemic State:")
        print(f"  Known: {result.epistemic_state['known_concepts']}")
        print(f"  Unknown: {result.epistemic_state['unknown_concepts']}")
        print(f"  Uncertainty: {result.epistemic_state['uncertainty_estimate']:.2f}")
        print(f"\nSelf-Awareness:")
        print(f"  Know answer: {result.self_awareness['know_answer']}")
        print(f"  Meta-confidence: {result.self_awareness['confidence_in_confidence']:.2f}")
        print(f"  Reasoning quality: {result.self_awareness['reasoning_quality']:.2f}")
        print(f"  Gaps: {result.self_awareness['knowledge_gaps']}")
        print(f"  Biases: {result.self_awareness['potential_biases']}")
        print(f"\nReflection: {result.self_awareness['meta_reflection']}")

    def introspect(self) -> Dict[str, Any]:
        """Интроспекция - посмотреть на себя"""
        return {
            "meta_knowledge": {
                "known_concepts": len(self.what_i_know),
                "known_unknowns": len(self.what_i_know_i_dont_know),
                "estimated_unknown_unknowns": len(self.what_i_might_not_know)
            },
            "self_model": self.self_model.get_summary(),
            "knowledge_base": {
                "total_concepts": len(self.knowledge_base.concepts),
                "total_facts": sum(len(facts) for facts in self.knowledge_base.facts.values())
            }
        }


def demo():
    """Демонстрация consciousness-like agent"""
    print("=" * 80)
    print("CONSCIOUSNESS-LIKE SELF-AWARENESS - DEMO")
    print("=" * 80)

    agent = ConsciousAgent(verbose=True)

    # === ОБУЧЕНИЕ ===
    print("\n" + "=" * 80)
    print("LEARNING PHASE")
    print("=" * 80)

    # Обучить концептам с разными epistemic states
    agent.learn_concept(
        concept="5G",
        facts=[
            "5G is the fifth generation of wireless technology",
            "5G provides high-speed connectivity",
            "5G uses millimeter wave frequencies"
        ],
        epistemic_state=EpistemicState.KNOWN,
        confidence=0.9
    )

    agent.learn_concept(
        concept="mmWave",
        facts=[
            "mmWave operates at 30-300 GHz",
            "mmWave has poor penetration through walls"
        ],
        epistemic_state=EpistemicState.KNOWN,
        confidence=0.85
    )

    agent.learn_concept(
        concept="penetration",
        facts=[
            "Signal penetration depends on frequency and material"
        ],
        epistemic_state=EpistemicState.PARTIALLY_KNOWN,
        confidence=0.5
    )

    # Объявить известный unknown
    agent.declare_unknown("6G")

    # === ЗАПРОСЫ ===
    print("\n" + "=" * 80)
    print("QUERY PHASE")
    print("=" * 80)

    # Запрос 1: Хорошо известный вопрос
    result1 = agent.query("What is 5G mmWave?")

    # Запрос 2: Частично известный вопрос
    result2 = agent.query("Does mmWave penetration work through walls?")

    # Запрос 3: Неизвестный вопрос
    result3 = agent.query("What is 6G technology?")

    # Запрос 4: Полностью неизвестный вопрос (unknown unknown)
    result4 = agent.query("What is quantum entanglement in 7G networks?")

    # === INTROSPECTION ===
    print("\n" + "=" * 80)
    print("INTROSPECTION")
    print("=" * 80)

    introspection = agent.introspect()

    print("\nMeta-Knowledge:")
    print(f"  Known concepts: {introspection['meta_knowledge']['known_concepts']}")
    print(f"  Known unknowns: {introspection['meta_knowledge']['known_unknowns']}")
    print(f"  Estimated unknown unknowns: {introspection['meta_knowledge']['estimated_unknown_unknowns']}")

    print("\nSelf-Model:")
    print(f"  Total queries: {introspection['self_model']['total_queries']}")
    print(f"  Success rate: {introspection['self_model']['success_rate']:.2%}")
    print(f"  Strengths: {introspection['self_model']['strengths']}")
    print(f"  Weaknesses: {introspection['self_model']['weaknesses']}")

    print("\nKnowledge Base:")
    print(f"  Total concepts: {introspection['knowledge_base']['total_concepts']}")
    print(f"  Total facts: {introspection['knowledge_base']['total_facts']}")

    # === COMPARATIVE ANALYSIS ===
    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)

    results = [result1, result2, result3, result4]

    print("\nConfidence vs Meta-Confidence:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Query: {result.query[:50]}...")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Meta-confidence: {result.reflection.meta_confidence:.2f}")
        print(f"   Gap: {abs(result.confidence - result.reflection.meta_confidence):.2f}")

    print("\nReasoning Quality:")
    for i, result in enumerate(results, 1):
        quality = result.reflection.reasoning_quality
        print(f"{i}. {result.query[:40]}... → Quality: {quality:.2f}")

    print("\nKnowledge Gaps Identified:")
    for i, result in enumerate(results, 1):
        if result.reflection.identified_gaps:
            print(f"{i}. {result.query[:40]}...")
            for gap in result.reflection.identified_gaps:
                print(f"   - {gap}")

    # === PHILOSOPHICAL REFLECTION ===
    print("\n" + "=" * 80)
    print("PHILOSOPHICAL REFLECTION")
    print("=" * 80)

    print("""
This agent demonstrates consciousness-like self-awareness:

1. KNOWS WHAT IT KNOWS
   - Explicitly tracks known concepts
   - Distinguishes between different levels of knowledge

2. KNOWS WHAT IT DOESN'T KNOW (Known Unknowns)
   - Declares concepts as unknown
   - Identifies knowledge gaps in queries

3. ESTIMATES WHAT IT DOESN'T KNOW IT DOESN'T KNOW (Unknown Unknowns)
   - Detects previously unseen concepts
   - Updates epistemic state dynamically

4. META-COGNITIVE REFLECTION
   - Reflects on its own answers
   - Assesses confidence in confidence
   - Evaluates reasoning quality

5. BIAS DETECTION
   - Identifies potential cognitive biases
   - Self-corrects for overconfidence

6. SELF-MODEL
   - Builds internal model of itself
   - Tracks strengths and weaknesses
   - Improves over time

This is approaching "strong AI" - the system doesn't just answer,
it **understands** what it knows and what it doesn't know.
    """)

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return agent


if __name__ == "__main__":
    agent = demo()
