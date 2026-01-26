#!/usr/bin/env python3
"""
Примеры интеграции с популярными AI/ML библиотеками

Демонстрирует использование 4-уровневой системы знаний с:
- OpenAI API (GPT)
- Sentence Transformers (эмбеддинги)
- FAISS (векторный поиск)
- Langchain (RAG)

Примечание: Для запуска требуются дополнительные библиотеки:
    pip install openai sentence-transformers faiss-cpu langchain tiktoken
"""

import json
from typing import List, Dict, Any
from knowledge_system import KnowledgeSystem, generate_training_data


# ============================================================================
# 1. ИНТЕГРАЦИЯ С OPENAI API (Fine-tuning и RAG)
# ============================================================================

def prepare_for_openai_finetuning(ks: KnowledgeSystem, output_file: str = 'openai_training.jsonl'):
    """
    Подготовка данных для fine-tuning OpenAI моделей

    Формат: JSONL с полями messages[] (chat format)
    Документация: https://platform.openai.com/docs/guides/fine-tuning

    Args:
        ks: Система знаний
        output_file: Путь для сохранения
    """
    print("Генерация данных для OpenAI fine-tuning...")

    # Генерируем базовые тренировочные данные
    training_data = generate_training_data(ks)

    # Конвертируем в формат OpenAI (chat messages)
    openai_data = []
    for item in training_data:
        openai_item = {
            "messages": [
                {
                    "role": "system",
                    "content": f"Ты эксперт по теме '{ks.get_topic()}'. Отвечай точно и информативно на основе 4-уровневой системы познания."
                },
                {
                    "role": "user",
                    "content": item['question']
                },
                {
                    "role": "assistant",
                    "content": item['answer']
                }
            ]
        }
        openai_data.append(openai_item)

    # Добавляем дополнительные примеры из теоремы
    theorem = ks.get_theorem()

    # Примеры про insights
    for insight in theorem.key_insights:
        openai_data.append({
            "messages": [
                {"role": "system", "content": f"Ты эксперт по теме '{ks.get_topic()}'."},
                {"role": "user", "content": f"Объясни концепцию: {insight.get('insight')}"},
                {"role": "assistant", "content": json.dumps(insight, ensure_ascii=False, indent=2)}
            ]
        })

    # Примеры про real-world cases
    for example in theorem.real_world_examples:
        openai_data.append({
            "messages": [
                {"role": "system", "content": f"Ты эксперт по теме '{ks.get_topic()}'."},
                {"role": "user", "content": f"Расскажи про пример: {example.get('name')}"},
                {"role": "assistant", "content": f"{example.get('lesson', 'N/A')}\n\nДетали: {json.dumps(example, ensure_ascii=False, indent=2)}"}
            ]
        })

    # Сохранение в JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in openai_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✓ Сохранено {len(openai_data)} примеров в {output_file}")
    print(f"  Теперь можно использовать для fine-tuning:")
    print(f"    openai api fine_tunes.create -t {output_file} -m gpt-3.5-turbo")

    return openai_data


def rag_with_openai(ks: KnowledgeSystem, user_question: str, api_key: str = None):
    """
    RAG (Retrieval-Augmented Generation) с OpenAI

    1. Находим релевантные фрагменты из системы знаний
    2. Передаём их как контекст в GPT
    3. Получаем ответ на основе знаний

    Args:
        ks: Система знаний
        user_question: Вопрос пользователя
        api_key: OpenAI API ключ (опционально, можно в переменной окружения)
    """
    print(f"\nRAG: Вопрос пользователя: '{user_question}'")

    # 1. Поиск релевантного контекста
    # Простой keyword search (для production лучше использовать semantic search)
    keywords = user_question.lower().split()
    context_parts = []

    for keyword in keywords:
        results = ks.search(keyword)
        for level, items in results.items():
            if items:
                context_parts.extend(items)

    # Собираем контекст
    context = "\n".join(set(context_parts[:5]))  # Топ-5 уникальных фрагментов

    if not context:
        context = f"Формула: {ks.get_formula().expression}\nТеорема: {ks.get_theorem().main_theorem}"

    # 2. Формируем промпт для GPT
    system_message = f"""Ты эксперт по теме '{ks.get_topic()}'.
Используй следующий контекст из системы знаний для ответа на вопрос:

КОНТЕКСТ:
{context}

Отвечай точно, опираясь на этот контекст."""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_question}
    ]

    print("\n--- Контекст для RAG ---")
    print(context[:300] + "..." if len(context) > 300 else context)
    print("--- ---\n")

    # 3. Вызов OpenAI API (требует установленной библиотеки и API ключа)
    try:
        import openai
        if api_key:
            openai.api_key = api_key

        # Раскомментируйте для реального использования:
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=messages,
        #     temperature=0.7,
        #     max_tokens=500
        # )
        # answer = response.choices[0].message.content
        # print(f"GPT ответ: {answer}")
        # return answer

        print("(OpenAI API не вызван - требуется API ключ)")
        print(f"Промпт готов к отправке с {len(messages)} сообщениями")

    except ImportError:
        print("Библиотека openai не установлена. Установите: pip install openai")
    except Exception as e:
        print(f"Ошибка: {e}")

    return messages


