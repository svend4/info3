#!/usr/bin/env python3
"""
Модуль для работы с 4-уровневой системой познания

Этот модуль предоставляет классы и функции для загрузки, обработки и анализа
знаний, представленных в 4-уровневой системе (Формула → Архетип → Алгоритм → Теорема).

Использование:
    from knowledge_system import KnowledgeSystem

    # Загрузка из JSON
    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Получение информации
    formula = ks.get_formula()
    theorem = ks.get_theorem()

    # Поиск примеров
    examples = ks.find_examples('ChatGPT')
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Formula:
    """Уровень 1: Формула — самое общее, абстрактное"""

    expression: str
    variables: Dict[str, str]
    description: Optional[str] = None

    def __str__(self) -> str:
        return f"Формула: {self.expression}"

    def explain(self) -> str:
        """Объяснение формулы с расшифровкой переменных"""
        lines = [self.expression, "\nгде:"]
        for var, meaning in self.variables.items():
            lines.append(f"  {var} = {meaning}")
        return "\n".join(lines)


@dataclass
class Archetype:
    """Уровень 2: Архетип — расширенная формула, детальная"""

    components: Dict[str, Any]
    extended_formula: Optional[str] = None

    def get_component(self, name: str) -> Optional[Dict]:
        """Получить компонент по имени"""
        return self.components.get(name)

    def list_components(self) -> List[str]:
        """Список всех компонентов"""
        return list(self.components.keys())


@dataclass
class Algorithm:
    """Уровень 3: Алгоритм — пошаговый процесс"""

    steps: List[Dict[str, Any]]
    pipeline_name: Optional[str] = None

    def get_step(self, step_number: int) -> Optional[Dict]:
        """Получить шаг по номеру"""
        for step in self.steps:
            if step.get('step') == step_number:
                return step
        return None

    def total_steps(self) -> int:
        """Общее количество шагов"""
        return len(self.steps)

    def step_names(self) -> List[str]:
        """Список названий всех шагов"""
        return [step.get('name', f"Шаг {step.get('step')}") for step in self.steps]


@dataclass
class Theorem:
    """Уровень 4: Теорема — конкретное, житейское (примеры, афоризмы)"""

    main_theorem: str
    context: Dict[str, Any]
    key_insights: List[Dict[str, Any]]
    real_world_examples: List[Dict[str, Any]]
    practical_advice: List[str]
    related_aphorisms: Optional[List[str]] = None

    def get_example(self, name: str) -> Optional[Dict]:
        """Найти пример по имени"""
        for example in self.real_world_examples:
            if name.lower() in example.get('name', '').lower():
                return example
        return None

    def get_insight(self, keyword: str) -> List[Dict]:
        """Найти insights по ключевому слову"""
        results = []
        for insight in self.key_insights:
            insight_str = json.dumps(insight, ensure_ascii=False).lower()
            if keyword.lower() in insight_str:
                results.append(insight)
        return results


class KnowledgeSystem:
    """
    Главный класс для работы с 4-уровневой системой познания

    Attributes:
        metadata: Метаданные (тема, название, язык, дата)
        formula: Уровень 1 - Формула
        archetype: Уровень 2 - Архетип
        algorithm: Уровень 3 - Алгоритм
        theorem: Уровень 4 - Теорема
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Инициализация системы из словаря данных

        Args:
            data: Словарь с данными всех уровней
        """
        self.metadata = data.get('metadata', {})
        self._raw_data = data

        # Парсинг уровня 1: Формула
        level1 = data.get('level_1_formula', {})
        primary = level1.get('primary_formula', {})
        self.formula = Formula(
            expression=primary.get('expression', ''),
            variables=primary.get('variables', {}),
            description=level1.get('description')
        )

        # Альтернативная формула (если есть)
        self.alternative_formula = None
        if 'alternative_formula' in level1:
            alt = level1['alternative_formula']
            self.alternative_formula = Formula(
                expression=alt.get('expression', ''),
                variables=alt.get('variables', {}),
                description=alt.get('goal')
            )

        # Парсинг уровня 2: Архетип
        level2 = data.get('level_2_archetype', {})
        self.archetype = Archetype(
            components=level2.get('components', {}),
            extended_formula=level2.get('extended_formula')
        )

        # Парсинг уровня 3: Алгоритм
        level3 = data.get('level_3_algorithm', {})
        self.algorithm = Algorithm(
            steps=level3.get('steps', []),
            pipeline_name=level3.get('pipeline_name')
        )

        # Парсинг уровня 4: Теорема
        level4 = data.get('level_4_theorem', {})
        self.theorem = Theorem(
            main_theorem=level4.get('main_theorem', ''),
            context=level4.get('context', {}),
            key_insights=level4.get('key_insights', []),
            real_world_examples=level4.get('real_world_examples', []),
            practical_advice=level4.get('practical_advice', []),
            related_aphorisms=level4.get('related_aphorisms')
        )

    @classmethod
    def from_json(cls, filepath: str) -> 'KnowledgeSystem':
        """
        Загрузка из JSON файла

        Args:
            filepath: Путь к JSON файлу

        Returns:
            Экземпляр KnowledgeSystem
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)

    @classmethod
    def from_yaml(cls, filepath: str) -> 'KnowledgeSystem':
        """
        Загрузка из YAML файла

        Args:
            filepath: Путь к YAML файлу

        Returns:
            Экземпляр KnowledgeSystem
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(data)

    def get_topic(self) -> str:
        """Получить тему"""
        return self.metadata.get('topic', 'Unknown')

    def get_title(self) -> str:
        """Получить название"""
        return self.metadata.get('title', 'Unknown')

    def get_formula(self) -> Formula:
        """Получить формулу (уровень 1)"""
        return self.formula

    def get_archetype(self) -> Archetype:
        """Получить архетип (уровень 2)"""
        return self.archetype

    def get_algorithm(self) -> Algorithm:
        """Получить алгоритм (уровень 3)"""
        return self.algorithm

    def get_theorem(self) -> Theorem:
        """Получить теорему (уровень 4)"""
        return self.theorem

    def search(self, keyword: str) -> Dict[str, List[Any]]:
        """
        Поиск по всей системе знаний

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            Словарь с результатами по уровням
        """
        results = {
            'formula': [],
            'archetype': [],
            'algorithm': [],
            'theorem': []
        }

        keyword_lower = keyword.lower()

        # Поиск в формуле
        if keyword_lower in self.formula.expression.lower():
            results['formula'].append(self.formula.expression)
        for var, meaning in self.formula.variables.items():
            if keyword_lower in var.lower() or keyword_lower in meaning.lower():
                results['formula'].append(f"{var}: {meaning}")

        # Поиск в архетипе
        for comp_name, comp_data in self.archetype.components.items():
            comp_str = json.dumps(comp_data, ensure_ascii=False).lower()
            if keyword_lower in comp_str:
                results['archetype'].append(comp_name)

        # Поиск в алгоритме
        for step in self.algorithm.steps:
            step_str = json.dumps(step, ensure_ascii=False).lower()
            if keyword_lower in step_str:
                results['algorithm'].append(step.get('name', f"Step {step.get('step')}"))

        # Поиск в теореме
        if keyword_lower in self.theorem.main_theorem.lower():
            results['theorem'].append(self.theorem.main_theorem)

        for example in self.theorem.real_world_examples:
            example_str = json.dumps(example, ensure_ascii=False).lower()
            if keyword_lower in example_str:
                results['theorem'].append(example.get('name', 'Unknown example'))

        return results

    def find_examples(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Найти реальные примеры по ключевому слову

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            Список найденных примеров
        """
        results = []
        keyword_lower = keyword.lower()

        for example in self.theorem.real_world_examples:
            example_str = json.dumps(example, ensure_ascii=False).lower()
            if keyword_lower in example_str:
                results.append(example)

        return results

    def get_practical_advice(self) -> List[str]:
        """Получить практические советы"""
        return self.theorem.practical_advice

    def get_aphorisms(self) -> List[str]:
        """Получить связанные афоризмы"""
        return self.theorem.related_aphorisms or []

    def to_summary(self) -> str:
        """
        Краткое резюме всей системы знаний

        Returns:
            Текстовое резюме
        """
        lines = [
            "=" * 80,
            f"ТЕМА: {self.get_title()}",
            "=" * 80,
            "",
            f"[1] ФОРМУЛА: {self.formula.expression}",
            "",
            f"[2] АРХЕТИП: {len(self.archetype.list_components())} компонентов",
            f"    Компоненты: {', '.join(self.archetype.list_components()[:5])}...",
            "",
            f"[3] АЛГОРИТМ: {self.algorithm.total_steps()} шагов",
            f"    Pipeline: {self.algorithm.pipeline_name or 'N/A'}",
            "",
            f"[4] ТЕОРЕМА: {self.theorem.main_theorem}",
            f"    Примеров: {len(self.theorem.real_world_examples)}",
            f"    Советов: {len(self.theorem.practical_advice)}",
            "",
            "=" * 80
        ]
        return "\n".join(lines)

    def export_to_dict(self) -> Dict[str, Any]:
        """Экспорт обратно в словарь"""
        return self._raw_data

    def export_to_json(self, filepath: str, indent: int = 2):
        """
        Экспорт в JSON файл

        Args:
            filepath: Путь для сохранения
            indent: Отступ для форматирования
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._raw_data, f, ensure_ascii=False, indent=indent)

    def export_to_yaml(self, filepath: str):
        """
        Экспорт в YAML файл

        Args:
            filepath: Путь для сохранения
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(self._raw_data, f, allow_unicode=True, default_flow_style=False)


