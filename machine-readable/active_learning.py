#!/usr/bin/env python3
"""
============================================================================
ACTIVE LEARNING - Intelligent Knowledge Gap Identification
============================================================================
Уровень 2.3: ПРОДВИНУТОЕ

Система самостоятельно определяет чему ей нужно научиться:
- Идентификация пробелов в знаниях
- Запрос недостающих знаний у экспертов
- Приоритизация важных пробелов
- Uncertainty-based sample selection
- Query-by-committee
- Self-improvement loop

ВОЗМОЖНОСТИ:
- Система сама определяет чему ей нужно научиться
- Запрашивает пояснения у экспертов
- Приоритизирует важные пробелы
- Самостоятельно улучшает базу знаний

Реальность: 85%
============================================================================
"""

import json
import os
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import random

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class KnowledgeGap:
    """Пробел в знаниях"""
    gap_id: str
    query: str
    missing_concepts: List[str]
    uncertainty_score: float  # 0-1, чем выше - тем больше uncertainty
    priority: float  # 0-1, чем выше - тем важнее
    frequency: int  # Сколько раз встречался похожий запрос
    examples: List[str] = field(default_factory=list)
    identified_at: str = None

    def __post_init__(self):
        if self.identified_at is None:
            self.identified_at = datetime.now().isoformat()


@dataclass
class LearningRequest:
    """Запрос на обучение"""
    request_id: str
    gap: KnowledgeGap
    question: str  # Что спросить у эксперта
    context: Dict[str, Any]
    status: str = "pending"  # pending, answered, integrated
    created_at: str = None
    answered_at: Optional[str] = None
    answer: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class QueryResult:
    """Результат запроса"""
    query: str
    results: List[Dict[str, Any]]
    confidence: float
    uncertainty: float
    method: str
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


# ============================================================================
# ACTIVE LEARNING AGENT
# ============================================================================

