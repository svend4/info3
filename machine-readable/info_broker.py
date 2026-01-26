#!/usr/bin/env python3
"""
ИНФОБРОКЕР - ПОСРЕДНИК МЕЖДУ AI И СТРУКТУРИРОВАННЫМИ ДАННЫМИ
============================================================

Концепция: "Информационный Redis" - виртуальный посредник, коммивояжёр знаний

ФИЛОСОФИЯ:
- Не физический кэш данных, а ИНФОРМАЦИОННЫЙ посредник
- Стоит между нейросетью и хаотичными данными
- Структурирует, фильтрует, оптимизирует доступ к знаниям
- Понимает контекст и намерения AI-системы
- Автономно принимает решения о маршрутизации запросов

РОЛИ:
- 🚚 Коммивояжёр: доставляет нужную информацию в нужное место
- 🎯 Курьер: быстрая доставка срочных знаний
- 📮 Почтальон: регулярная доставка паттернов
- 🔀 Маршрутизатор: выбирает оптимальный путь к данным
- 🧠 Консультант: советует какие знания применить

АРХИТЕКТУРА: Multi-Agent с специализацией
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


class QueryIntent(Enum):
    """Намерения запроса (зачем AI обращается?)"""
    SOLVE_PROBLEM = "solve_problem"           # Решить конкретную проблему
    LEARN_CONCEPT = "learn_concept"           # Изучить концепцию
    FIND_ANALOGY = "find_analogy"             # Найти аналогию
    GET_FORMULA = "get_formula"               # Получить формулу
    SEE_EXAMPLES = "see_examples"             # Увидеть примеры
    VALIDATE_APPROACH = "validate_approach"   # Валидировать подход
    EXPLORE_DOMAIN = "explore_domain"         # Исследовать область
    COMPARE_OPTIONS = "compare_options"       # Сравнить опции


class KnowledgeRoute(Enum):
    """Маршруты доставки знаний"""
    EXPRESS = "express"           # Самый быстрый (кэш)
    STANDARD = "standard"         # Обычный поиск
    DEEP_SEARCH = "deep_search"   # Глубокий поиск
    MULTI_SOURCE = "multi_source" # Из нескольких источников
    SYNTHESIZE = "synthesize"     # Синтезировать из частей


@dataclass
class KnowledgePackage:
    """Пакет знаний для доставки AI-системе"""
    content: Any
    confidence: float
    route_taken: str
    delivery_time_ms: float
    sources: List[str]
    metadata: Dict[str, Any]
    recommendations: List[str]  # Что делать дальше


@dataclass
class BrokerDecision:
    """Решение брокера"""
    decision_type: str
    action: str
    reasoning: str
    alternatives_considered: List[str]
    confidence: float
    timestamp: str


class InfoBroker:
    """
    ИНФОБРОКЕР - главный класс

    Управляет потоком информации между AI и базой знаний
    Автономно принимает решения о маршрутизации
    """

    def __init__(self, knowledge_base_path: str = "афоризмы"):
        self.kb_path = Path(knowledge_base_path)

        # Загрузка агентов (будут созданы позже)
        self.agents = {}

        # Маршрутизация: какой агент для какой задачи
        self.routing_rules = self._init_routing_rules()

        # История обслуживания
        self.service_history = []

        # Статистика брокера
        self.broker_stats = {
            "requests_served": 0,
            "avg_delivery_time_ms": 0,
            "routes_used": {route.value: 0 for route in KnowledgeRoute},
            "intents_served": {intent.value: 0 for intent in QueryIntent},
            "customer_satisfaction": 0.0  # AI системы как "клиенты"
        }

        # Кэш маршрутов (какой маршрут работал лучше для какого типа запросов)
        self.route_cache = {}

        print("═══════════════════════════════════════════════════════════")
        print("  ИНФОБРОКЕР ИНИЦИАЛИЗИРОВАН")
        print("═══════════════════════════════════════════════════════════")
        print(f"  Роль: Посредник между AI и структурированными знаниями")
        print(f"  База знаний: {self.kb_path}")
        print(f"  Маршрутов доступно: {len(KnowledgeRoute)}")
        print(f"  Намерений понимает: {len(QueryIntent)}")
        print("═══════════════════════════════════════════════════════════")

    def _init_routing_rules(self) -> Dict:
        """Инициализация правил маршрутизации"""
        return {
            QueryIntent.SOLVE_PROBLEM: [
                KnowledgeRoute.EXPRESS,      # Сначала проверить кэш
                KnowledgeRoute.MULTI_SOURCE, # Если нет - из нескольких источников
                KnowledgeRoute.SYNTHESIZE    # Синтезировать решение
            ],
            QueryIntent.LEARN_CONCEPT: [
                KnowledgeRoute.STANDARD,     # Обычный поиск
                KnowledgeRoute.DEEP_SEARCH   # Если нужно глубже
            ],
            QueryIntent.FIND_ANALOGY: [
                KnowledgeRoute.MULTI_SOURCE, # Искать в разных доменах
                KnowledgeRoute.SYNTHESIZE    # Синтезировать аналогию
            ],
            QueryIntent.GET_FORMULA: [
                KnowledgeRoute.EXPRESS,      # Формулы кэшируются
                KnowledgeRoute.STANDARD
            ],
            QueryIntent.SEE_EXAMPLES: [
                KnowledgeRoute.STANDARD,
                KnowledgeRoute.MULTI_SOURCE
            ],
            QueryIntent.VALIDATE_APPROACH: [
                KnowledgeRoute.MULTI_SOURCE, # Сравнить с известными подходами
                KnowledgeRoute.SYNTHESIZE
            ],
            QueryIntent.EXPLORE_DOMAIN: [
                KnowledgeRoute.DEEP_SEARCH,
                KnowledgeRoute.MULTI_SOURCE
            ],
            QueryIntent.COMPARE_OPTIONS: [
                KnowledgeRoute.MULTI_SOURCE,
                KnowledgeRoute.SYNTHESIZE
            ]
        }

    def serve(self,
              query: str,
              intent: Optional[QueryIntent] = None,
              context: Optional[Dict] = None,
              urgency: str = "normal") -> KnowledgePackage:
        """
        ГЛАВНЫЙ МЕТОД: обслуживание запроса от AI системы

        Args:
            query: Запрос
            intent: Намерение (опционально, будет определено автоматически)
            context: Контекст (предыдущие запросы, состояние AI)
            urgency: Срочность ("low", "normal", "high", "critical")

        Returns:
            KnowledgePackage: Упакованные знания с метаданными
        """
        start_time = time.time()
        self.broker_stats["requests_served"] += 1

        decisions = []

        print(f"\n{'='*70}")
        print(f"  НОВЫЙ ЗАПРОС К ИНФОБРОКЕРУ")
        print(f"{'='*70}")
        print(f"  Запрос: {query[:50]}...")
        print(f"  Срочность: {urgency}")

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 1: Определение намерения (если не указано)
        # ═══════════════════════════════════════════════════════════════
        if intent is None:
            intent_decision = self._decide_intent(query)
            decisions.append(intent_decision)
            intent = intent_decision["intent"]
        else:
            decisions.append(BrokerDecision(
                decision_type="intent",
                action=f"use_provided:{intent.value}",
                reasoning="Намерение предоставлено клиентом",
                alternatives_considered=[],
                confidence=1.0,
                timestamp=datetime.now().isoformat()
            ))

        print(f"  Намерение: {intent.value}")
        self.broker_stats["intents_served"][intent.value] += 1

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 2: Выбор маршрута доставки
        # ═══════════════════════════════════════════════════════════════
        route_decision = self._decide_route(query, intent, urgency, context)
        decisions.append(route_decision)
        route = route_decision["route"]

        print(f"  Маршрут: {route.value}")
        self.broker_stats["routes_used"][route.value] += 1

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 3: Выполнение запроса по выбранному маршруту
        # ═══════════════════════════════════════════════════════════════
        delivery_result = self._execute_delivery(query, route, intent, context)
        decisions.append(delivery_result["decision"])

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 4: Упаковка результата
        # ═══════════════════════════════════════════════════════════════
        package = self._package_knowledge(
            content=delivery_result["content"],
            route=route,
            confidence=delivery_result["confidence"],
            sources=delivery_result["sources"],
            decisions=decisions,
            elapsed=time.time() - start_time
        )

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 5: Генерация рекомендаций
        # ═══════════════════════════════════════════════════════════════
        recommendations = self._generate_recommendations(query, intent, package, context)
        package.recommendations = recommendations

        # Обновление статистики
        self._update_stats(package)

        # Логирование
        self._log_service(query, intent, route, package, decisions)

        print(f"  Доставлено за: {package.delivery_time_ms:.2f} ms")
        print(f"  Уверенность: {package.confidence:.2f}")
        print(f"  Источников: {len(package.sources)}")
        print(f"{'='*70}\n")

        return package

    def _decide_intent(self, query: str) -> BrokerDecision:
        """РЕШЕНИЕ 1: Определение намерения запроса"""
        q = query.lower()

        # Эвристики для определения намерения
        intent_signals = {
            QueryIntent.GET_FORMULA: ['формула', 'уравнение', 'expression', 'equation'],
            QueryIntent.SEE_EXAMPLES: ['пример', 'example', 'case study', 'кейс'],
            QueryIntent.LEARN_CONCEPT: ['что такое', 'объясни', 'explain', 'what is'],
            QueryIntent.SOLVE_PROBLEM: ['как решить', 'как сделать', 'how to', 'проблема'],
            QueryIntent.FIND_ANALOGY: ['аналогия', 'похож', 'similar', 'analogy', 'like'],
            QueryIntent.VALIDATE_APPROACH: ['правильно ли', 'валидно', 'validate', 'correct'],
            QueryIntent.EXPLORE_DOMAIN: ['обзор', 'все о', 'overview', 'comprehensive'],
            QueryIntent.COMPARE_OPTIONS: ['сравни', 'разница', 'compare', 'difference', 'vs']
        }

        scores = {}
        for intent, signals in intent_signals.items():
            score = sum(1 for signal in signals if signal in q)
            if score > 0:
                scores[intent] = score

        if scores:
            detected_intent = max(scores, key=scores.get)
            confidence = min(0.9, scores[detected_intent] / 3.0)
            alternatives = [i.value for i in scores.keys() if i != detected_intent]
        else:
            detected_intent = QueryIntent.EXPLORE_DOMAIN  # Default
            confidence = 0.5
            alternatives = []

        return BrokerDecision(
            decision_type="intent_detection",
            action=detected_intent.value,
            reasoning=f"Обнаружены сигналы: {intent_signals.get(detected_intent, [])}",
            alternatives_considered=alternatives,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )

    def _decide_route(self, query: str, intent: QueryIntent, urgency: str, context: Optional[Dict]) -> Dict:
        """РЕШЕНИЕ 2: Выбор оптимального маршрута"""

        # Проверка кэша маршрутов
        cache_key = f"{intent.value}_{urgency}"
        if cache_key in self.route_cache:
            cached_route = self.route_cache[cache_key]
            return {
                "route": cached_route,
                "decision": BrokerDecision(
                    decision_type="route_selection",
                    action=cached_route.value,
                    reasoning="Использован закэшированный оптимальный маршрут",
                    alternatives_considered=[],
                    confidence=0.9,
                    timestamp=datetime.now().isoformat()
                )
            }

        # Получение возможных маршрутов для данного намерения
        possible_routes = self.routing_rules.get(intent, [KnowledgeRoute.STANDARD])

        # Выбор на основе срочности
        if urgency == "critical":
            # Всегда EXPRESS для критических
            selected_route = KnowledgeRoute.EXPRESS
            reasoning = "Критическая срочность → EXPRESS маршрут"
        elif urgency == "high":
            # Первый маршрут из списка
            selected_route = possible_routes[0]
            reasoning = f"Высокая срочность → {selected_route.value}"
        elif urgency == "low":
            # DEEP_SEARCH если доступен, иначе STANDARD
            if KnowledgeRoute.DEEP_SEARCH in possible_routes:
                selected_route = KnowledgeRoute.DEEP_SEARCH
                reasoning = "Низкая срочность → глубокий поиск"
            else:
                selected_route = possible_routes[-1]
                reasoning = f"Низкая срочность → {selected_route.value}"
        else:  # normal
            # Первый маршрут по умолчанию
            selected_route = possible_routes[0]
            reasoning = f"Нормальная срочность → {selected_route.value}"

        # Кэшируем решение
        self.route_cache[cache_key] = selected_route

        alternatives = [r.value for r in possible_routes if r != selected_route]

        return {
            "route": selected_route,
            "decision": BrokerDecision(
                decision_type="route_selection",
                action=selected_route.value,
                reasoning=reasoning,
                alternatives_considered=alternatives,
                confidence=0.85,
                timestamp=datetime.now().isoformat()
            )
        }

    def _execute_delivery(self, query: str, route: KnowledgeRoute, intent: QueryIntent, context: Optional[Dict]) -> Dict:
        """РЕШЕНИЕ 3: Выполнение доставки по маршруту"""

        # В реальной реализации здесь вызывались бы различные агенты
        # Для демонстрации - простая эмуляция

        if route == KnowledgeRoute.EXPRESS:
            # Быстрый кэш-поиск
            content = self._mock_express_search(query)
            confidence = 0.9
            sources = ["cache"]
            reasoning = "EXPRESS: данные из кэша"

        elif route == KnowledgeRoute.STANDARD:
            # Обычный поиск
            content = self._mock_standard_search(query)
            confidence = 0.75
            sources = ["knowledge_base"]
            reasoning = "STANDARD: поиск в базе знаний"

        elif route == KnowledgeRoute.DEEP_SEARCH:
            # Глубокий поиск
            content = self._mock_deep_search(query)
            confidence = 0.85
            sources = ["knowledge_base", "extended_search"]
            reasoning = "DEEP_SEARCH: расширенный поиск"

        elif route == KnowledgeRoute.MULTI_SOURCE:
            # Из нескольких источников
            content = self._mock_multi_source(query)
            confidence = 0.8
            sources = ["knowledge_base", "формулы", "примеры", "алгоритмы"]
            reasoning = "MULTI_SOURCE: агрегация из нескольких доменов"

        elif route == KnowledgeRoute.SYNTHESIZE:
            # Синтез из частей
            content = self._mock_synthesize(query)
            confidence = 0.7
            sources = ["synthesized_knowledge"]
            reasoning = "SYNTHESIZE: синтезированный ответ из частей"

        else:
            content = {"error": "Unknown route"}
            confidence = 0.0
            sources = []
            reasoning = "ERROR: неизвестный маршрут"

        return {
            "content": content,
            "confidence": confidence,
            "sources": sources,
            "decision": BrokerDecision(
                decision_type="delivery_execution",
                action=route.value,
                reasoning=reasoning,
                alternatives_considered=[],
                confidence=confidence,
                timestamp=datetime.now().isoformat()
            )
        }

    def _mock_express_search(self, query: str) -> Dict:
        """Эмуляция EXPRESS поиска"""
        return {
            "type": "express_result",
            "query": query,
            "data": "Быстрый результат из кэша",
            "cached": True
        }

    def _mock_standard_search(self, query: str) -> Dict:
        """Эмуляция STANDARD поиска"""
        return {
            "type": "standard_result",
            "query": query,
            "data": "Результат из базы знаний",
            "results_count": 5
        }

    def _mock_deep_search(self, query: str) -> Dict:
        """Эмуляция DEEP поиска"""
        return {
            "type": "deep_search_result",
            "query": query,
            "data": "Глубокий анализ из расширенного поиска",
            "depth_level": 3,
            "results_count": 15
        }

    def _mock_multi_source(self, query: str) -> Dict:
        """Эмуляция MULTI_SOURCE поиска"""
        return {
            "type": "multi_source_result",
            "query": query,
            "data": "Агрегированные данные из нескольких источников",
            "sources": ["формулы", "архетипы", "алгоритмы", "теоремы"],
            "aggregation_method": "weighted_merge"
        }

    def _mock_synthesize(self, query: str) -> Dict:
        """Эмуляция SYNTHESIZE"""
        return {
            "type": "synthesized_result",
            "query": query,
            "data": "Синтезированный ответ из частей знаний",
            "synthesis_confidence": 0.7,
            "parts_used": 4
        }

    def _package_knowledge(self, content: Any, route: KnowledgeRoute, confidence: float,
                          sources: List[str], decisions: List[Any], elapsed: float) -> KnowledgePackage:
        """РЕШЕНИЕ 4: Упаковка результата в стандартный формат"""

        metadata = {
            "packaged_at": datetime.now().isoformat(),
            "decisions_made": len(decisions),
            "route_efficiency": self._calculate_route_efficiency(route, elapsed)
        }

        return KnowledgePackage(
            content=content,
            confidence=confidence,
            route_taken=route.value,
            delivery_time_ms=elapsed * 1000,
            sources=sources,
            metadata=metadata,
            recommendations=[]  # Будет заполнено позже
        )

    def _calculate_route_efficiency(self, route: KnowledgeRoute, elapsed: float) -> float:
        """Эффективность маршрута (меньше время = выше эффективность)"""
        # EXPRESS должен быть <10ms, DEEP_SEARCH может быть >100ms
        target_times = {
            KnowledgeRoute.EXPRESS: 0.01,
            KnowledgeRoute.STANDARD: 0.05,
            KnowledgeRoute.DEEP_SEARCH: 0.15,
            KnowledgeRoute.MULTI_SOURCE: 0.1,
            KnowledgeRoute.SYNTHESIZE: 0.2
        }

        target = target_times.get(route, 0.1)
        efficiency = max(0.0, 1.0 - (elapsed - target) / target)
        return min(1.0, efficiency)

    def _generate_recommendations(self, query: str, intent: QueryIntent,
                                 package: KnowledgePackage, context: Optional[Dict]) -> List[str]:
        """РЕШЕНИЕ 5: Генерация рекомендаций для AI системы"""

        recommendations = []

        # Рекомендации на основе намерения
        if intent == QueryIntent.GET_FORMULA:
            recommendations.append("💡 Рекомендация: Посмотрите примеры применения этой формулы")
            recommendations.append("📚 Следующий шаг: Изучите алгоритм использования")

        elif intent == QueryIntent.SEE_EXAMPLES:
            recommendations.append("🔍 Рекомендация: Обобщите паттерны из примеров")
            recommendations.append("⚡ Попробуйте: Адаптировать пример под свою задачу")

        elif intent == QueryIntent.SOLVE_PROBLEM:
            recommendations.append("✓ Следующий шаг: Валидировать решение")
            recommendations.append("🎯 Проверьте: Есть ли похожие решённые проблемы")

        elif intent == QueryIntent.LEARN_CONCEPT:
            recommendations.append("📖 Углубитесь: Изучите связанные концепции")
            recommendations.append("🧪 Практика: Найдите примеры применения")

        # Рекомендации на основе уверенности
        if package.confidence < 0.6:
            recommendations.append("⚠️ Низкая уверенность: Рекомендуется дополнительный поиск")
            recommendations.append("🔄 Попробуйте: Переформулировать запрос")

        # Рекомендации на основе маршрута
        if package.route_taken == KnowledgeRoute.EXPRESS.value:
            recommendations.append("⚡ Быстрая доставка: Данные из кэша, возможно не самые актуальные")

        return recommendations

    def _update_stats(self, package: KnowledgePackage):
        """Обновление статистики брокера"""
        # Скользящее среднее времени доставки
        n = self.broker_stats["requests_served"]
        old_avg = self.broker_stats["avg_delivery_time_ms"]
        new_time = package.delivery_time_ms

        self.broker_stats["avg_delivery_time_ms"] = (old_avg * (n - 1) + new_time) / n

        # Удовлетворённость клиента (на основе confidence)
        old_sat = self.broker_stats["customer_satisfaction"]
        self.broker_stats["customer_satisfaction"] = (old_sat * (n - 1) + package.confidence) / n

    def _log_service(self, query: str, intent: QueryIntent, route: KnowledgeRoute,
                    package: KnowledgePackage, decisions: List[Any]):
        """Логирование обслуживания"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "intent": intent.value,
            "route": route.value,
            "delivery_time_ms": package.delivery_time_ms,
            "confidence": package.confidence,
            "decisions": [asdict(d) if hasattr(d, '__dataclass_fields__') else d for d in decisions]
        }
        self.service_history.append(log_entry)

    def get_statistics(self) -> Dict:
        """Получение статистики брокера"""
        return {
            "broker_stats": self.broker_stats,
            "total_services": len(self.service_history),
            "route_preferences": self._analyze_route_preferences(),
            "intent_distribution": self._analyze_intent_distribution()
        }

    def _analyze_route_preferences(self) -> Dict:
        """Анализ предпочтений маршрутов"""
        if not self.service_history:
            return {}

        route_times = {}
        for entry in self.service_history:
            route = entry["route"]
            time_ms = entry["delivery_time_ms"]

            if route not in route_times:
                route_times[route] = []
            route_times[route].append(time_ms)

        # Средние времена
        route_avg = {route: sum(times) / len(times) for route, times in route_times.items()}
        return route_avg

    def _analyze_intent_distribution(self) -> Dict:
        """Анализ распределения намерений"""
        if not self.service_history:
            return {}

        intent_counts = {}
        for entry in self.service_history:
            intent = entry["intent"]
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        return intent_counts

    def explain_last_service(self) -> str:
        """Объяснение последнего обслуживания"""
        if not self.service_history:
            return "История обслуживания пуста"

        last = self.service_history[-1]

        explanation = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ОБЪЯСНЕНИЕ РАБОТЫ ИНФОБРОКЕРА                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Запрос: {last['query']}
