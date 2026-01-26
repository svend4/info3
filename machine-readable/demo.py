#!/usr/bin/env python3
"""
Демонстрация использования модуля knowledge_system

Этот скрипт показывает различные способы работы с 4-уровневой системой познания
для машинной обработки, AI и программной реализации.
"""

import json
from knowledge_system import (
    KnowledgeSystem,
    compare_knowledge_systems,
    extract_keywords,
    generate_training_data
)


def demo_basic_usage():
    """Базовое использование: загрузка и просмотр данных"""
    print("=" * 80)
    print("ДЕМО 1: Базовое использование")
    print("=" * 80)

    # Загрузка из JSON
    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Получение базовой информации
    print(f"\nТема: {ks.get_topic()}")
    print(f"Название: {ks.get_title()}")

    # Просмотр формулы
    print("\n[УРОВЕНЬ 1] Формула:")
    print(ks.get_formula().explain())

    # Альтернативная формула
    if ks.alternative_formula:
        print("\nАльтернативная формула:")
        print(ks.alternative_formula.explain())

    # Просмотр теоремы
    print("\n[УРОВЕНЬ 4] Главная теорема:")
    print(f"  {ks.get_theorem().main_theorem}")

    print("\n" + "=" * 80 + "\n")


def demo_search_and_query():
    """Поиск и запросы по данным"""
    print("=" * 80)
    print("ДЕМО 2: Поиск и запросы")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Поиск по ключевому слову
    keyword = "ChatGPT"
    print(f"\nПоиск '{keyword}' по всей системе:")
    results = ks.search(keyword)

    for level, items in results.items():
        if items:
            print(f"\n  {level.upper()}:")
            for item in items:
                print(f"    - {item}")

    # Поиск конкретных примеров
    print(f"\n\nПримеры с '{keyword}':")
    examples = ks.find_examples(keyword)
    for ex in examples:
        print(f"\n  Пример: {ex.get('name')}")
        print(f"  Урок: {ex.get('lesson', 'N/A')}")

    # Получение компонентов архетипа
    print("\n\nКомпоненты архетипа:")
    archetype = ks.get_archetype()
    for comp_name in archetype.list_components():
        print(f"  - {comp_name}")

    # Детали конкретного компонента
    print("\n\nДетали компонента 'challenges':")
    challenges = archetype.get_component('challenges')
    if challenges:
        for challenge_name, challenge_data in challenges.items():
            print(f"\n  {challenge_name}:")
            print(f"    Название: {challenge_data.get('name')}")
            print(f"    Описание: {challenge_data.get('description', challenge_data.get('danger', 'N/A'))}")

    print("\n" + "=" * 80 + "\n")