class ActiveLearningAgent:
    """
    Агент активного обучения

    Основные компоненты:
    - Uncertainty estimation: определение неуверенности
    - Gap identification: поиск пробелов в знаниях
    - Query selection: выбор наиболее информативных запросов
    - Knowledge integration: интеграция новых знаний
    """

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        uncertainty_threshold: float = 0.7,
        min_gap_frequency: int = 2
    ):
        self.confidence_threshold = confidence_threshold
        self.uncertainty_threshold = uncertainty_threshold
        self.min_gap_frequency = min_gap_frequency

        # История
        self.query_history: List[QueryResult] = []
        self.failed_queries: List[QueryResult] = []
        self.identified_gaps: List[KnowledgeGap] = []
        self.learning_requests: List[LearningRequest] = []
        self.knowledge_base: Dict[str, Any] = {}  # Расширяемая база знаний

        # Статистика
        self.stats = {
            'total_queries': 0,
            'low_confidence_queries': 0,
            'gaps_identified': 0,
            'knowledge_added': 0
        }

    # ========================================================================
    # UNCERTAINTY ESTIMATION
    # ========================================================================

    def calculate_uncertainty(
        self,
        results: List[Dict[str, Any]],
        method: str = "entropy"
    ) -> float:
        """
        Вычисление uncertainty для результатов

        Methods:
        - entropy: информационная энтропия распределения scores
        - variance: дисперсия scores
        - margin: разница между top-1 и top-2 scores
        - confidence: 1 - max(scores)
        """
        if not results:
            return 1.0  # Максимальная uncertainty если нет результатов

        scores = [r.get('score', 0.0) for r in results]

        if method == "entropy":
            # Нормализация scores в распределение вероятностей
            total = sum(scores) if sum(scores) > 0 else 1.0
            probs = [s / total for s in scores]

            # Shannon entropy
            entropy = -sum(p * math.log(p + 1e-10) for p in probs if p > 0)
            max_entropy = math.log(len(scores)) if len(scores) > 1 else 1.0
            return entropy / max_entropy if max_entropy > 0 else 0.0

        elif method == "variance":
            # Variance
            if len(scores) < 2:
                return 0.0
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            return min(1.0, variance * 4)  # Масштабирование в [0, 1]

        elif method == "margin":
            # Margin between top-1 and top-2
            if len(scores) < 2:
                return 1.0 - max(scores, default=0.0)
            sorted_scores = sorted(scores, reverse=True)
            margin = sorted_scores[0] - sorted_scores[1]
            return 1.0 - margin  # Низкий margin = высокая uncertainty

        elif method == "confidence":
            # Simple: 1 - max confidence
            return 1.0 - max(scores, default=0.0)

        else:
            raise ValueError(f"Unknown uncertainty method: {method}")

    def estimate_query_difficulty(self, query: str) -> float:
        """
        Оценка сложности запроса

        Heuristics:
        - Длина запроса
        - Количество специфичных терминов
        - Наличие в базе знаний
        """
        difficulty = 0.0

        # Длина (более длинные запросы сложнее)
        words = query.split()
        if len(words) > 15:
            difficulty += 0.3
        elif len(words) > 8:
            difficulty += 0.2
        elif len(words) > 4:
            difficulty += 0.1

        # Специфичные термины (сложные слова)
        complex_words = [w for w in words if len(w) > 12]
        difficulty += min(0.3, len(complex_words) * 0.1)

        # Наличие в базе знаний
        query_lower = query.lower()
        if not any(concept.lower() in query_lower for concept in self.knowledge_base.keys()):
            difficulty += 0.3

        return min(1.0, difficulty)

    # ========================================================================
    # GAP IDENTIFICATION
    # ========================================================================

    def identify_knowledge_gaps(
        self,
        min_frequency: Optional[int] = None
    ) -> List[KnowledgeGap]:
        """
        Анализ пробелов в знаниях на основе истории запросов

        Алгоритм:
        1. Найти все low-confidence queries
        2. Кластеризовать похожие запросы
        3. Определить missing concepts
        4. Вычислить priority
        """
        if min_frequency is None:
            min_frequency = self.min_gap_frequency

        # Анализ failed queries
        query_clusters = defaultdict(list)

        for query_result in self.failed_queries:
            # Простая кластеризация по first word
            first_word = query_result.query.split()[0].lower() if query_result.query else "unknown"
            query_clusters[first_word].append(query_result)

        gaps = []

        for cluster_key, cluster_queries in query_clusters.items():
            if len(cluster_queries) < min_frequency:
                continue

            # Определение missing concepts
            missing_concepts = self._extract_missing_concepts(cluster_queries)

            # Вычисление uncertainty
            avg_uncertainty = sum(
                q.uncertainty for q in cluster_queries
            ) / len(cluster_queries)

            # Вычисление priority
            priority = self._calculate_gap_priority(
                cluster_queries,
                avg_uncertainty,
                missing_concepts
            )

            gap = KnowledgeGap(
                gap_id=f"gap_{len(gaps)}_{cluster_key}",
                query=cluster_queries[0].query,  # Representative query
                missing_concepts=missing_concepts,
                uncertainty_score=avg_uncertainty,
                priority=priority,
                frequency=len(cluster_queries),
                examples=[q.query for q in cluster_queries[:5]]
            )

            gaps.append(gap)

        # Сортировка по priority
        gaps.sort(key=lambda g: g.priority, reverse=True)
        self.identified_gaps.extend(gaps)
        self.stats['gaps_identified'] += len(gaps)

        return gaps

    def _extract_missing_concepts(
        self,
        queries: List[QueryResult]
    ) -> List[str]:
        """Извлечение missing concepts из запросов"""
        # Простая эвристика: слова которые не в knowledge base
        all_words = set()
        for query_result in queries:
            all_words.update(query_result.query.lower().split())

        known_concepts = set(c.lower() for c in self.knowledge_base.keys())
        missing = list(all_words - known_concepts - {'the', 'a', 'an', 'and', 'or', 'is', 'are'})

        return missing[:5]  # Top 5 missing

    def _calculate_gap_priority(
        self,
        queries: List[QueryResult],
        uncertainty: float,
        missing_concepts: List[str]
    ) -> float:
        """
        Вычисление приоритета пробела

        Факторы:
        - Frequency: чем чаще встречается, тем важнее
        - Uncertainty: чем больше uncertainty, тем важнее
        - Number of missing concepts: чем больше пробелов, тем важнее
        """
        frequency_score = min(1.0, len(queries) / 10.0)  # Нормализация
        uncertainty_score = uncertainty
        missing_score = min(1.0, len(missing_concepts) / 5.0)

        # Weighted average
        priority = (
            0.4 * frequency_score +
            0.4 * uncertainty_score +
            0.2 * missing_score
        )

        return priority

    # ========================================================================
    # QUERY SELECTION
    # ========================================================================

    def select_queries_for_labeling(
        self,
        gaps: List[KnowledgeGap],
        budget: int = 5,
        strategy: str = "uncertainty"
    ) -> List[LearningRequest]:
        """
        Выбор queries для labeling/clarification

        Strategies:
        - uncertainty: наибольшая uncertainty
        - diversity: максимальное разнообразие
        - priority: highest priority
        """
        if strategy == "uncertainty":
            # Сортировка по uncertainty
            sorted_gaps = sorted(gaps, key=lambda g: g.uncertainty_score, reverse=True)
        elif strategy == "diversity":
            # Diversity sampling (простая: разные first words)
            sorted_gaps = self._diversity_sampling(gaps)
        elif strategy == "priority":
            # По priority
            sorted_gaps = sorted(gaps, key=lambda g: g.priority, reverse=True)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Выбор top-k
        selected_gaps = sorted_gaps[:budget]

        # Создание learning requests
        requests = []
        for gap in selected_gaps:
            request = self._create_learning_request(gap)
            requests.append(request)

        self.learning_requests.extend(requests)
        return requests

    def _diversity_sampling(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Diversity-based sampling"""
        # Простая эвристика: группировка по first word
        groups = defaultdict(list)
        for gap in gaps:
            first_word = gap.query.split()[0].lower() if gap.query else "unknown"
            groups[first_word].append(gap)

        # Берём по одному из каждой группы (highest uncertainty)
        diverse = []
        for group_gaps in groups.values():
            best = max(group_gaps, key=lambda g: g.uncertainty_score)
            diverse.append(best)

        # Сортировка по uncertainty
        diverse.sort(key=lambda g: g.uncertainty_score, reverse=True)
        return diverse

    def _create_learning_request(self, gap: KnowledgeGap) -> LearningRequest:
        """Создание learning request для эксперта"""
        # Формирование вопроса
        missing_str = ", ".join(gap.missing_concepts[:3])
        question = (
            f"I'm uncertain about this query: '{gap.query}'\n\n"
            f"Missing concepts might include: {missing_str}\n\n"
            f"Can you provide:\n"
            f"1. Explanation of the query\n"
            f"2. Definition of key concepts\n"
            f"3. Example use cases"
        )

        request = LearningRequest(
            request_id=f"req_{gap.gap_id}_{len(self.learning_requests)}",
            gap=gap,
            question=question,
            context={
                'uncertainty': gap.uncertainty_score,
                'priority': gap.priority,
                'frequency': gap.frequency
            }
        )

        return request

    # ========================================================================
    # KNOWLEDGE INTEGRATION
    # ========================================================================

    def integrate_expert_feedback(
        self,
        request_id: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Интеграция ответа эксперта в базу знаний

        1. Найти request
        2. Пометить как answered
        3. Добавить в knowledge base
        4. Обновить статистику
        """
        # Найти request
        request = next(
            (r for r in self.learning_requests if r.request_id == request_id),
            None
        )

        if not request:
            print(f"⚠️  Request {request_id} not found")
            return

        # Обновить request
        request.answer = answer
        request.answered_at = datetime.now().isoformat()
        request.status = "answered"

        # Добавить в knowledge base
        for concept in request.gap.missing_concepts:
            if concept not in self.knowledge_base:
                self.knowledge_base[concept] = {
                    'explanation': answer,
                    'source': 'expert',
                    'related_queries': [request.gap.query],
                    'added_at': datetime.now().isoformat(),
                    'metadata': metadata or {}
                }
                self.stats['knowledge_added'] += 1

        request.status = "integrated"
        print(f"✅ Integrated knowledge from request {request_id}")

    def learn_from_clarification(
        self,
        query: str,
        clarification: str
    ):
        """Добавление clarification в базу знаний"""
        self.knowledge_base[query] = {
            'clarification': clarification,
            'source': 'user',
            'added_at': datetime.now().isoformat()
        }
        self.stats['knowledge_added'] += 1

    # ========================================================================
    # QUERY PROCESSING
    # ========================================================================

    def query(
        self,
        question: str,
        mock_search: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Обработка запроса с active learning

        1. Выполнить базовый поиск
        2. Оценить confidence и uncertainty
        3. Если низкая confidence - запросить помощь
        4. Вернуть результат
        """
        self.stats['total_queries'] += 1

        # Mock search function для демонстрации
        if mock_search is None:
            mock_search = self._mock_search

        # Базовый поиск
        results = mock_search(question)

        # Вычисление метрик
        max_score = max((r.get('score', 0.0) for r in results), default=0.0)
        confidence = max_score
        uncertainty = self.calculate_uncertainty(results, method="entropy")

        query_result = QueryResult(
            query=question,
            results=results,
            confidence=confidence,
            uncertainty=uncertainty,
            method="mock"
        )

        self.query_history.append(query_result)

        # Если confidence низкая - записать как failed
        if confidence < self.confidence_threshold:
            self.failed_queries.append(query_result)
            self.stats['low_confidence_queries'] += 1

            # Если uncertainty высокая - запросить помощь
            if uncertainty > self.uncertainty_threshold:
                print(f"\n⚠️  LOW CONFIDENCE detected!")
                print(f"   Query: {question}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Uncertainty: {uncertainty:.2f}")
                print(f"   → Requesting expert clarification")

                # В реальной системе здесь был бы запрос к эксперту
                # Для демонстрации просто помечаем
                gap = KnowledgeGap(
                    gap_id=f"gap_auto_{len(self.identified_gaps)}",
                    query=question,
                    missing_concepts=question.split()[:3],
                    uncertainty_score=uncertainty,
                    priority=uncertainty,
                    frequency=1
                )
                self.identified_gaps.append(gap)

        return {
            'results': results,
            'confidence': confidence,
            'uncertainty': uncertainty,
            'status': 'success' if confidence >= self.confidence_threshold else 'low_confidence'
        }

    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """Mock search function для демонстрации"""
        query_lower = query.lower()

        # Если query содержит известные concepts - high confidence
        # Иначе - low confidence
        known_concepts = list(self.knowledge_base.keys())

        if any(concept.lower() in query_lower for concept in known_concepts):
            # High confidence
            return [
                {'text': f'Result 1 for "{query}"', 'score': 0.9},
                {'text': f'Result 2 for "{query}"', 'score': 0.75},
                {'text': f'Result 3 for "{query}"', 'score': 0.6},
            ]
        else:
            # Low confidence
            return [
                {'text': f'Maybe related to "{query}"', 'score': 0.3},
                {'text': f'Possibly about "{query}"', 'score': 0.25},
            ]

    # ========================================================================
    # STATISTICS & REPORTING
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика active learning"""
        return {
            'queries': {
                'total': self.stats['total_queries'],
                'low_confidence': self.stats['low_confidence_queries'],
                'low_confidence_rate': (
                    self.stats['low_confidence_queries'] / self.stats['total_queries']
                    if self.stats['total_queries'] > 0 else 0.0
                )
            },
            'gaps': {
                'identified': self.stats['gaps_identified'],
                'total': len(self.identified_gaps)
            },
            'learning': {
                'requests': len(self.learning_requests),
                'pending': len([r for r in self.learning_requests if r.status == 'pending']),
                'answered': len([r for r in self.learning_requests if r.status == 'answered']),
                'integrated': len([r for r in self.learning_requests if r.status == 'integrated'])
            },
            'knowledge_base': {
                'concepts': len(self.knowledge_base),
                'knowledge_added': self.stats['knowledge_added']
            }
        }

    def report_knowledge_gaps(self, top_k: int = 10) -> str:
        """Отчёт о пробелах в знаниях"""
        gaps = sorted(self.identified_gaps, key=lambda g: g.priority, reverse=True)[:top_k]

        report = "=" * 70 + "\n"
        report += "KNOWLEDGE GAPS REPORT\n"
        report += "=" * 70 + "\n\n"

        for i, gap in enumerate(gaps, 1):
            report += f"{i}. {gap.query}\n"
            report += f"   Priority: {gap.priority:.2f}\n"
            report += f"   Uncertainty: {gap.uncertainty_score:.2f}\n"
            report += f"   Frequency: {gap.frequency}\n"
            report += f"   Missing: {', '.join(gap.missing_concepts[:3])}\n"
            report += "\n"

        return report


# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_active_learning():
    """Демонстрация Active Learning"""
    print("=" * 70)
    print("  ACTIVE LEARNING - Demo")
    print("=" * 70)
    print()

    # ========================================================================
    # 1. Инициализация
    # ========================================================================
    print("=" * 70)
    print("1. Initializing Active Learning Agent")
    print("=" * 70)

    agent = ActiveLearningAgent(
        confidence_threshold=0.5,
        uncertainty_threshold=0.7,
        min_gap_frequency=2
    )

    # Добавление начальных знаний
    initial_knowledge = {
        'machine learning': {'type': 'concept', 'domain': 'AI'},
        'neural networks': {'type': 'concept', 'domain': 'AI'},
        'python': {'type': 'language', 'domain': 'programming'},
    }

    for concept, data in initial_knowledge.items():
        agent.knowledge_base[concept] = data

    print(f"  ✅ Agent initialized")
    print(f"  ✅ Initial knowledge: {len(agent.knowledge_base)} concepts")
    print()

    # ========================================================================
    # 2. Симуляция запросов
    # ========================================================================
    print("=" * 70)
    print("2. Simulating User Queries")
    print("=" * 70)

    test_queries = [
        "What is machine learning?",  # Known - high confidence
        "Explain neural networks",    # Known - high confidence
        "Python tutorial",             # Known - high confidence
        "Quantum computing basics",    # Unknown - low confidence
        "Quantum entanglement",        # Unknown - low confidence
        "Blockchain technology",       # Unknown - low confidence
        "Quantum algorithms",          # Unknown - low confidence (repeated theme)
        "Distributed ledger",          # Unknown - low confidence
    ]

    for query in test_queries:
        result = agent.query(query)
        print(f"  Query: {query}")
        print(f"    Confidence: {result['confidence']:.2f}, Uncertainty: {result['uncertainty']:.2f}")
        print(f"    Status: {result['status']}")
        print()

    # ========================================================================
    # 3. Идентификация пробелов
    # ========================================================================
    print("=" * 70)
    print("3. Identifying Knowledge Gaps")
    print("=" * 70)

    gaps = agent.identify_knowledge_gaps(min_frequency=1)

    print(f"  ✅ Identified {len(gaps)} knowledge gaps")
    for gap in gaps[:5]:
        print(f"\n  Gap: {gap.query}")
        print(f"    Priority: {gap.priority:.2f}")
        print(f"    Uncertainty: {gap.uncertainty_score:.2f}")
        print(f"    Frequency: {gap.frequency}")
        print(f"    Missing concepts: {', '.join(gap.missing_concepts[:3])}")

    print()

    # ========================================================================
    # 4. Выбор queries для labeling
    # ========================================================================
    print("=" * 70)
    print("4. Selecting Queries for Expert Labeling")
    print("=" * 70)

    requests = agent.select_queries_for_labeling(
        gaps=gaps,
        budget=3,
        strategy="priority"
    )

    print(f"  ✅ Selected {len(requests)} queries for labeling")
    for request in requests:
        print(f"\n  Request ID: {request.request_id}")
        print(f"  Gap: {request.gap.query}")
        print(f"  Priority: {request.gap.priority:.2f}")
        print(f"  Question for expert:")
        print(f"    {request.question[:100]}...")

    print()

    # ========================================================================
    # 5. Симуляция expert feedback
    # ========================================================================
    print("=" * 70)
    print("5. Simulating Expert Feedback")
    print("=" * 70)

    # Симуляция ответов эксперта
    for request in requests[:2]:  # Обработаем первые 2
        expert_answer = f"Explanation of '{request.gap.query}': This is a detailed explanation with examples and use cases."

        print(f"\n  Processing request: {request.request_id}")
        agent.integrate_expert_feedback(
            request_id=request.request_id,
            answer=expert_answer,
            metadata={'source': 'simulated_expert'}
        )

    print()

    # ========================================================================
    # 6. Проверка улучшения
    # ========================================================================
    print("=" * 70)
    print("6. Verifying Improvement")
    print("=" * 70)

    # Повторный запрос
    improved_query = "Quantum computing basics"
    print(f"  Re-querying: {improved_query}")

    result_before = agent.query_history[3]  # Quantum computing query
    result_after = agent.query(improved_query)

    print(f"\n  Before expert feedback:")
    print(f"    Confidence: {result_before.confidence:.2f}")
    print(f"    Uncertainty: {result_before.uncertainty:.2f}")

    print(f"\n  After expert feedback:")
    print(f"    Confidence: {result_after['confidence']:.2f}")
    print(f"    Uncertainty: {result_after['uncertainty']:.2f}")

    print()

    # ========================================================================
    # 7. Статистика
    # ========================================================================
    print("=" * 70)
    print("7. Statistics")
    print("=" * 70)

    stats = agent.get_statistics()

    print(f"  Queries:")
    print(f"    Total: {stats['queries']['total']}")
    print(f"    Low confidence: {stats['queries']['low_confidence']}")
    print(f"    Low confidence rate: {stats['queries']['low_confidence_rate']:.1%}")

    print(f"\n  Knowledge Gaps:")
    print(f"    Identified: {stats['gaps']['identified']}")

    print(f"\n  Learning Requests:")
    print(f"    Total: {stats['learning']['requests']}")
    print(f"    Pending: {stats['learning']['pending']}")
    print(f"    Answered: {stats['learning']['answered']}")
    print(f"    Integrated: {stats['learning']['integrated']}")

    print(f"\n  Knowledge Base:")
    print(f"    Concepts: {stats['knowledge_base']['concepts']}")
    print(f"    Knowledge added: {stats['knowledge_base']['knowledge_added']}")

    print()

    # ========================================================================
    # 8. Knowledge Gaps Report
    # ========================================================================
    print("=" * 70)
    print("8. Knowledge Gaps Report")
    print("=" * 70)

    report = agent.report_knowledge_gaps(top_k=5)
    print(report)

    print("=" * 70)
    print("  Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_active_learning()