# ============================================================================
# 2. SEMANTIC SEARCH С SENTENCE TRANSFORMERS + FAISS
# ============================================================================

def create_embeddings_and_index(ks: KnowledgeSystem):
    """
    Создание эмбеддингов и векторного индекса для semantic search

    Использует:
    - sentence-transformers для создания векторов
    - FAISS для быстрого поиска

    Args:
        ks: Система знаний

    Returns:
        (embeddings, texts, index) - векторы, тексты, FAISS индекс
    """
    print("\nСоздание эмбеддингов для semantic search...")

    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np

        # Загрузка модели (поддержка русского языка)
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print(f"✓ Модель загружена: {model}")

        # Собираем все тексты для индексации
        texts = []

        # Формулы
        texts.append(f"Формула: {ks.get_formula().explain()}")
        if ks.alternative_formula:
            texts.append(f"Альтернативная формула: {ks.alternative_formula.explain()}")

        # Компоненты архетипа
        archetype = ks.get_archetype()
        for comp_name, comp_data in archetype.components.items():
            comp_text = f"Компонент {comp_name}: {json.dumps(comp_data, ensure_ascii=False)}"
            texts.append(comp_text)

        # Шаги алгоритма
        algorithm = ks.get_algorithm()
        for step in algorithm.steps:
            step_text = f"Шаг {step.get('step')}: {step.get('name')} - {json.dumps(step, ensure_ascii=False)}"
            texts.append(step_text)

        # Теорема и примеры
        theorem = ks.get_theorem()
        texts.append(f"Теорема: {theorem.main_theorem}")

        for insight in theorem.key_insights:
            texts.append(f"Инсайт: {insight.get('insight')} - {json.dumps(insight, ensure_ascii=False)}")

        for example in theorem.real_world_examples:
            texts.append(f"Пример {example.get('name')}: {example.get('lesson')} - {json.dumps(example, ensure_ascii=False)}")

        for advice in theorem.practical_advice:
            texts.append(f"Совет: {advice}")

        print(f"✓ Собрано {len(texts)} текстовых фрагментов")

        # Создаём эмбеддинги
        print("Генерация эмбеддингов...")
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        print(f"✓ Создано {embeddings.shape[0]} векторов размерности {embeddings.shape[1]}")

        # Создаём FAISS индекс
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)  # L2 distance
        index.add(embeddings.astype('float32'))
        print(f"✓ FAISS индекс создан: {index.ntotal} векторов")

        return embeddings, texts, index, model

    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Установите библиотеки: pip install sentence-transformers faiss-cpu")
        return None, None, None, None


def semantic_search(query: str, texts: List[str], index, model, top_k: int = 5):
    """
    Семантический поиск по индексу

    Args:
        query: Поисковый запрос
        texts: Список текстов (соответствует индексу)
        index: FAISS индекс
        model: SentenceTransformer модель
        top_k: Количество результатов

    Returns:
        Список (score, text) пар
    """
    if index is None or model is None:
        print("Индекс не создан")
        return []

    try:
        import numpy as np

        # Создаём эмбеддинг запроса
        query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')

        # Поиск ближайших векторов
        distances, indices = index.search(query_embedding, top_k)

        # Результаты
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
            score = 1 / (1 + dist)  # Конвертируем distance в similarity score
            text = texts[idx]
            results.append((score, text))

        return results

    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return []


def demo_semantic_search(ks: KnowledgeSystem):
    """Демонстрация semantic search"""
    print("\n" + "=" * 80)
    print("DEMO: Semantic Search")
    print("=" * 80)

    embeddings, texts, index, model = create_embeddings_and_index(ks)

    if index is None:
        print("Semantic search недоступен - требуются библиотеки")
        return

    # Тестовые запросы
    queries = [
        "Что такое переобучение?",
        "Примеры использования в медицине",
        "Как работает обучение нейросети?",
        "ChatGPT и его ограничения"
    ]

    for query in queries:
        print(f"\n🔍 Запрос: '{query}'")
        print("-" * 80)

        results = semantic_search(query, texts, index, model, top_k=3)

        for i, (score, text) in enumerate(results, 1):
            # Обрезаем длинные тексты
            display_text = text[:200] + "..." if len(text) > 200 else text
            print(f"\n  {i}. Score: {score:.3f}")
            print(f"     {display_text}")


# ============================================================================
# 3. ИНТЕГРАЦИЯ С LANGCHAIN (RAG Framework)
# ============================================================================

