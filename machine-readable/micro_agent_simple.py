#!/usr/bin/env python3
"""
МИКРО-АГЕНТ УРОВЕНЬ 1: Простейший посредник

Минималистичная реализация "информационного курьера" между AI и базой знаний.
Без зависимостей, только стандартная библиотека Python.

Концепция: Агент принимает запрос, делает простые решения, возвращает релевантный контекст
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib


class MicroAgent:
    """Простейший автономный агент для работы с базой знаний"""

    def __init__(self, knowledge_base_path: str = "."):
        self.kb_path = Path(knowledge_base_path)
        self.cache = {}  # Простой in-memory кэш
        self.decision_log = []  # Лог принятых решений
        self.stats = {
            "queries": 0,
            "cache_hits": 0,
            "decisions_made": 0
        }

    def load_knowledge_base(self, filename: str) -> Dict:
        """Загрузка базы знаний из JSON"""
        path = self.kb_path / filename
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Главный метод: обработка запроса с автономными решениями

        Args:
            question: Вопрос пользователя
            top_k: Количество результатов

        Returns:
            Словарь с результатами и метаданными решений
        """
        self.stats["queries"] += 1
        start_time = datetime.now()

        # РЕШЕНИЕ 1: Проверить кэш
        cache_key = self._hash(question)
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            self._log_decision("cache_hit", "Найдено в кэше")
            return {
                "source": "cache",
                "results": self.cache[cache_key],
                "decisions": self.decision_log[-1:],
                "stats": self.stats
            }

        # РЕШЕНИЕ 2: Определить тип запроса
        query_type = self._analyze_query_type(question)
        self._log_decision("query_analysis", f"Тип запроса: {query_type}")

        # РЕШЕНИЕ 3: Определить целевой уровень
        target_levels = self._decide_target_levels(question, query_type)
        self._log_decision("level_selection", f"Целевые уровни: {target_levels}")

        # РЕШЕНИЕ 4: Загрузить релевантные базы знаний
        knowledge_files = self._list_knowledge_files()
        self._log_decision("file_scan", f"Найдено {len(knowledge_files)} файлов знаний")

        # РЕШЕНИЕ 5: Поиск по всем базам
        all_results = []
        for kb_file in knowledge_files:
            kb = self.load_knowledge_base(kb_file)
            results = self._search_in_knowledge_base(kb, question, target_levels)
            all_results.extend(results)

        # РЕШЕНИЕ 6: Ранжирование результатов
        ranked_results = self._rank_results(all_results, question)
        self._log_decision("ranking", f"Найдено {len(ranked_results)} результатов")

        # РЕШЕНИЕ 7: Оценить качество результатов
        confidence = self._assess_confidence(ranked_results)
        self._log_decision("confidence", f"Уверенность: {confidence:.2f}")

        # РЕШЕНИЕ 8: Выбрать стратегию ответа
        strategy = self._decide_response_strategy(confidence, ranked_results)
        self._log_decision("strategy", f"Стратегия: {strategy}")

        # РЕШЕНИЕ 9: Кэшировать если результат хороший
        top_results = ranked_results[:top_k]
        if confidence > 0.6:
            self.cache[cache_key] = top_results
            self._log_decision("caching", "Результат закэширован")

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return {
            "source": "knowledge_base",
            "query_type": query_type,
            "target_levels": target_levels,
            "results": top_results,
            "confidence": confidence,
            "strategy": strategy,
            "decisions": self.decision_log[-9:],  # Последние 9 решений
            "stats": self.stats,
            "elapsed_ms": elapsed
        }

    def _analyze_query_type(self, question: str) -> str:
        """
        АВТОНОМНОЕ РЕШЕНИЕ: Определение типа запроса

        Типы:
        - formula: запрос про формулы, математику
        - example: запрос про примеры, кейсы
        - algorithm: запрос про алгоритм, процесс
        - concept: запрос про концепцию, объяснение
        - advice: запрос про совет, рекомендацию
        """
        q_lower = question.lower()

        # Паттерны для разных типов
        patterns = {
            "formula": [r"формул", r"уравнен", r"математ", r"выраж", r"^\s*[a-z]\s*="],
            "example": [r"пример", r"случай", r"кейс", r"история", r"ситуац"],
            "algorithm": [r"алгоритм", r"процесс", r"шаг", r"как\s+(сделать|работ)", r"процедур"],
            "advice": [r"совет", r"рекоменд", r"как\s+лучше", r"стоит\s+ли", r"что\s+делать"],
            "concept": [r"что\s+так", r"объясни", r"расскажи", r"понятие", r"определение"]
        }

        # Подсчёт совпадений
        scores = {}
        for qtype, pattern_list in patterns.items():
            score = sum(1 for pattern in pattern_list if re.search(pattern, q_lower))
            if score > 0:
                scores[qtype] = score

        if not scores:
            return "general"

        # Вернуть тип с наибольшим score
        return max(scores.items(), key=lambda x: x[1])[0]

    def _decide_target_levels(self, question: str, query_type: str) -> List[int]:
        """
        АВТОНОМНОЕ РЕШЕНИЕ: Определение целевых уровней

        Уровень 1: Формулы
        Уровень 2: Архетипы
        Уровень 3: Алгоритмы
        Уровень 4: Теоремы/Примеры
        """
        # Маппинг тип запроса → уровни
        type_to_levels = {
            "formula": [1, 2],  # Формулы + Архетипы
            "example": [4, 3],  # Примеры + Алгоритмы
            "algorithm": [3, 2],  # Алгоритмы + Архетипы
            "advice": [4, 3],  # Примеры + Алгоритмы
            "concept": [2, 1, 4],  # Архетипы + Формулы + Примеры
            "general": [1, 2, 3, 4]  # Все уровни
        }

        return type_to_levels.get(query_type, [1, 2, 3, 4])

    def _list_knowledge_files(self) -> List[str]:
        """Найти все JSON файлы с базами знаний"""
        json_files = []
        for path in self.kb_path.glob("*.json"):
            if path.stem != "package":  # Исключить package.json etc
                json_files.append(path.name)
        return json_files

    def _search_in_knowledge_base(self, kb: Dict, question: str, target_levels: List[int]) -> List[Dict]:
        """Простой keyword-based поиск в базе знаний"""
        if not kb:
            return []

        results = []
        q_lower = question.lower()
        keywords = set(re.findall(r'\w+', q_lower))

        # Извлечь topic
        topic = kb.get('metadata', {}).get('topic', 'unknown')

        # Поиск по уровням
        for level_num in target_levels:
            level_key = f"level_{level_num}_"

            if level_num == 1:
                # Формулы
                formula = kb.get('level_1_formula', {})
                if self._matches_keywords(formula, keywords):
                    results.append({
                        "level": 1,
                        "topic": topic,
                        "type": "formula",
                        "content": str(formula.get('primary_formula', {})),
                        "score": self._calculate_score(formula, keywords)
                    })

            elif level_num == 2:
                # Архетипы
                archetype = kb.get('level_2_archetype', {})
                components = archetype.get('components', {})
                for comp_name, comp_data in components.items():
                    if self._matches_keywords(comp_data, keywords):
                        results.append({
                            "level": 2,
                            "topic": topic,
                            "type": "archetype_component",
                            "component": comp_name,
                            "content": json.dumps(comp_data, ensure_ascii=False)[:500],
                            "score": self._calculate_score(comp_data, keywords)
                        })

            elif level_num == 3:
                # Алгоритмы
                algorithm = kb.get('level_3_algorithm', {})
                steps = algorithm.get('steps', [])
                for step in steps:
                    if self._matches_keywords(step, keywords):
                        results.append({
                            "level": 3,
                            "topic": topic,
                            "type": "algorithm_step",
                            "step": step.get('step', '?'),
                            "content": step.get('name', '') + ": " + json.dumps(step, ensure_ascii=False)[:500],
                            "score": self._calculate_score(step, keywords)
                        })

            elif level_num == 4:
                # Теоремы и примеры
                theorem = kb.get('level_4_theorem', {})
                examples = theorem.get('real_world_examples', [])
                for example in examples:
                    if self._matches_keywords(example, keywords):
                        results.append({
                            "level": 4,
                            "topic": topic,
                            "type": "example",
                            "name": example.get('name', ''),
                            "content": example.get('lesson', '') + " | " + json.dumps(example, ensure_ascii=False)[:500],
                            "score": self._calculate_score(example, keywords)
                        })

        return results

    def _matches_keywords(self, data: Any, keywords: set) -> bool:
        """Проверка, содержит ли data хотя бы одно ключевое слово"""
        data_str = json.dumps(data, ensure_ascii=False).lower()
        data_words = set(re.findall(r'\w+', data_str))
        return bool(keywords & data_words)

    def _calculate_score(self, data: Any, keywords: set) -> float:
        """Простой scoring: количество совпадающих слов"""
        data_str = json.dumps(data, ensure_ascii=False).lower()
        data_words = set(re.findall(r'\w+', data_str))
        matches = len(keywords & data_words)
        return matches / max(len(keywords), 1)

    def _rank_results(self, results: List[Dict], question: str) -> List[Dict]:
        """Ранжирование результатов по score"""
        return sorted(results, key=lambda x: x.get('score', 0), reverse=True)

    def _assess_confidence(self, results: List[Dict]) -> float:
        """
        АВТОНОМНОЕ РЕШЕНИЕ: Оценка уверенности в результатах

        Возвращает число от 0 до 1
        """
        if not results:
            return 0.0

        # Метрики уверенности
        top_score = results[0].get('score', 0)
        num_results = len(results)
        score_variance = self._calculate_variance([r.get('score', 0) for r in results[:5]])

        # Уверенность выше если:
        # - Высокий top score
        # - Много результатов (но не слишком много)
        # - Низкая дисперсия scores (явный победитель)

        confidence = 0.0
        confidence += top_score * 0.5  # 50% от top score
        confidence += min(num_results / 10, 0.3)  # до 30% за количество
        confidence += (1 - score_variance) * 0.2  # до 20% за low variance

        return min(confidence, 1.0)

    def _calculate_variance(self, scores: List[float]) -> float:
        """Вычислить дисперсию scores"""
        if not scores:
            return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance

    def _decide_response_strategy(self, confidence: float, results: List[Dict]) -> str:
        """
        АВТОНОМНОЕ РЕШЕНИЕ: Выбор стратегии ответа

        Стратегии:
        - direct: высокая уверенность, вернуть топ-1
        - ranked_list: средняя уверенность, вернуть топ-N
        - expand_search: низкая уверенность, нужно расширить поиск
        - ask_clarification: очень низкая уверенность, спросить пользователя
        """
        if confidence > 0.85:
            return "direct"  # Один чёткий ответ
        elif confidence > 0.6:
            return "ranked_list"  # Список вариантов
        elif confidence > 0.3:
            return "expand_search"  # Расширить поиск
        else:
            return "ask_clarification"  # Нужны уточнения

    def _hash(self, text: str) -> str:
        """Хэш для кэширования"""
        return hashlib.md5(text.encode()).hexdigest()

    def _log_decision(self, decision_type: str, description: str):
        """Логирование принятого решения"""
        self.stats["decisions_made"] += 1
        self.decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": decision_type,
            "description": description
        })

    def explain_decisions(self) -> str:
        """Объяснение принятых решений (для прозрачности)"""
        if not self.decision_log:
            return "Решения пока не принимались"

        explanation = "🤖 АВТОНОМНЫЕ РЕШЕНИЯ АГЕНТА:\n\n"
        for i, decision in enumerate(self.decision_log, 1):
            explanation += f"{i}. [{decision['type']}] {decision['description']}\n"

        explanation += f"\n📊 СТАТИСТИКА:\n"
        explanation += f"  Всего запросов: {self.stats['queries']}\n"
        explanation += f"  Попаданий в кэш: {self.stats['cache_hits']}\n"
        explanation += f"  Решений принято: {self.stats['decisions_made']}\n"

        return explanation


