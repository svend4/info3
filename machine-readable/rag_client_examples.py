#!/usr/bin/env python3
"""
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ RAG API

Демонстрация различных способов взаимодействия с микро-агентом:
1. Прямые запросы через requests
2. Интеграция с LLM (OpenAI-compatible)
3. Batch processing
4. Streaming ответов
5. Автоматическое принятие решений
"""

import requests
import json
from typing import List, Dict, Any
import time


# ============================================================================
# БАЗОВЫЙ КЛИЕНТ
# ============================================================================

class RAGClient:
    """Клиент для работы с RAG API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def query(self, question: str, top_k: int = 5, levels: List[int] = None,
              use_semantic: bool = True, explain: bool = False) -> Dict[str, Any]:
        """Отправить запрос к агенту"""
        response = self.session.post(
            f"{self.base_url}/query",
            json={
                "question": question,
                "top_k": top_k,
                "levels": levels,
                "use_semantic": use_semantic,
                "explain": explain
            }
        )
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        """Проверить здоровье сервиса"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def clear_cache(self):
        """Очистить кэш"""
        response = self.session.post(f"{self.base_url}/clear-cache")
        response.raise_for_status()
        return response.json()


# ============================================================================
# ПРИМЕР 1: БАЗОВОЕ ИСПОЛЬЗОВАНИЕ
# ============================================================================

def demo_basic_usage():
    """Простейшее использование"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 1: Базовое использование")
    print("=" * 80 + "\n")

    client = RAGClient()

    # Проверить здоровье
    health = client.health()
    print(f"✅ Сервис работает: {health['status']}")
    print(f"🔍 Semantic search: {'✅' if health['semantic_search_available'] else '❌'}")
    print(f"📚 Загружено баз знаний: {health['knowledge_bases_loaded']}")
    print(f"📄 Всего документов: {health['total_embeddings']}\n")

    # Задать вопрос
    question = "Что такое overfitting в машинном обучении?"
    print(f"❓ Вопрос: {question}\n")

    response = client.query(question, explain=True)

    print(f"📊 Тип запроса: {response['query_type']}")
    print(f"🎯 Целевые уровни: {response['target_levels']}")
    print(f"💯 Уверенность: {response['confidence']:.2%}")
    print(f"🚀 Стратегия: {response['strategy']}")
    print(f"⏱️  Время: {response['elapsed_ms']:.1f}ms\n")

    print(f"🔍 РЕЗУЛЬТАТЫ (топ-{len(response['results'])}):\n")
    for i, result in enumerate(response['results'], 1):
        print(f"  {i}. [Уровень {result['level']}] {result['topic']}")
        print(f"     Score: {result['score']:.3f}")
        print(f"     Тип: {result['type']}")
        content = result['content'][:150].replace('\n', ' ')
        print(f"     {content}...\n")

    if response.get('decisions'):
        print("🤖 АВТОНОМНЫЕ РЕШЕНИЯ АГЕНТА:\n")
        for decision in response['decisions']:
            print(f"  • [{decision['type']}] {decision['description']}")


# ============================================================================
# ПРИМЕР 2: ИНТЕГРАЦИЯ С LLM (RAG PATTERN)
# ============================================================================

def demo_rag_with_llm():
    """RAG pattern: извлечь контекст + отправить в LLM"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 2: RAG с LLM интеграцией")
    print("=" * 80 + "\n")

    client = RAGClient()

    question = "Как защититься от ransomware?"
    print(f"❓ Вопрос пользователя: {question}\n")

    # Шаг 1: Извлечь контекст из базы знаний
    print("🔍 Шаг 1: Поиск в базе знаний...\n")
    response = client.query(question, top_k=3)

    # Собрать контекст
    context_parts = []
    for result in response['results']:
        context_parts.append(
            f"[Уровень {result['level']}, {result['topic']}]\n{result['content']}\n"
        )

    context = "\n---\n".join(context_parts)

    print("📚 Найденный контекст:\n")
    print(context[:500] + "...\n")

    # Шаг 2: Сформировать промпт для LLM
    print("🤖 Шаг 2: Формирование промпта для LLM...\n")

    system_prompt = """Ты эксперт по кибербезопасности.
Используй предоставленный контекст из базы знаний для ответа на вопрос.
Если в контексте нет информации, так и скажи."""

    user_prompt = f"""КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ВОПРОС: {question}

Ответь подробно, основываясь на контексте."""

    # Шаг 3: Вызов LLM (псевдокод, требует API ключ)
    print("💬 Шаг 3: Отправка в LLM...\n")
    print("(Для реального использования нужен OpenAI API key)\n")

    """
    # Реальный вызов (раскомментировать при наличии API key):
    import openai

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    answer = response.choices[0].message.content
    print(f"📝 Ответ LLM:\n{answer}")
    """

    print("✅ RAG pipeline готов к использованию!")
    print("   1. Извлечение контекста ✓")
    print("   2. Формирование промпта ✓")
    print("   3. Вызов LLM (требует API key)")