# Вспомогательные функции для AI/ML обработки

def compare_knowledge_systems(ks1: KnowledgeSystem, ks2: KnowledgeSystem) -> Dict[str, Any]:
    """
    Сравнение двух систем знаний

    Args:
        ks1: Первая система
        ks2: Вторая система

    Returns:
        Словарь с результатами сравнения
    """
    return {
        'topics': {
            'topic1': ks1.get_topic(),
            'topic2': ks2.get_topic()
        },
        'formulas': {
            'formula1': ks1.formula.expression,
            'formula2': ks2.formula.expression,
            'same': ks1.formula.expression == ks2.formula.expression
        },
        'complexity': {
            'ks1_components': len(ks1.archetype.list_components()),
            'ks2_components': len(ks2.archetype.list_components()),
            'ks1_steps': ks1.algorithm.total_steps(),
            'ks2_steps': ks2.algorithm.total_steps(),
            'ks1_examples': len(ks1.theorem.real_world_examples),
            'ks2_examples': len(ks2.theorem.real_world_examples)
        }
    }


def extract_keywords(ks: KnowledgeSystem, top_n: int = 10) -> List[str]:
    """
    Извлечение ключевых слов из системы знаний

    Args:
        ks: Система знаний
        top_n: Количество топ-слов

    Returns:
        Список ключевых слов
    """
    from collections import Counter
    import re

    # Собираем весь текст
    text = json.dumps(ks.export_to_dict(), ensure_ascii=False)

    # Простая токенизация (для русского языка лучше использовать специальные библиотеки)
    words = re.findall(r'\b[а-яА-ЯёЁa-zA-Z]{4,}\b', text.lower())

    # Подсчёт частоты
    counter = Counter(words)

    # Фильтрация стоп-слов (упрощённый список)
    stop_words = {'это', 'быть', 'для', 'как', 'или', 'что', 'если', 'при', 'все', 'этот'}
    filtered = [(word, count) for word, count in counter.items() if word not in stop_words]

    # Топ N слов
    top_words = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_n]

    return [word for word, _ in top_words]