def demo_simple_agent():
    """Демонстрация работы простого агента"""
    print("=" * 80)
    print("ДЕМО: Простой Микро-Агент (Уровень 1)")
    print("=" * 80)
    print()

    # Создать агента
    agent = MicroAgent(knowledge_base_path=".")

    # Тестовые запросы
    test_queries = [
        "Что такое overfitting в машинном обучении?",
        "Покажи формулу для блокчейна",
        "Приведи пример атаки на кибербезопасность",
        "Как работает алгоритм квантовых вычислений?",
        "Дай совет по облачным вычислениям"
    ]

    for query in test_queries:
        print(f"\n{'─' * 80}")
        print(f"❓ ЗАПРОС: {query}")
        print(f"{'─' * 80}\n")

        # Выполнить запрос
        response = agent.query(query, top_k=3)

        # Вывод результатов
        print(f"📊 Тип запроса: {response['query_type']}")
        print(f"🎯 Целевые уровни: {response['target_levels']}")
        print(f"💯 Уверенность: {response['confidence']:.2%}")
        print(f"🚀 Стратегия: {response['strategy']}")
        print(f"⏱️  Время: {response['elapsed_ms']:.1f}ms")
        print(f"📁 Источник: {response['source']}")

        print(f"\n🔍 РЕЗУЛЬТАТЫ (топ-{len(response['results'])}):\n")
        for i, result in enumerate(response['results'], 1):
            print(f"  {i}. [Уровень {result['level']}] {result['topic']}")
            print(f"     Тип: {result['type']}")
            print(f"     Score: {result['score']:.3f}")
            print(f"     Контент: {result['content'][:200]}...")
            print()

        print("🤖 ПРИНЯТЫЕ РЕШЕНИЯ:")
        for decision in response['decisions']:
            print(f"  • [{decision['type']}] {decision['description']}")

        print(f"\n{'─' * 80}\n")

    # Итоговая статистика
    print("\n" + "=" * 80)
    print("📈 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print(agent.explain_decisions())


if __name__ == '__main__':
    demo_simple_agent()
