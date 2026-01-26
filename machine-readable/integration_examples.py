#!/usr/bin/env python3
"""
ПРИМЕРЫ ИНТЕГРАЦИИ 4-УРОВНЕВОЙ СИСТЕМЫ С GPT/CLAUDE
==================================================

Демонстрация различных сценариев применения системы в реальных задачах

СЦЕНАРИИ:
1. RAG для обучения AI (AI учится из примеров)
2. Автономный советник (AI дает советы на основе базы знаний)
3. Генератор аналогий (AI находит похожие концепции)
4. Валидатор решений (AI проверяет решения по формулам)
5. Учитель-объяснитель (AI объясняет сложные концепции)
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════
# ПРИМЕР 1: RAG ДЛЯ ОБУЧЕНИЯ AI
# ═══════════════════════════════════════════════════════════════════════════

class AILearningAssistant:
    """
    Помощник для обучения AI на основе 4-уровневой системы

    Концепция: Прежде чем решать задачу, AI смотрит в "учебник"
    """

    def __init__(self, knowledge_system):
        self.ks = knowledge_system
        self.learning_history = []

    def learn_before_solve(self, problem: str) -> Dict:
        """
        Процесс:
        1. Получить проблему
        2. Найти релевантные знания в базе
        3. Изучить формулы, алгоритмы, примеры
        4. Применить к решению
        """

        print(f"\n{'='*70}")
        print(f"  AI ОБУЧАЕТСЯ ПЕРЕД РЕШЕНИЕМ ЗАДАЧИ")
        print(f"{'='*70}")
        print(f"  Задача: {problem}\n")

        # Шаг 1: Поиск релевантных знаний
        print("  [1/4] Поиск релевантных знаний...")
        knowledge = self.ks.query(problem, top_k=3)

        if not knowledge['results']:
            return {
                "success": False,
                "reason": "Нет релевантных знаний в базе"
            }

        print(f"       ✓ Найдено: {len(knowledge['results'])} документов")

        # Шаг 2: Извлечение ключевых концепций
        print("  [2/4] Извлечение ключевых концепций...")
        concepts = self._extract_concepts(knowledge['results'])
        print(f"       ✓ Концепций: {len(concepts)}")

        # Шаг 3: Изучение примеров
        print("  [3/4] Изучение примеров...")
        examples = self._extract_examples(knowledge['results'])
        print(f"       ✓ Примеров: {len(examples)}")

        # Шаг 4: Формирование контекста для AI
        print("  [4/4] Формирование контекста...")
        context = self._build_learning_context(concepts, examples, knowledge)

        # Логирование
        self.learning_history.append({
            "problem": problem,
            "concepts_learned": len(concepts),
            "examples_studied": len(examples),
            "confidence": knowledge['confidence']
        })

        print(f"  \n  ✓ Обучение завершено! Уверенность: {knowledge['confidence']:.2f}")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "context": context,
            "concepts": concepts,
            "examples": examples,
            "confidence": knowledge['confidence'],
            "prompt_for_ai": self._generate_ai_prompt(problem, context)
        }

    def _extract_concepts(self, results: List[Dict]) -> List[str]:
        """Извлечение ключевых концепций"""
        concepts = []
        for result in results:
            # Извлечение из формул и архетипов
            content = result.get('content', '')
            # Простая эвристика: строки с "="
            lines = content.split('\n')
            for line in lines:
                if '=' in line and len(line) < 100:
                    concepts.append(line.strip())

        return concepts[:10]  # Топ-10

    def _extract_examples(self, results: List[Dict]) -> List[str]:
        """Извлечение примеров"""
        examples = []
        for result in results:
            content = result.get('content', '')
            # Поиск секций ПРИМЕР
            import re
            pattern = r'ПРИМЕР \d+:.*?(?=ПРИМЕР \d+:|\n\[|\Z)'
            found = re.findall(pattern, content, re.DOTALL)
            examples.extend([ex[:200] for ex in found])

        return examples[:5]  # Топ-5

    def _build_learning_context(self, concepts: List[str], examples: List[str],
                                knowledge: Dict) -> str:
        """Построение контекста для обучения"""
        context = "=== КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ ===\n\n"

        context += "КЛЮЧЕВЫЕ КОНЦЕПЦИИ:\n"
        for i, concept in enumerate(concepts[:5], 1):
            context += f"{i}. {concept}\n"

        context += "\nПРИМЕРЫ ПРИМЕНЕНИЯ:\n"
        for i, example in enumerate(examples[:3], 1):
            context += f"\nПример {i}:\n{example}\n"

        context += f"\n(Уверенность в данных: {knowledge['confidence']:.0%})"

        return context

    def _generate_ai_prompt(self, problem: str, context: str) -> str:
        """Генерация промпта для AI (GPT/Claude)"""
        return f"""Ты — эксперт, который использует базу структурированных знаний для решения задач.