def demo_algorithm_processing():
    """Работа с алгоритмом (уровень 3)"""
    print("=" * 80)
    print("ДЕМО 3: Обработка алгоритма")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')
    algorithm = ks.get_algorithm()

    print(f"\nПайплайн: {algorithm.pipeline_name}")
    print(f"Всего шагов: {algorithm.total_steps()}")

    # Список всех шагов
    print("\nШаги:")
    for i, step_name in enumerate(algorithm.step_names(), 1):
        print(f"  {i}. {step_name}")

    # Детали конкретного шага
    step_num = 4
    print(f"\n\nДетали шага {step_num}:")
    step = algorithm.get_step(step_num)
    if step:
        print(f"  Название: {step.get('name')}")
        print(f"  Действия:")
        for action in step.get('actions', []):
            if isinstance(action, dict):
                print(f"    - Фаза: {action.get('phase', action.get('action', 'N/A'))}")

    # Извлечение всех названий шагов для ML-модели
    print("\n\nДанные для ML (названия шагов в JSON):")
    step_data = {
        'pipeline': algorithm.pipeline_name,
        'total_steps': algorithm.total_steps(),
        'steps': [
            {'step_number': i, 'step_name': name}
            for i, name in enumerate(algorithm.step_names(), 1)
        ]
    }
    print(json.dumps(step_data, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80 + "\n")


def demo_practical_advice():
    """Извлечение практических советов"""
    print("=" * 80)
    print("ДЕМО 4: Практические советы и афоризмы")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Практические советы
    print("\nПрактические советы:")
    for i, advice in enumerate(ks.get_practical_advice(), 1):
        print(f"  {i}. {advice}")

    # Афоризмы
    print("\n\nСвязанные афоризмы:")
    for i, aphorism in enumerate(ks.get_aphorisms(), 1):
        print(f"  {i}. {aphorism}")

    # Insights
    print("\n\nКлючевые insights:")
    theorem = ks.get_theorem()
    for i, insight in enumerate(theorem.key_insights, 1):
        print(f"\n  {i}. {insight.get('insight')}")
        if 'example' in insight:
            ex = insight['example']
            if isinstance(ex, dict):
                print(f"     Пример: {ex.get('question', ex.get('case', 'N/A'))}")

    print("\n" + "=" * 80 + "\n")


def demo_ai_training_data():
    """Генерация тренировочных данных для нейросети"""
    print("=" * 80)
    print("ДЕМО 5: Генерация данных для обучения AI")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Генерация тренировочных данных
    training_data = generate_training_data(ks)

    print(f"\nСгенерировано {len(training_data)} пар вопрос-ответ")
    print("\nПримеры (первые 3):\n")

    for i, item in enumerate(training_data[:3], 1):
        print(f"Пример {i}:")
        print(f"  Вопрос: {item['question']}")
        print(f"  Ответ: {item['answer'][:200]}{'...' if len(item['answer']) > 200 else ''}")
        print(f"  Уровень: {item['level']}, Тип: {item['type']}")
        print()

    # Сохранение в JSON для использования в ML
    output_file = 'training_data_ai.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)

    print(f"Все данные сохранены в {output_file}")

    # Статистика по типам
    print("\nСтатистика по типам данных:")
    type_counts = {}
    for item in training_data:
        item_type = item['type']
        type_counts[item_type] = type_counts.get(item_type, 0) + 1

    for item_type, count in type_counts.items():
        print(f"  {item_type}: {count}")

    print("\n" + "=" * 80 + "\n")


def demo_keyword_extraction():
    """Извлечение ключевых слов"""
    print("=" * 80)
    print("ДЕМО 6: Извлечение ключевых слов")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Извлечение топ-20 ключевых слов
    keywords = extract_keywords(ks, top_n=20)

    print("\nТоп-20 ключевых слов:")
    for i, keyword in enumerate(keywords, 1):
        print(f"  {i}. {keyword}")

    print("\n\nПрименение: эти ключевые слова можно использовать для:")
    print("  - Индексации в поисковой системе")
    print("  - Тегирования документов")
    print("  - Создания эмбеддингов для semantic search")
    print("  - Кластеризации похожих тем")

    print("\n" + "=" * 80 + "\n")


def demo_yaml_format():
    """Работа с YAML форматом"""
    print("=" * 80)
    print("ДЕМО 7: Работа с YAML форматом")
    print("=" * 80)

    # Загрузка из YAML
    ks_yaml = KnowledgeSystem.from_yaml('искусственный-интеллект.yaml')

    print("\nДанные загружены из YAML файла")
    print(f"Тема: {ks_yaml.get_topic()}")

    # Сравнение с JSON версией
    ks_json = KnowledgeSystem.from_json('искусственный-интеллект.json')

    print("\nСравнение JSON vs YAML:")
    print(f"  Формулы идентичны: {ks_json.formula.expression == ks_yaml.formula.expression}")
    print(f"  Теоремы идентичны: {ks_json.theorem.main_theorem == ks_yaml.theorem.main_theorem}")
    print(f"  Количество шагов: JSON={ks_json.algorithm.total_steps()}, YAML={ks_yaml.algorithm.total_steps()}")

    print("\nВывод: JSON и YAML содержат идентичные данные, ")
    print("        выбор формата зависит от предпочтений:")
    print("        - JSON: лучше для API, JavaScript, строгая структура")
    print("        - YAML: более читаем человеком, меньше символов")

    print("\n" + "=" * 80 + "\n")


def demo_summary():
    """Краткое резюме"""
    print("=" * 80)
    print("ДЕМО 8: Краткое резюме системы")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    # Вывод резюме
    print(ks.to_summary())

    print("\n" + "=" * 80 + "\n")


def demo_use_cases():
    """Примеры использования для различных задач"""
    print("=" * 80)
    print("ДЕМО 9: Примеры использования в реальных задачах")
    print("=" * 80)

    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

    print("\n1. ДЛЯ ЧАТБОТА (Question-Answering system):")
    print("   - Загрузить систему знаний")
    print("   - Индексировать все уровни")
    print("   - На вопрос пользователя искать релевантный контент")

    user_question = "Что такое overfitting?"
    results = ks.search("overfitting")
    print(f"\n   Пользователь: {user_question}")
    print(f"   Бот: Найдено в архетипе:")
    for item in results.get('archetype', []):
        print(f"        {item}")

    print("\n\n2. ДЛЯ SEMANTIC SEARCH:")
    print("   - Извлечь эмбеддинги из каждого уровня")
    print("   - Создать векторную БД (FAISS, Pinecone)")
    print("   - Поиск по косинусному сходству")

    print("\n\n3. ДЛЯ ОБУЧЕНИЯ LLM:")
    training_data = generate_training_data(ks)
    print(f"   - Сгенерировано {len(training_data)} пар вопрос-ответ")
    print("   - Формат для fine-tuning GPT/BERT")
    print("   - Можно использовать для:")
    print("     * Supervised fine-tuning")
    print("     * RLHF (Reinforcement Learning from Human Feedback)")
    print("     * Few-shot learning examples")

    print("\n\n4. ДЛЯ KNOWLEDGE GRAPH:")
    print("   - Формула → связь с переменными")
    print("   - Архетип → связь с компонентами")
    print("   - Теорема → связь с примерами")
    print("   - Создать граф в Neo4j или RDF")

    print("\n\n5. ДЛЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ:")
    print("   - Извлечь ключевые слова из разных тем")
    print("   - Вычислить сходство между темами")
    print("   - Рекомендовать: 'Если интересует X, смотри Y'")

    print("\n" + "=" * 80 + "\n")


def main():
    """Главная функция - запускает все демо"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "ДЕМОНСТРАЦИЯ MACHINE-READABLE ФОРМАТОВ" + " " * 24 + "║")
    print("║" + " " * 20 + "4-уровневая система познания" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    demos = [
        ("Базовое использование", demo_basic_usage),
        ("Поиск и запросы", demo_search_and_query),
        ("Обработка алгоритма", demo_algorithm_processing),
        ("Практические советы", demo_practical_advice),
        ("Генерация данных для AI", demo_ai_training_data),
        ("Извлечение ключевых слов", demo_keyword_extraction),
        ("Работа с YAML", demo_yaml_format),
        ("Резюме системы", demo_summary),
        ("Примеры использования", demo_use_cases),
    ]

    print("Доступные демонстрации:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")

    print("\n" + "=" * 80)
    print("Запуск всех демонстраций...")
    print("=" * 80 + "\n")

    for name, demo_func in demos:
        try:
            demo_func()
            input("Нажмите Enter для продолжения...")
        except FileNotFoundError as e:
            print(f"\nОшибка: {e}")
            print("Убедитесь, что файлы искусственный-интеллект.json и .yaml находятся в той же директории")
            break
        except Exception as e:
            print(f"\nОшибка в демо '{name}': {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 80)
    print("""
Эти машиночитаемые форматы (JSON, YAML, Python модуль) позволяют:

1. ПРОГРАММНАЯ ОБРАБОТКА:
   - Автоматическое извлечение данных
   - Интеграция с существующими системами
   - Создание API для доступа к знаниям

2. ОБУЧЕНИЕ AI/ML МОДЕЛЕЙ:
   - Генерация тренировочных данных
   - Fine-tuning языковых моделей
   - Создание датасетов для supervised learning

3. ПОИСК И ИНДЕКСАЦИЯ:
   - Полнотекстовый поиск
   - Семантический поиск (embeddings)
   - Индексация в поисковых системах

4. ИНТЕГРАЦИЯ:
   - REST API
   - GraphQL
   - Микросервисы
   - Базы данных (SQL, NoSQL, Vector DB)

5. АНАЛИТИКА:
   - Извлечение ключевых слов
   - Кластеризация тем
   - Построение knowledge graphs

Форматы легко расширяемы и совместимы с современными AI/ML инструментами!
    """)
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
