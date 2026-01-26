#!/usr/bin/env python3
"""
SEMANTIC SEARCH AGENT - ПОИСК ПО СМЫСЛУ
========================================

Улучшение поиска с помощью vector embeddings:
- Поиск по смыслу, а не по ключевым словам
- Понимание синонимов и похожих концепций
- Многоязычная поддержка (50+ языков)
- Гибридный поиск (keyword + semantic)

ПРЕИМУЩЕСТВА:
- "нейросеть" найдёт "искусственный интеллект"
- "защита от атак" найдёт "кибербезопасность"
- Работает даже если точных слов нет в документе
"""

import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import time
from collections import defaultdict
import re

# Попытка импорта библиотек (с fallback если нет)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠ sentence-transformers не установлен. Используется keyword search.")
    print("  Установите: pip install sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠ faiss не установлен. Используется brute-force search.")
    print("  Установите: pip install faiss-cpu")


@dataclass
class SearchResult:
    """Результат семантического поиска"""
    doc_id: int
    topic: str
    content: str
    score: float
    semantic_score: float
    keyword_score: float
    combined_score: float
    path: str
    metadata: Dict[str, Any]


class SemanticSearchAgent:
    """
    Агент семантического поиска

    Использует:
    - Sentence Transformers для эмбеддингов
    - FAISS для быстрого поиска векторов
    - Гибридный подход (semantic + keyword)
    """

    def __init__(
        self,
        knowledge_base_path: str = "афоризмы",
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir: str = ".cache"
    ):
        self.kb_path = Path(knowledge_base_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Загрузка модели
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            print(f"Загрузка модели {model_name}...")
            self.model = SentenceTransformer(model_name)
            print(f"✓ Модель загружена")
        else:
            self.model = None

        # Хранилище
        self.documents = []
        self.embeddings = None
        self.index = None

        # Статистика
        self.stats = {
            "semantic_searches": 0,
            "keyword_searches": 0,
            "hybrid_searches": 0,
            "avg_semantic_time_ms": 0,
            "avg_keyword_time_ms": 0
        }

        # Загрузка базы знаний
        self._load_knowledge_base()

        # Создание индекса
        self._build_index()

    def _load_knowledge_base(self):
        """Загрузка документов"""
        print(f"\nЗагрузка базы знаний из {self.kb_path}...")

        if not self.kb_path.exists():
            print(f"⚠ Путь не найден: {self.kb_path}")
            return

        txt_files = list(self.kb_path.rglob("*.txt"))
        print(f"Найдено файлов: {len(txt_files)}")

        for i, file_path in enumerate(txt_files):
            try:
                content = file_path.read_text(encoding='utf-8')
                topic = file_path.parent.name

                # Разбиение на чанки (для больших документов)
                chunks = self._chunk_document(content, max_chunk_size=500)

                for chunk_id, chunk in enumerate(chunks):
                    doc = {
                        "id": len(self.documents),
                        "path": str(file_path),
                        "topic": topic,
                        "content": chunk,
                        "full_content": content,
                        "chunk_id": chunk_id,
                        "total_chunks": len(chunks),
                        "metadata": {
                            "file_size": len(content),
                            "num_lines": len(content.split('\n'))
                        }
                    }
                    self.documents.append(doc)

            except Exception as e:
                print(f"⚠ Ошибка загрузки {file_path}: {e}")

        print(f"✓ Загружено документов: {len(self.documents)}")

    def _chunk_document(self, content: str, max_chunk_size: int = 500) -> List[str]:
        """Разбиение документа на чанки"""
        # Разбиение по параграфам
        paragraphs = content.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [content]

    def _build_index(self):
        """Построение FAISS индекса"""
        if not self.model or not self.documents:
            print("⚠ Semantic search недоступен")
            return

        # Проверка кэша
        cache_file = self.cache_dir / "embeddings.pkl"

        if cache_file.exists():
            print("\nЗагрузка эмбеддингов из кэша...")
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self.embeddings = cached_data['embeddings']
            print(f"✓ Загружено из кэша")
        else:
            print("\nСоздание эмбеддингов...")
            texts = [doc['content'] for doc in self.documents]

            # Батч-обработка для эффективности
            batch_size = 32
            embeddings_list = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_embeddings = self.model.encode(
                    batch,
                    show_progress_bar=True,
                    convert_to_numpy=True
                )
                embeddings_list.append(batch_embeddings)

            self.embeddings = np.vstack(embeddings_list)

            # Сохранение в кэш
            with open(cache_file, 'wb') as f:
                pickle.dump({'embeddings': self.embeddings}, f)

            print(f"✓ Создано эмбеддингов: {self.embeddings.shape}")

        # Построение FAISS индекса
        if FAISS_AVAILABLE:
            print("\nПостроение FAISS индекса...")
            dimension = self.embeddings.shape[1]

            # IndexFlatIP для cosine similarity
            # (после нормализации IP = cosine similarity)
            self.index = faiss.IndexFlatIP(dimension)

            # Нормализация векторов
            faiss.normalize_L2(self.embeddings)

            # Добавление в индекс
            self.index.add(self.embeddings)

            print(f"✓ FAISS индекс построен ({self.index.ntotal} векторов)")
        else:
            print("⚠ FAISS недоступен, используется brute-force")

    def semantic_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """Чисто семантический поиск"""
        if not self.model:
            raise RuntimeError("Semantic search недоступен (нет модели)")

        start_time = time.time()

        # Кодирование запроса
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Нормализация
        if FAISS_AVAILABLE:
            faiss.normalize_L2(query_embedding)

        # Поиск
        if FAISS_AVAILABLE and self.index:
            # FAISS поиск (быстро)
            scores, indices = self.index.search(query_embedding, top_k)
            scores = scores[0]
            indices = indices[0]
        else:
            # Brute-force (медленно)
            # Нормализация
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            embeddings_norm = self.embeddings / np.linalg.norm(
                self.embeddings, axis=1, keepdims=True
            )

            # Cosine similarity
            similarities = np.dot(embeddings_norm, query_norm.T).flatten()

            # Топ-k
            indices = np.argsort(similarities)[::-1][:top_k]
            scores = similarities[indices]

        # Формирование результатов
        results = []
        for idx, score in zip(indices, scores):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append(SearchResult(
                    doc_id=doc['id'],
                    topic=doc['topic'],
                    content=doc['content'][:300],
                    score=float(score),
                    semantic_score=float(score),
                    keyword_score=0.0,
                    combined_score=float(score),
                    path=doc['path'],
                    metadata=doc['metadata']
                ))

        elapsed = (time.time() - start_time) * 1000

        # Обновление статистики
        self.stats['semantic_searches'] += 1
        n = self.stats['semantic_searches']
        old_avg = self.stats['avg_semantic_time_ms']
        self.stats['avg_semantic_time_ms'] = (old_avg * (n - 1) + elapsed) / n

        return results

    def keyword_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """Традиционный поиск по ключевым словам"""
        start_time = time.time()

        # Извлечение ключевых слов
        keywords = self._extract_keywords(query)

        # Поиск
        scores = []
        for doc in self.documents:
            score = self._calculate_keyword_score(keywords, doc['content'])
            scores.append((doc['id'], score))

        # Сортировка
        scores.sort(key=lambda x: x[1], reverse=True)
        top_scores = scores[:top_k]

        # Формирование результатов
        results = []
        for doc_id, score in top_scores:
            if score > 0:
                doc = self.documents[doc_id]
                results.append(SearchResult(
                    doc_id=doc['id'],
                    topic=doc['topic'],
                    content=doc['content'][:300],
                    score=score,
                    semantic_score=0.0,
                    keyword_score=score,
                    combined_score=score,
                    path=doc['path'],
                    metadata=doc['metadata']
                ))

        elapsed = (time.time() - start_time) * 1000

        # Статистика
        self.stats['keyword_searches'] += 1
        n = self.stats['keyword_searches']
        old_avg = self.stats['avg_keyword_time_ms']
        self.stats['avg_keyword_time_ms'] = (old_avg * (n - 1) + elapsed) / n

        return results

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResult]:
        """
        Гибридный поиск (semantic + keyword)

        Args:
            query: Поисковый запрос
            top_k: Количество результатов
            semantic_weight: Вес семантического поиска (0-1)
            keyword_weight: Вес keyword поиска (0-1)
        """
        if not self.model:
            # Fallback на keyword если нет модели
            return self.keyword_search(query, top_k)

        start_time = time.time()

        # Семантический поиск
        semantic_results = self.semantic_search(query, top_k=top_k*2)

        # Keyword поиск
        keyword_results = self.keyword_search(query, top_k=top_k*2)

        # Объединение результатов
        combined_scores = defaultdict(lambda: {'semantic': 0.0, 'keyword': 0.0})

        for result in semantic_results:
            combined_scores[result.doc_id]['semantic'] = result.semantic_score

        for result in keyword_results:
            combined_scores[result.doc_id]['keyword'] = result.keyword_score

        # Вычисление комбинированного score
        final_results = []
        for doc_id, scores in combined_scores.items():
            # Нормализация и взвешивание
            combined = (
                scores['semantic'] * semantic_weight +
                scores['keyword'] * keyword_weight
            )

            doc = self.documents[doc_id]
            final_results.append(SearchResult(
                doc_id=doc['id'],
                topic=doc['topic'],
                content=doc['content'][:300],
                score=combined,
                semantic_score=scores['semantic'],
                keyword_score=scores['keyword'],
                combined_score=combined,
                path=doc['path'],
                metadata=doc['metadata']
            ))

        # Сортировка по комбинированному score
        final_results.sort(key=lambda x: x.combined_score, reverse=True)

        # Топ-k
        final_results = final_results[:top_k]

        elapsed = (time.time() - start_time) * 1000

        # Статистика
        self.stats['hybrid_searches'] += 1

        return final_results

    def _extract_keywords(self, query: str) -> List[str]:
        """Извлечение ключевых слов"""
        # Стоп-слова
        stop_words = {
            'как', 'что', 'где', 'когда', 'почему', 'какой', 'какая', 'какие',
            'это', 'есть', 'был', 'была', 'были', 'будет', 'можно', 'нужно',
            'и', 'или', 'не', 'в', 'на', 'с', 'по', 'для', 'к', 'от', 'до'
        }

        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def _calculate_keyword_score(self, keywords: List[str], text: str) -> float:
        """Вычисление keyword score"""
        text_lower = text.lower()
        score = 0.0

        for keyword in keywords:
            count = text_lower.count(keyword)
            score += count

        return score

    def query(
        self,
        query: str,
        method: str = "hybrid",
        top_k: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Главный метод поиска

        Args:
            query: Поисковый запрос
            method: "semantic", "keyword", или "hybrid"
            top_k: Количество результатов
            **kwargs: Дополнительные параметры

        Returns:
            Dict с результатами и метаданными
        """
        print(f"\n{'='*70}")
        print(f"  SEMANTIC SEARCH")
        print(f"{'='*70}")
        print(f"  Запрос: {query}")
        print(f"  Метод: {method}")
        print(f"  Top-K: {top_k}")

        start_time = time.time()

        # Выбор метода
        if method == "semantic":
            results = self.semantic_search(query, top_k)
        elif method == "keyword":
            results = self.keyword_search(query, top_k)
        elif method == "hybrid":
            results = self.hybrid_search(query, top_k, **kwargs)
        else:
            raise ValueError(f"Неизвестный метод: {method}")

        elapsed = (time.time() - start_time) * 1000

        print(f"\n  Результатов: {len(results)}")
        print(f"  Время: {elapsed:.2f} ms")
        print(f"{'='*70}\n")

        return {
            "query": query,
            "method": method,
            "results": [asdict(r) for r in results],
            "count": len(results),
            "elapsed_ms": elapsed,
            "stats": self.stats
        }

    def compare_methods(self, query: str, top_k: int = 5):
        """Сравнение всех методов поиска"""
        print(f"\n{'='*70}")
        print(f"  СРАВНЕНИЕ МЕТОДОВ ПОИСКА")
        print(f"{'='*70}")
        print(f"  Запрос: {query}\n")

        methods = []

        # Keyword
        if self.documents:
            print("→ Keyword search...")
            kw_results = self.keyword_search(query, top_k)
            methods.append(("Keyword", kw_results))

        # Semantic
        if self.model:
            print("→ Semantic search...")
            sem_results = self.semantic_search(query, top_k)
            methods.append(("Semantic", sem_results))

            print("→ Hybrid search...")
            hyb_results = self.hybrid_search(query, top_k)
            methods.append(("Hybrid", hyb_results))

        # Вывод сравнения
        print(f"\n{'─'*70}")
        print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ:")
        print(f"{'─'*70}\n")

        for method_name, results in methods:
            print(f"{method_name} Search:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.topic} (score: {result.score:.3f})")
            print()

        return methods

    def get_statistics(self) -> Dict:
        """Получение статистики"""
        return {
            "stats": self.stats,
            "documents": len(self.documents),
            "embeddings_shape": self.embeddings.shape if self.embeddings is not None else None,
            "index_size": self.index.ntotal if self.index else 0,
            "model": self.model.get_sentence_embedding_dimension() if self.model else None
        }


# ═══════════════════════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ДЕМОНСТРАЦИЯ SEMANTIC SEARCH")
    print("="*80 + "\n")

    # Инициализация
    agent = SemanticSearchAgent(knowledge_base_path="афоризмы")

    # Тест 1: Semantic search
    print("\n" + "─"*80)
    print("  ТЕСТ 1: Semantic Search")
    print("─"*80)

    if agent.model:
        result1 = agent.query(
            "защита от кибератак",
            method="semantic",
            top_k=3
        )

        print("Топ-3 результата:")
        for i, res in enumerate(result1['results'][:3], 1):
            print(f"{i}. {res['topic']} (score: {res['score']:.3f})")
            print(f"   {res['content'][:100]}...")
            print()

    # Тест 2: Hybrid search
    print("\n" + "─"*80)
    print("  ТЕСТ 2: Hybrid Search")
    print("─"*80)

    if agent.model:
        result2 = agent.query(
            "формула для беспроводных сетей",
            method="hybrid",
            top_k=3,
            semantic_weight=0.7,
            keyword_weight=0.3
        )

        print("Топ-3 результата:")
        for i, res in enumerate(result2['results'][:3], 1):
            print(f"{i}. {res['topic']}")
            print(f"   Semantic: {res['semantic_score']:.3f}, "
                  f"Keyword: {res['keyword_score']:.3f}, "
                  f"Combined: {res['combined_score']:.3f}")
            print()

    # Тест 3: Сравнение методов
    print("\n" + "─"*80)
    print("  ТЕСТ 3: Сравнение всех методов")
    print("─"*80)

    agent.compare_methods("искусственный интеллект и нейронные сети", top_k=3)

    # Статистика
    print("\n" + "="*80)
    print("  СТАТИСТИКА")
    print("="*80)

    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n✓ Демонстрация завершена!")