{context}

ЗАДАЧА:
{problem}

ИНСТРУКЦИЯ:
1. Используй концепции и примеры из контекста выше
2. Примени их к данной задаче
3. Объясни как ты применил знания из базы
4. Дай конкретное решение

Твой ответ:"""


# ═══════════════════════════════════════════════════════════════════════════
# ПРИМЕР 2: АВТОНОМНЫЙ СОВЕТНИК
# ═══════════════════════════════════════════════════════════════════════════

class AutonomousAdvisor:
    """
    Автономный советник на основе 4-уровневой системы

    Концепция: AI дает советы, основанные на практических примерах из базы
    """

    def __init__(self, knowledge_system):
        self.ks = knowledge_system
        self.advice_log = []

    def give_advice(self, situation: str) -> Dict:
        """
        Даёт совет на основе похожих ситуаций из базы знаний
        """

        print(f"\n{'='*70}")
        print(f"  АВТОНОМНЫЙ СОВЕТНИК")
        print(f"{'='*70}")
        print(f"  Ситуация: {situation}\n")

        # Поиск релевантных примеров (уровень 4 - Теоремы)
        results = self.ks.query(situation, top_k=5)

        if not results['results']:
            return {
                "success": False,
                "advice": "К сожалению, в базе знаний нет похожих примеров"
            }

        # Анализ примеров
        lessons_learned = self._analyze_examples(results['results'])

        # Генерация совета
        advice = self._synthesize_advice(situation, lessons_learned)

        # Логирование
        self.advice_log.append({
            "situation": situation,
            "examples_used": len(results['results']),
            "confidence": results['confidence']
        })

        print(f"  ✓ Совет сформирован (на основе {len(results['results'])} примеров)")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "advice": advice,
            "lessons": lessons_learned,
            "confidence": results['confidence'],
            "sources": [r['topic'] for r in results['results']]
        }

    def _analyze_examples(self, results: List[Dict]) -> List[Dict]:
        """Анализ примеров для извлечения уроков"""
        lessons = []

        for result in results:
            content = result.get('content', '')

            # Поиск секции "УРОК:"
            import re
            pattern = r'УРОК:.*?(?=\n\n|ПРИМЕР|\Z)'
            found = re.findall(pattern, content, re.DOTALL)

            for lesson in found:
                lessons.append({
                    "topic": result['topic'],
                    "lesson": lesson.strip()
                })

        return lessons

    def _synthesize_advice(self, situation: str, lessons: List[Dict]) -> str:
        """Синтез совета из уроков"""
        advice = f"На основе анализа {len(lessons)} примеров:\n\n"

        for i, lesson_data in enumerate(lessons[:3], 1):
            advice += f"{i}. {lesson_data['lesson']}\n\n"

        advice += f"\nПРИМЕНИТЕЛЬНО К ВАШЕЙ СИТУАЦИИ:\n"
        advice += f"[Здесь AI (GPT/Claude) должен применить уроки к конкретной ситуации]\n"

        return advice


# ═══════════════════════════════════════════════════════════════════════════
# ПРИМЕР 3: ГЕНЕРАТОР АНАЛОГИЙ
# ═══════════════════════════════════════════════════════════════════════════

class AnalogyGenerator:
    """
    Находит аналогии между концепциями в разных доменах

    Концепция: "5G сети похожи на..." - поиск паттернов в других областях
    """

    def __init__(self, knowledge_system):
        self.ks = knowledge_system

    def find_analogies(self, concept: str, target_domain: Optional[str] = None) -> Dict:
        """
        Поиск аналогий для концепции

        Args:
            concept: Концепция для поиска аналогий
            target_domain: Целевой домен (опционально)
        """

        print(f"\n{'='*70}")
        print(f"  ГЕНЕРАТОР АНАЛОГИЙ")
        print(f"{'='*70}")
        print(f"  Концепция: {concept}")
        print(f"  Целевой домен: {target_domain or 'любой'}\n")

        # Шаг 1: Извлечение ключевых характеристик концепции
        concept_results = self.ks.query(concept, top_k=3)

        if not concept_results['results']:
            return {"success": False, "reason": "Концепция не найдена"}

        characteristics = self._extract_characteristics(concept_results['results'][0])

        print(f"  Характеристики концепции:")
        for char in characteristics[:3]:
            print(f"    • {char}")

        # Шаг 2: Поиск похожих паттернов в других доменах
        print(f"\n  Поиск похожих паттернов...")

        analogies = []

        # Поиск по каждой характеристике
        for char in characteristics[:3]:
            results = self.ks.query(char, top_k=5)

            for result in results['results']:
                # Исключаем тот же домен
                if result['topic'] != concept_results['results'][0]['topic']:
                    analogies.append({
                        "domain": result['topic'],
                        "similarity": result['score'],
                        "characteristic": char
                    })

        # Группировка по доменам
        by_domain = {}
        for analogy in analogies:
            domain = analogy['domain']
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(analogy)

        # Сортировка
        sorted_analogies = sorted(
            by_domain.items(),
            key=lambda x: sum(a['similarity'] for a in x[1]),
            reverse=True
        )

        print(f"  ✓ Найдено аналогий в {len(sorted_analogies)} доменах")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "concept": concept,
            "characteristics": characteristics,
            "analogies": sorted_analogies[:5],  # Топ-5 доменов
            "prompt_for_ai": self._generate_analogy_prompt(concept, sorted_analogies)
        }

    def _extract_characteristics(self, result: Dict) -> List[str]:
        """Извлечение характеристик концепции"""
        content = result.get('content', '')

        # Простая эвристика: строки после "где:", "характеристики:"
        characteristics = []

        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'где:' in line.lower() or 'характеристик' in line.lower():
                # Следующие 5-10 строк
                for j in range(i+1, min(i+10, len(lines))):
                    l = lines[j].strip()
                    if l and len(l) < 100:
                        characteristics.append(l)

        return characteristics[:10]

    def _generate_analogy_prompt(self, concept: str, analogies: List) -> str:
        """Промпт для AI для генерации аналогий"""
        prompt = f"""Ты — эксперт по поиску аналогий между концепциями.