# ============================================================================
# ПРИМЕР 3: BATCH PROCESSING
# ============================================================================

def demo_batch_processing():
    """Обработка множественных запросов"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 3: Batch processing (массовая обработка)")
    print("=" * 80 + "\n")

    client = RAGClient()

    questions = [
        "Что такое Bitcoin?",
        "Как работает квантовый компьютер?",
        "Приведи пример ransomware атаки",
        "Что такое облачные вычисления?",
        "Формула для блокчейна"
    ]

    results = []
    total_time = 0

    print(f"📦 Обработка {len(questions)} запросов...\n")

    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
        start = time.time()
        response = client.query(question, top_k=1)
        elapsed = time.time() - start
        total_time += elapsed

        if response['results']:
            top_result = response['results'][0]
            print(f"   ✅ [{top_result['level']}] {top_result['topic']} (score: {top_result['score']:.2f}, {elapsed*1000:.0f}ms)")
        else:
            print(f"   ❌ Ничего не найдено ({elapsed*1000:.0f}ms)")

        results.append(response)
        print()

    print(f"📊 СТАТИСТИКА:")
    print(f"   Всего запросов: {len(questions)}")
    print(f"   Общее время: {total_time:.2f}s")
    print(f"   Среднее время: {total_time/len(questions)*1000:.1f}ms/запрос")

    # Проверить кэш
    stats = client.stats()
    print(f"   Попаданий в кэш: {stats['stats']['cache_hits']}")
    print(f"   Размер кэша: {stats['cache_size']}")


# ============================================================================
# ПРИМЕР 4: АВТОНОМНОЕ ПРИНЯТИЕ РЕШЕНИЙ
# ============================================================================

def demo_autonomous_decision_making():
    """Демонстрация автономных решений агента"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 4: Автономное принятие решений")
    print("=" * 80 + "\n")

    client = RAGClient()

    # Запросы разных типов
    test_cases = [
        {
            "question": "Покажи формулу для искусственного интеллекта",
            "expected_type": "formula",
            "expected_levels": [1, 2]
        },
        {
            "question": "Приведи примеры применения блокчейна",
            "expected_type": "example",
            "expected_levels": [4, 3]
        },
        {
            "question": "Как работает алгоритм квантовых вычислений?",
            "expected_type": "algorithm",
            "expected_levels": [3, 2]
        },
        {
            "question": "Дай совет по безопасности",
            "expected_type": "advice",
            "expected_levels": [4]
        }
    ]

    print("🤖 Проверка автономных решений агента:\n")

    for i, test in enumerate(test_cases, 1):
        print(f"{i}. Запрос: {test['question']}")
        response = client.query(test['question'], explain=True)

        # Проверить решения
        print(f"   Ожидаемый тип: {test['expected_type']}")
        print(f"   Определённый тип: {response['query_type']}")
        print(f"   {'✅' if response['query_type'] == test['expected_type'] else '⚠️ '} Распознавание типа")

        print(f"\n   Ожидаемые уровни: {test['expected_levels']}")
        print(f"   Выбранные уровни: {response['target_levels']}")
        print(f"   {'✅' if response['target_levels'] == test['expected_levels'] else '⚠️ '} Выбор уровней")

        print(f"\n   Уверенность: {response['confidence']:.2%}")
        print(f"   Стратегия: {response['strategy']}")

        # Показать решения
        print(f"\n   🧠 Принятые решения:")
        for decision in response['decisions'][:5]:  # Первые 5
            print(f"      • [{decision['type']}] {decision['description']}")

        print(f"\n{'─' * 80}\n")


# ============================================================================
# ПРИМЕР 5: ФИЛЬТРАЦИЯ ПО УРОВНЯМ
# ============================================================================