def create_langchain_vectorstore(ks: KnowledgeSystem):
    """
    Создание векторного хранилища LangChain для RAG

    Args:
        ks: Система знаний

    Returns:
        vectorstore объект LangChain
    """
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.docstore.document import Document

        print("\nСоздание LangChain vectorstore...")

        # Создаём документы
        documents = []

        # Формула
        documents.append(Document(
            page_content=ks.get_formula().explain(),
            metadata={"level": 1, "type": "formula", "topic": ks.get_topic()}
        ))

        # Архетип
        for comp_name, comp_data in ks.get_archetype().components.items():
            documents.append(Document(
                page_content=json.dumps(comp_data, ensure_ascii=False, indent=2),
                metadata={"level": 2, "type": "archetype_component", "name": comp_name, "topic": ks.get_topic()}
            ))

        # Алгоритм
        for step in ks.get_algorithm().steps:
            documents.append(Document(
                page_content=json.dumps(step, ensure_ascii=False, indent=2),
                metadata={"level": 3, "type": "algorithm_step", "step": step.get('step'), "topic": ks.get_topic()}
            ))

        # Теорема
        theorem = ks.get_theorem()
        documents.append(Document(
            page_content=theorem.main_theorem,
            metadata={"level": 4, "type": "main_theorem", "topic": ks.get_topic()}
        ))

        for example in theorem.real_world_examples:
            documents.append(Document(
                page_content=f"{example.get('name')}: {example.get('lesson')}\n{json.dumps(example, ensure_ascii=False, indent=2)}",
                metadata={"level": 4, "type": "example", "name": example.get('name'), "topic": ks.get_topic()}
            ))

        print(f"✓ Создано {len(documents)} документов")

        # Создаём эмбеддинги и векторное хранилище
        embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        vectorstore = FAISS.from_documents(documents, embeddings)

        print(f"✓ Vectorstore создан")
        return vectorstore

    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Установите: pip install langchain faiss-cpu sentence-transformers")
        return None


def demo_langchain_rag(ks: KnowledgeSystem):
    """Демонстрация RAG с LangChain"""
    try:
        from langchain.chains import RetrievalQA
        from langchain.llms import OpenAI

        print("\n" + "=" * 80)
        print("DEMO: LangChain RAG")
        print("=" * 80)

        vectorstore = create_langchain_vectorstore(ks)

        if vectorstore is None:
            print("Vectorstore не создан")
            return

        # Тестовый поиск
        query = "Что такое overfitting?"
        print(f"\n🔍 Запрос: '{query}'")

        docs = vectorstore.similarity_search(query, k=3)

        print("\nНайденные документы:")
        for i, doc in enumerate(docs, 1):
            print(f"\n  {i}. [{doc.metadata.get('type')}] {doc.metadata.get('name', 'N/A')}")
            content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            print(f"     {content}")

        # Для полного RAG с LLM нужен OpenAI API ключ:
        # llm = OpenAI(temperature=0)
        # qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
        # answer = qa_chain.run(query)

    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Установите: pip install langchain openai")


# ============================================================================
# MAIN - Запуск всех демонстраций
# ============================================================================

def main():
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "AI/ML ИНТЕГРАЦИЯ - ДЕМОНСТРАЦИЯ" + " " * 26 + "║")
    print("╚" + "═" * 78 + "╝\n")

    # Загрузка системы знаний
    ks = KnowledgeSystem.from_json('искусственный-интеллект.json')
    print(f"✓ Загружена система знаний: {ks.get_title()}\n")

    # 1. OpenAI fine-tuning
    print("\n" + "=" * 80)
    print("1. OPENAI FINE-TUNING - Подготовка данных")
    print("=" * 80)
    prepare_for_openai_finetuning(ks, 'openai_training.jsonl')

    # 2. OpenAI RAG
    print("\n" + "=" * 80)
    print("2. OPENAI RAG - Retrieval-Augmented Generation")
    print("=" * 80)
    rag_with_openai(ks, "Что такое bias в данных и почему это опасно?")

    # 3. Semantic Search
    demo_semantic_search(ks)

    # 4. LangChain
    demo_langchain_rag(ks)

    print("\n" + "=" * 80)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 80)
    print("""
Продемонстрированы интеграции с:
  ✓ OpenAI API (fine-tuning и RAG)
  ✓ Sentence Transformers (эмбеддинги)
  ✓ FAISS (векторный поиск)
  ✓ LangChain (RAG framework)

Эти подходы позволяют использовать 4-уровневую систему знаний в:
  • Чатботах и Q&A системах
  • Обучении и fine-tuning LLM
  • Семантическом поиске
  • RAG (Retrieval-Augmented Generation)
  • Knowledge bases и документации

Форматы JSON/YAML идеально подходят для AI/ML обработки!
    """)


if __name__ == '__main__':
    main()