КОНЦЕПЦИЯ: {concept}

ПОХОЖИЕ ПАТТЕРНЫ НАЙДЕНЫ В:
"""

        for domain, items in analogies[:3]:
            prompt += f"\n• {domain}:"
            for item in items[:2]:
                prompt += f"\n  - {item['characteristic']}"

        prompt += f"""

ЗАДАЧА:
Создай яркую, понятную аналогию между "{concept}" и одной из найденных областей.
Объясни сходство так, чтобы было понятно даже неспециалисту.

Твоя аналогия:"""

        return prompt


# ═══════════════════════════════════════════════════════════════════════════
# ПРИМЕР 4: ВАЛИДАТОР РЕШЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════

class SolutionValidator:
    """
    Валидирует решения на основе формул и принципов из базы знаний

    Концепция: "Проверь моё решение по формулам"
    """

    def __init__(self, knowledge_system):
        self.ks = knowledge_system

    def validate(self, problem: str, proposed_solution: str) -> Dict:
        """
        Валидация решения

        Args:
            problem: Описание проблемы
            proposed_solution: Предложенное решение
        """

        print(f"\n{'='*70}")
        print(f"  ВАЛИДАТОР РЕШЕНИЙ")
        print(f"{'='*70}")
        print(f"  Проблема: {problem}")
        print(f"  Решение: {proposed_solution[:50]}...\n")

        # Поиск релевантных формул и принципов
        formulas = self.ks.query(problem + " формула", top_k=3)

        if not formulas['results']:
            return {
                "success": False,
                "reason": "Нет формул для валидации"
            }

        # Извлечение критериев валидации
        criteria = self._extract_validation_criteria(formulas['results'])

        print(f"  Критерии валидации:")
        for i, criterion in enumerate(criteria, 1):
            print(f"    {i}. {criterion[:60]}...")

        # Генерация промпта для AI для проверки
        validation_prompt = self._generate_validation_prompt(
            problem, proposed_solution, criteria
        )

        print(f"\n  ✓ Критерии подготовлены для валидации")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "criteria": criteria,
            "prompt_for_ai": validation_prompt,
            "sources": [r['topic'] for r in formulas['results']]
        }

    def _extract_validation_criteria(self, results: List[Dict]) -> List[str]:
        """Извлечение критериев валидации из формул"""
        criteria = []

        for result in results:
            content = result.get('content', '')

            # Поиск формул
            import re
            # Строки с "="
            lines = content.split('\n')
            for line in lines:
                if '=' in line and len(line) < 150:
                    criteria.append(line.strip())

        return criteria[:5]

    def _generate_validation_prompt(self, problem: str, solution: str,
                                   criteria: List[str]) -> str:
        """Промпт для AI для валидации"""
        prompt = f"""Ты — валидатор решений. Проверь решение на соответствие критериям.

ПРОБЛЕМА:
{problem}

ПРЕДЛОЖЕННОЕ РЕШЕНИЕ:
{solution}

КРИТЕРИИ ИЗ БАЗЫ ЗНАНИЙ:
"""

        for i, criterion in enumerate(criteria, 1):
            prompt += f"{i}. {criterion}\n"

        prompt += """
