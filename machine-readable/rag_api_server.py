#!/usr/bin/env python3
"""
RAG API SERVER - Уровень 2-3

REST API для автономного микро-агента с semantic search.

Запуск:
    pip install fastapi uvicorn sentence-transformers faiss-cpu pydantic
    python rag_api_server.py

API будет доступен на http://localhost:8000
Документация: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import time
from pathlib import Path
from datetime import datetime
import hashlib

# Опциональные зависимости (если установлены)
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False
    print("⚠️  Semantic search недоступен. Установите: pip install sentence-transformers faiss-cpu")

# ============================================================================
# MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """Запрос к агенту"""
    question: str = Field(..., description="Вопрос пользователя")
    top_k: int = Field(5, ge=1, le=20, description="Количество результатов")
    levels: Optional[List[int]] = Field(None, description="Фильтр по уровням (1-4)")
    use_semantic: bool = Field(True, description="Использовать semantic search")
    explain: bool = Field(False, description="Включить объяснения решений")


class QueryResponse(BaseModel):
    """Ответ агента"""
    success: bool
    query_type: str
    target_levels: List[int]
    results: List[Dict[str, Any]]
    confidence: float
    strategy: str
    decisions: List[Dict[str, str]]
    stats: Dict[str, Any]
    elapsed_ms: float
    semantic_search_used: bool = False


class HealthResponse(BaseModel):
    """Статус здоровья сервиса"""
    status: str
    version: str
    semantic_search_available: bool
    knowledge_bases_loaded: int
    total_embeddings: int
    cache_size: int


# ============================================================================
# AUTONOMOUS RAG AGENT
# ============================================================================

class AutonomousRAGAgent:
    """
    Автономный RAG агент с семантическим поиском

    Возможности:
    - Semantic search (sentence-transformers)
    - Автономные решения
    - Кэширование
    - Логирование решений
    - Приоритизация результатов
    """

    def __init__(self, knowledge_base_dir: str = "."):
        self.kb_dir = Path(knowledge_base_dir)
        self.cache = {}
        self.decision_log = []
        self.stats = {
            "queries": 0,
            "cache_hits": 0,
            "decisions_made": 0,
            "semantic_searches": 0
        }

        # Semantic search setup
        self.semantic_available = SEMANTIC_SEARCH_AVAILABLE
        self.model = None
        self.index = None
        self.documents = []
        self.embeddings = None

        if self.semantic_available:
            self._init_semantic_search()

    def _init_semantic_search(self):
        """Инициализация semantic search"""
        try:
            print("🔄 Загрузка модели для semantic search...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Модель загружена")

            # Загрузить и индексировать базы знаний
            print("🔄 Индексация баз знаний...")
            self._index_knowledge_bases()
            print(f"✅ Индексировано {len(self.documents)} документов")

        except Exception as e:
            print(f"⚠️  Ошибка инициализации semantic search: {e}")
            self.semantic_available = False

    def _index_knowledge_bases(self):
        """Индексация всех баз знаний"""
        self.documents = []

        # Найти все JSON файлы
        json_files = list(self.kb_dir.glob("*.json"))

        for json_file in json_files:
            if json_file.stem == "package":
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    kb = json.load(f)

                # Извлечь документы из базы знаний
                docs = self._extract_documents_from_kb(kb)
                self.documents.extend(docs)

            except Exception as e:
                print(f"⚠️  Ошибка загрузки {json_file}: {e}")

        # Создать embeddings
        if self.documents and self.model:
            texts = [doc['content'] for doc in self.documents]
            self.embeddings = self.model.encode(texts, show_progress_bar=False)

            # Создать FAISS индекс
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))

    def _extract_documents_from_kb(self, kb: Dict) -> List[Dict]:
        """Извлечь документы из структуры базы знаний"""
        docs = []
        topic = kb.get('metadata', {}).get('topic', 'unknown')

        # Уровень 1: Формулы
        formula = kb.get('level_1_formula', {})
        if formula:
            docs.append({
                'level': 1,
                'topic': topic,
                'type': 'formula',
                'content': json.dumps(formula, ensure_ascii=False),
                'metadata': formula
            })

        # Уровень 2: Архетипы (компоненты)
        archetype = kb.get('level_2_archetype', {})
        components = archetype.get('components', {})
        for comp_name, comp_data in components.items():
            docs.append({
                'level': 2,
                'topic': topic,
                'type': 'archetype_component',
                'component': comp_name,
                'content': f"{comp_name}: {json.dumps(comp_data, ensure_ascii=False)}",
                'metadata': comp_data
            })

        # Уровень 3: Алгоритмы (шаги)
        algorithm = kb.get('level_3_algorithm', {})
        steps = algorithm.get('steps', [])
        for step in steps:
            step_name = step.get('name', '')
            docs.append({
                'level': 3,
                'topic': topic,
                'type': 'algorithm_step',
                'step': step.get('step', '?'),
                'content': f"Шаг {step.get('step')}: {step_name} - {json.dumps(step, ensure_ascii=False)}",
                'metadata': step
            })

        # Уровень 4: Теоремы и примеры
        theorem = kb.get('level_4_theorem', {})

        # Главная теорема
        main_theorem = theorem.get('main_theorem', '')
        if main_theorem:
            docs.append({
                'level': 4,
                'topic': topic,
                'type': 'main_theorem',
                'content': f"Теорема: {main_theorem}",
                'metadata': {'main_theorem': main_theorem}
            })

        # Примеры
        examples = theorem.get('real_world_examples', [])
        for example in examples:
            name = example.get('name', '')
            lesson = example.get('lesson', '')
            docs.append({
                'level': 4,
                'topic': topic,
                'type': 'example',
                'name': name,
                'content': f"Пример {name}: {lesson} - {json.dumps(example, ensure_ascii=False)}",
                'metadata': example
            })

        # Практические советы
        advice = theorem.get('practical_advice', [])
        for adv in advice:
            docs.append({
                'level': 4,
                'topic': topic,
                'type': 'advice',
                'content': f"Совет: {adv}",
                'metadata': {'advice': adv}
            })

        return docs

    def query(self, request: QueryRequest) -> QueryResponse:
        """Главный метод: обработка запроса"""
        self.stats["queries"] += 1
        start_time = time.time()
        self.decision_log = []  # Сбросить лог для нового запроса

        # РЕШЕНИЕ 1: Проверить кэш
        cache_key = self._hash(request.question)
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            self._log_decision("cache_hit", "Результат найден в кэше")
            cached = self.cache[cache_key]
            cached['decisions'] = self.decision_log if request.explain else []
            return QueryResponse(**cached)

        # РЕШЕНИЕ 2: Анализ типа запроса
        query_type = self._analyze_query_type(request.question)
        self._log_decision("query_analysis", f"Определён тип запроса: {query_type}")

        # РЕШЕНИЕ 3: Определить целевые уровни
        if request.levels:
            target_levels = request.levels
            self._log_decision("level_override", f"Уровни заданы пользователем: {target_levels}")
        else:
            target_levels = self._decide_target_levels(request.question, query_type)
            self._log_decision("level_selection", f"Автоматически выбраны уровни: {target_levels}")

        # РЕШЕНИЕ 4: Выбор метода поиска
        use_semantic = request.use_semantic and self.semantic_available
        if use_semantic:
            self._log_decision("search_method", "Использован semantic search (embeddings)")
            results = self._semantic_search(request.question, target_levels, request.top_k * 2)
            self.stats["semantic_searches"] += 1
        else:
            self._log_decision("search_method", "Использован keyword search")
            results = self._keyword_search(request.question, target_levels)

        # РЕШЕНИЕ 5: Ранжирование
        ranked_results = self._rank_results(results, request.question)
        self._log_decision("ranking", f"Результаты отранжированы, найдено {len(ranked_results)}")

        # РЕШЕНИЕ 6: Оценка уверенности
        confidence = self._assess_confidence(ranked_results)
        self._log_decision("confidence", f"Уверенность оценена: {confidence:.2%}")

        # РЕШЕНИЕ 7: Стратегия ответа
        strategy = self._decide_response_strategy(confidence, ranked_results)
        self._log_decision("strategy", f"Выбрана стратегия: {strategy}")

        # РЕШЕНИЕ 8: Кэширование
        top_results = ranked_results[:request.top_k]
        if confidence > 0.6:
            response_dict = {
                "success": True,
                "query_type": query_type,
                "target_levels": target_levels,
                "results": top_results,
                "confidence": confidence,
                "strategy": strategy,
                "decisions": [],
                "stats": self.stats.copy(),
                "elapsed_ms": 0,
                "semantic_search_used": use_semantic
            }
            self.cache[cache_key] = response_dict
            self._log_decision("caching", "Результат сохранён в кэше")

        elapsed_ms = (time.time() - start_time) * 1000

        return QueryResponse(
            success=True,
            query_type=query_type,
            target_levels=target_levels,
            results=top_results,
            confidence=confidence,
            strategy=strategy,
            decisions=self.decision_log if request.explain else [],
            stats=self.stats.copy(),
            elapsed_ms=elapsed_ms,
            semantic_search_used=use_semantic
        )

    def _semantic_search(self, question: str, target_levels: List[int], top_k: int) -> List[Dict]:
        """Semantic search через FAISS"""
        if not self.semantic_available or not self.index:
            return []

        # Создать embedding запроса
        query_embedding = self.model.encode([question])[0]

        # Поиск в FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            min(top_k, len(self.documents))
        )

        # Собрать результаты
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()

                # Фильтр по уровням
                if doc['level'] not in target_levels:
                    continue

                # Рассчитать score (меньше distance = выше score)
                doc['score'] = 1 / (1 + dist)
                results.append(doc)

        return results

    def _keyword_search(self, question: str, target_levels: List[int]) -> List[Dict]:
        """Простой keyword search (fallback)"""
        results = []
        keywords = set(question.lower().split())

        for doc in self.documents:
            if doc['level'] not in target_levels:
                continue

            # Подсчёт совпадений
            content_words = set(doc['content'].lower().split())
            matches = len(keywords & content_words)

            if matches > 0:
                doc_copy = doc.copy()
                doc_copy['score'] = matches / len(keywords)
                results.append(doc_copy)

        return results

    def _analyze_query_type(self, question: str) -> str:
        """Определение типа запроса"""
        import re
        q_lower = question.lower()

        patterns = {
            "formula": [r"формул", r"уравнен", r"математ"],
            "example": [r"пример", r"случай", r"кейс"],
            "algorithm": [r"алгоритм", r"процесс", r"шаг", r"как\s+сделать"],
            "advice": [r"совет", r"рекоменд"],
            "concept": [r"что\s+так", r"объясни"]
        }

        for qtype, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, q_lower):
                    return qtype

        return "general"

    def _decide_target_levels(self, question: str, query_type: str) -> List[int]:
        """Определение целевых уровней"""
        type_to_levels = {
            "formula": [1, 2],
            "example": [4, 3],
            "algorithm": [3, 2],
            "advice": [4],
            "concept": [2, 1, 4],
            "general": [1, 2, 3, 4]
        }
        return type_to_levels.get(query_type, [1, 2, 3, 4])

    def _rank_results(self, results: List[Dict], question: str) -> List[Dict]:
        """Ранжирование по score"""
        return sorted(results, key=lambda x: x.get('score', 0), reverse=True)

    def _assess_confidence(self, results: List[Dict]) -> float:
        """Оценка уверенности"""
        if not results:
            return 0.0

        top_score = results[0].get('score', 0)
        num_results = len(results)

        confidence = top_score * 0.6 + min(num_results / 10, 0.4)
        return min(confidence, 1.0)

    def _decide_response_strategy(self, confidence: float, results: List[Dict]) -> str:
        """Выбор стратегии ответа"""
        if confidence > 0.85:
            return "direct"
        elif confidence > 0.6:
            return "ranked_list"
        elif confidence > 0.3:
            return "expand_search"
        else:
            return "ask_clarification"

    def _hash(self, text: str) -> str:
        """Хэш для кэширования"""
        return hashlib.md5(text.encode()).hexdigest()

    def _log_decision(self, decision_type: str, description: str):
        """Логирование решения"""
        self.stats["decisions_made"] += 1
        self.decision_log.append({
            "type": decision_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="RAG Micro-Agent API",
    description="Автономный микро-агент для работы с 4-уровневой базой знаний",
    version="2.0.0"
)

# Глобальный агент
agent = AutonomousRAGAgent(knowledge_base_dir=".")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Корневой endpoint"""
    return {
        "message": "RAG Micro-Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Статус здоровья сервиса"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        semantic_search_available=agent.semantic_available,
        knowledge_bases_loaded=len(list(agent.kb_dir.glob("*.json"))),
        total_embeddings=len(agent.documents) if agent.documents else 0,
        cache_size=len(agent.cache)
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Главный endpoint: запрос к агенту

    Агент автономно:
    1. Анализирует тип запроса
    2. Выбирает целевые уровни
    3. Ищет релевантные результаты (semantic или keyword)
    4. Ранжирует результаты
    5. Оценивает уверенность
    6. Выбирает стратегию ответа
    7. Кэширует если нужно
    """
    try:
        response = agent.query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-cache")
async def clear_cache():
    """Очистить кэш"""
    agent.cache.clear()
    return {"message": "Кэш очищен", "cache_size": 0}


@app.get("/stats")
async def get_stats():
    """Статистика агента"""
    return {
        "stats": agent.stats,
        "cache_size": len(agent.cache),
        "total_documents": len(agent.documents),
        "recent_decisions": agent.decision_log[-10:]
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 80)
    print("🚀 RAG MICRO-AGENT API SERVER")
    print("=" * 80)
    print(f"\n📍 URL: http://localhost:8000")
    print(f"📚 Документация: http://localhost:8000/docs")
    print(f"🔍 Semantic Search: {'✅ Доступен' if SEMANTIC_SEARCH_AVAILABLE else '❌ Недоступен'}")
    print(f"\n{'=' * 80}\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