def generate_training_data(ks: KnowledgeSystem) -> List[Dict[str, str]]:
    """
    Генерация тренировочных данных для обучения нейросети

    Создаёт пары вопрос-ответ из системы знаний

    Args:
        ks: Система знаний

    Returns:
        Список словарей с парами question-answer
    """
    training_data = []

    # Вопросы про формулу
    training_data.append({
        'question': f"Какая основная формула для темы '{ks.get_topic()}'?",
        'answer': ks.formula.explain(),
        'level': 1,
        'type': 'formula'
    })

    # Вопросы про теорему
    training_data.append({
        'question': f"Какая главная теорема или афоризм для темы '{ks.get_topic()}'?",
        'answer': ks.theorem.main_theorem,
        'level': 4,
        'type': 'theorem'
    })

    # Вопросы про примеры
    for example in ks.theorem.real_world_examples:
        training_data.append({
            'question': f"Расскажи про пример '{example.get('name')}' в контексте {ks.get_topic()}",
            'answer': json.dumps(example, ensure_ascii=False, indent=2),
            'level': 4,
            'type': 'example'
        })

    # Вопросы про шаги алгоритма
    for i, step in enumerate(ks.algorithm.steps, 1):
        training_data.append({
            'question': f"Что такое шаг {i} в алгоритме {ks.algorithm.pipeline_name or ks.get_topic()}?",
            'answer': step.get('name', 'Unknown'),
            'level': 3,
            'type': 'algorithm_step'
        })

    # Вопросы про практические советы
    training_data.append({
        'question': f"Какие практические советы для работы с {ks.get_topic()}?",
        'answer': '\n'.join([f"- {advice}" for advice in ks.get_practical_advice()]),
        'level': 4,
        'type': 'advice'
    })

    return training_data


if __name__ == '__main__':
    # Пример использования
    print("Модуль knowledge_system.py")
    print("Для использования импортируйте классы:")
    print("  from knowledge_system import KnowledgeSystem")
    print("\nСм. demo.py для примеров использования")