ЗАДАЧА:
1. Проверь соответствие решения каждому критерию
2. Укажи что верно, что нет
3. Предложи улучшения если нужно

Твоя валидация:"""

        return prompt


# ═══════════════════════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ ВСЕХ СЦЕНАРИЕВ
# ═══════════════════════════════════════════════════════════════════════════

def demo_all_scenarios():
    """Демонстрация всех сценариев интеграции"""

    print("\n" + "="*80)
    print("  ДЕМОНСТРАЦИЯ СЦЕНАРИЕВ ИНТЕГРАЦИИ С GPT/CLAUDE")
    print("="*80)

    # Для демонстрации - используем mock knowledge system
    from pathlib import Path

    class MockKnowledgeSystem:
        def query(self, q, top_k=5):
            return {
                "results": [
                    {
                        "topic": "5g-сети",
                        "content": "Формула: 5G_Performance = (Bandwidth × Latency) / Cost\n\nПРИМЕР 1: Verizon mmWave\nУРОК: mmWave работает только на близких расстояниях",
                        "score": 10
                    },
                    {
                        "topic": "интернет-вещей",
                        "content": "IoT_Value = Sensors × Connectivity\n\nПРИМЕР 2: Nest Thermostat\nУРОК: Простое устройство + умное облако = успех",
                        "score": 8
                    }
                ],
                "confidence": 0.85
            }

    ks = MockKnowledgeSystem()

    # Сценарий 1: Обучение AI
    print("\n" + "─"*80)
    print("  СЦЕНАРИЙ 1: ОБУЧЕНИЕ AI ПЕРЕД РЕШЕНИЕМ ЗАДАЧИ")
    print("─"*80)

    learner = AILearningAssistant(ks)
    result1 = learner.learn_before_solve(
        "Как оптимизировать производительность 5G сети в городе?"
    )

    if result1['success']:
        print("\nПРОМПТ ДЛЯ AI (GPT/CLAUDE):")
        print("─"*80)
        print(result1['prompt_for_ai'])

    # Сценарий 2: Автономный советник
    print("\n" + "─"*80)
    print("  СЦЕНАРИЙ 2: АВТОНОМНЫЙ СОВЕТНИК")
    print("─"*80)

    advisor = AutonomousAdvisor(ks)
    result2 = advisor.give_advice(
        "Моя компания хочет внедрить IoT, но переживаем за безопасность"
    )

    if result2['success']:
        print("\nСОВЕТ:")
        print("─"*80)
        print(result2['advice'])

    # Сценарий 3: Генератор аналогий
    print("\n" + "─"*80)
    print("  СЦЕНАРИЙ 3: ГЕНЕРАТОР АНАЛОГИЙ")
    print("─"*80)

    analogy_gen = AnalogyGenerator(ks)
    result3 = analogy_gen.find_analogies("5G сети")

    if result3['success']:
        print("\nПРОМПТ ДЛЯ AI:")
        print("─"*80)
        print(result3['prompt_for_ai'][:300] + "...")

    # Сценарий 4: Валидатор решений
    print("\n" + "─"*80)
    print("  СЦЕНАРИЙ 4: ВАЛИДАТОР РЕШЕНИЙ")
    print("─"*80)

    validator = SolutionValidator(ks)
    result4 = validator.validate(
        "Нужно улучшить покрытие 5G",
        "Предлагаю установить больше mmWave станций"
    )

    if result4['success']:
        print("\nПРОМПТ ДЛЯ ВАЛИДАЦИИ:")
        print("─"*80)
        print(result4['prompt_for_ai'][:300] + "...")

    print("\n" + "="*80)
    print("  ✓ ВСЕ СЦЕНАРИИ ПРОДЕМОНСТРИРОВАНЫ")
    print("="*80)

    print("""\n
ИТОГО СОЗДАНО 4 СЦЕНАРИЯ ИНТЕГРАЦИИ:

1. 🎓 AI Learning Assistant - обучение перед решением задач
2. 💡 Autonomous Advisor - автономные советы на основе примеров
3. 🔄 Analogy Generator - поиск аналогий между концепциями
4. ✓ Solution Validator - валидация решений по формулам

ПРИМЕНЕНИЕ:
- Используйте эти классы с реальным knowledge_system
- Передавайте сгенерированные промпты в GPT/Claude API
- Получайте ответы обогащённые структурированными знаниями

ПРЕИМУЩЕСТВА:
- AI не "выдумывает" - опирается на проверенные знания
- Прозрачность: видно откуда взята информация
- Консистентность: одинаковые вопросы → одинаковые контексты
- Обучаемость: AI "учится" из примеров перед ответом
    """)


if __name__ == "__main__":
    demo_all_scenarios()