def demo_level_filtering():
    """Фильтрация результатов по уровням"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 5: Фильтрация по уровням")
    print("=" * 80 + "\n")

    client = RAGClient()

    question = "Искусственный интеллект"

    print(f"❓ Запрос: {question}\n")

    for level in [1, 2, 3, 4]:
        print(f"🎯 Поиск только на уровне {level}:")
        response = client.query(question, levels=[level], top_k=2)

        if response['results']:
            for result in response['results']:
                print(f"   • [{result['type']}] {result['topic']} (score: {result['score']:.2f})")
        else:
            print(f"   (Ничего не найдено)")

        print()


# ============================================================================
# ПРИМЕР 6: СРАВНЕНИЕ SEMANTIC VS KEYWORD
# ============================================================================

def demo_search_comparison():
    """Сравнение semantic и keyword search"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 6: Сравнение Semantic vs Keyword search")
    print("=" * 80 + "\n")

    client = RAGClient()

    # Проверить доступность semantic search
    health = client.health()
    if not health['semantic_search_available']:
        print("⚠️  Semantic search недоступен, пропускаем демо")
        return

    question = "Как защитить данные от взлома?"
    print(f"❓ Вопрос: {question}\n")

    # Keyword search
    print("1️⃣  KEYWORD SEARCH:")
    response_kw = client.query(question, use_semantic=False, top_k=3)
    print(f"   Время: {response_kw['elapsed_ms']:.1f}ms")
    print(f"   Уверенность: {response_kw['confidence']:.2%}")
    print(f"   Результаты:")
    for result in response_kw['results']:
        print(f"      • [{result['level']}] {result['topic']} (score: {result['score']:.2f})")

    print()

    # Semantic search
    print("2️⃣  SEMANTIC SEARCH:")
    response_sem = client.query(question, use_semantic=True, top_k=3)
    print(f"   Время: {response_sem['elapsed_ms']:.1f}ms")
    print(f"   Уверенность: {response_sem['confidence']:.2%}")
    print(f"   Результаты:")
    for result in response_sem['results']:
        print(f"      • [{result['level']}] {result['topic']} (score: {result['score']:.2f})")

    print(f"\n📊 Semantic search понимает смысл запроса лучше!")


# ============================================================================
# ПРИМЕР 7: REAL-WORLD USE CASE - Chatbot
# ============================================================================

def demo_chatbot_integration():
    """Пример интеграции в чатбот"""
    print("\n" + "=" * 80)
    print("ПРИМЕР 7: Интеграция в чатбот")
    print("=" * 80 + "\n")

    client = RAGClient()

    def chatbot_response(user_question: str) -> str:
        """Функция чатбота с RAG"""
        # Получить контекст из базы знаний
        response = client.query(user_question, top_k=2)

        if response['confidence'] > 0.7:
            # Высокая уверенность - вернуть прямой ответ
            top_result = response['results'][0]
            return f"Из базы знаний (уровень {top_result['level']}):\n{top_result['content'][:300]}..."

        elif response['confidence'] > 0.4:
            # Средняя уверенность - предложить варианты
            answers = "\n".join([
                f"• [{r['topic']}] {r['content'][:100]}..."
                for r in response['results'][:3]
            ])
            return f"Возможно, вы имеете в виду:\n{answers}"

        else:
            # Низкая уверенность - попросить уточнения
            return "Извините, не могу найти точную информацию. Можете уточнить вопрос?"

    # Симуляция диалога
    conversation = [
        "Что такое blockchain?",
        "Приведи пример использования",
        "Какие есть проблемы?",
        "Как это работает технически?"
    ]

    print("💬 СИМУЛЯЦИЯ ДИАЛОГА С ЧАТБОТОМ:\n")

    for i, user_input in enumerate(conversation, 1):
        print(f"👤 Пользователь: {user_input}")
        bot_response = chatbot_response(user_input)
        print(f"🤖 Бот: {bot_response}\n")
        print(f"{'─' * 80}\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Запустить все примеры"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "RAG MICRO-AGENT - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ" + " " * 18 + "║")
    print("╚" + "═" * 78 + "╝")

    try:
        # Проверить, что сервер запущен
        client = RAGClient()
        client.health()
    except requests.exceptions.ConnectionError:
        print("\n❌ ОШИБКА: RAG API сервер не запущен!")
        print("\nЗапустите сервер:")
        print("   python rag_api_server.py")
        print("\nПосле этого запустите примеры снова.")
        return

    # Запустить все демо
    demo_basic_usage()
    demo_rag_with_llm()
    demo_batch_processing()
    demo_autonomous_decision_making()
    demo_level_filtering()
    demo_search_comparison()
    demo_chatbot_integration()

    print("\n" + "=" * 80)
    print("✅ ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ")
    print("=" * 80)
    print("""
📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ:

1. API Документация: http://localhost:8000/docs
2. Проверка здоровья: http://localhost:8000/health
3. Статистика: http://localhost:8000/stats

🔧 КАСТОМИЗАЦИЯ:

Вы можете использовать этот код как основу для:
- Интеграции в свой чатбот
- Создания Q&A системы
- Построения recommendation engine
- Автоматизации исследований
    """)


if __name__ == "__main__":
    main()