Время: {last['timestamp']}

┌──────────────────────────────────────────────────────────────────────────────┐
│  АНАЛИЗ ЗАПРОСА                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
  Определённое намерение: {last['intent']}
  Выбранный маршрут: {last['route']}
  Время доставки: {last['delivery_time_ms']:.2f} ms
  Уверенность: {last['confidence']:.2f}

┌──────────────────────────────────────────────────────────────────────────────┐
│  ПРИНЯТЫЕ РЕШЕНИЯ                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
"""
        for i, decision in enumerate(last['decisions'], 1):
            if isinstance(decision, dict) and 'decision_type' in decision:
                explanation += f"\n  {i}. {decision['decision_type'].upper()}\n"
                explanation += f"     Действие: {decision['action']}\n"
                explanation += f"     Обоснование: {decision['reasoning']}\n"
                explanation += f"     Уверенность: {decision['confidence']:.2f}\n"

        explanation += "\n"
        return explanation


# ═══════════════════════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ДЕМОНСТРАЦИЯ ИНФОБРОКЕРА")
    print("="*80 + "\n")

    broker = InfoBroker(knowledge_base_path="афоризмы")

    print("\n" + "─"*80)
    print("  ТЕСТ 1: Запрос формулы (критическая срочность)")
    print("─"*80)

    package1 = broker.serve(
        query="Какая формула для 5G сетей?",
        intent=QueryIntent.GET_FORMULA,
        urgency="critical"
    )

    print(f"\n📦 Пакет доставлен:")
    print(f"   Содержимое: {package1.content}")
    print(f"   Уверенность: {package1.confidence}")
    print(f"   Маршрут: {package1.route_taken}")
    print(f"   Рекомендации:")
    for rec in package1.recommendations:
        print(f"     • {rec}")

    print("\n" + "─"*80)
    print("  ТЕСТ 2: Решение проблемы (нормальная срочность)")
    print("─"*80)

    package2 = broker.serve(
        query="Как защититься от DDoS атак в IoT?",
        intent=QueryIntent.SOLVE_PROBLEM,
        urgency="normal"
    )

    print(f"\n📦 Пакет доставлен:")
    print(f"   Время: {package2.delivery_time_ms:.2f} ms")
    print(f"   Источники: {', '.join(package2.sources)}")

    print("\n" + "─"*80)
    print("  ТЕСТ 3: Автоопределение намерения")
    print("─"*80)

    package3 = broker.serve(
        query="Покажи примеры blockchain приложений",
        urgency="low"  # Не критично, можем искать глубже
    )

    print(f"\n📦 Пакет доставлен:")
    print(f"   Маршрут: {package3.route_taken}")
    print(f"   Рекомендации: {len(package3.recommendations)}")

    print("\n" + "="*80)
    print("  СТАТИСТИКА ИНФОБРОКЕРА")
    print("="*80)

    stats = broker.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n" + "="*80)
    print("  ОБЪЯСНЕНИЕ ПОСЛЕДНЕГО ОБСЛУЖИВАНИЯ")
    print("="*80)

    explanation = broker.explain_last_service()
    print(explanation)

    print("\n✓ Демонстрация завершена!")
    print(f"  Обслужено запросов: {broker.broker_stats['requests_served']}")
    print(f"  Средняя удовлетворённость: {broker.broker_stats['customer_satisfaction']:.2f}")
    print(f"  Среднее время доставки: {broker.broker_stats['avg_delivery_time_ms']:.2f} ms")
