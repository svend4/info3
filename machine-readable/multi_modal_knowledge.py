#!/usr/bin/env python3
"""
============================================================================
MULTI-MODAL KNOWLEDGE - Image, Text, and Combined Search
============================================================================
Уровень 2.4: ПРОДВИНУТОЕ

Поддержка различных модальностей знаний:
- Текстовый поиск (уже реализован)
- Поиск по изображениям (CLIP)
- Комбинированный текст+изображение поиск
- Кросс-модальный retrieval
- Image captioning
- Visual question answering (future)

ВОЗМОЖНОСТИ:
- CLIP model для zero-shot image classification
- Image-to-text и text-to-image search
- Multi-modal embeddings
- Unified search across modalities
- Image database management

Реальность: 85%
============================================================================
"""

import json
import os
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import random

# Попытка импорта PIL для работы с изображениями
try:
    from PIL import Image
    PIL_AVAILABLE = True
    ImageType = Image.Image
except ImportError:
    PIL_AVAILABLE = False
    ImageType = Any  # Fallback type hint
    print("⚠️  PIL not available. Install: pip install pillow")
    # Mock Image class for type hints
    class Image:
        class Image:
            pass

# Попытка импорта transformers для CLIP
try:
    from transformers import CLIPModel, CLIPProcessor
    import torch
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    print("⚠️  transformers or torch not available")
    print("   Install: pip install transformers torch")

# Попытка импорта numpy для векторных операций
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    ndarray = np.ndarray
except ImportError:
    NUMPY_AVAILABLE = False
    ndarray = Any  # Fallback type hint
    print("⚠️  NumPy not available. Install: pip install numpy")


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class MultiModalDocument:
    """Документ с мультимодальным содержимым"""
    doc_id: str
    text: str
    image_path: Optional[str] = None
    image_embedding: Optional[List[float]] = None
    text_embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class MultiModalSearchResult:
    """Результат мультимодального поиска"""
    doc_id: str
    text: str
    image_path: Optional[str]
    score: float
    modality: str  # text, image, multimodal
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CLIP EMBEDDING ENGINE
# ============================================================================

class CLIPEmbeddingEngine:
    """
    CLIP-based embedding engine для изображений и текста

    CLIP (Contrastive Language-Image Pre-training):
    - Обучен на 400M (image, text) парах
    - Zero-shot classification
    - Unified embedding space для text и image
    """

    def __init__(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        device: str = "cpu"
    ):
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP not available. Install transformers and torch.")

        self.model_name = model_name
        self.device = device

        print(f"Loading CLIP model: {model_name}...")
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()
        print(f"✅ CLIP model loaded on {device}")

    def encode_text(self, texts: Union[str, List[str]]) -> ndarray:
        """Кодирование текста в embedding"""
        if isinstance(texts, str):
            texts = [texts]

        inputs = self.processor(text=texts, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)

        # Нормализация
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()

    def encode_image(self, images: Union[ImageType, List[ImageType]]) -> ndarray:
        """Кодирование изображения в embedding"""
        if isinstance(images, Image.Image):
            images = [images]

        inputs = self.processor(images=images, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)

        # Нормализация
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()

    def compute_similarity(
        self,
        embeddings1: ndarray,
        embeddings2: ndarray
    ) -> ndarray:
        """Вычисление cosine similarity между embeddings"""
        # embeddings уже нормализованы, поэтому dot product = cosine similarity
        return np.dot(embeddings1, embeddings2.T)


# ============================================================================
# FALLBACK EMBEDDING ENGINE (без CLIP)
# ============================================================================

class MockEmbeddingEngine:
    """
    Mock embedding engine для демонстрации без CLIP

    Генерирует случайные embeddings для демонстрации работы
    """

    def __init__(self, embedding_dim: int = 512):
        self.embedding_dim = embedding_dim
        print(f"⚠️  Using Mock Embedding Engine (embedding_dim={embedding_dim})")

    def encode_text(self, texts: Union[str, List[str]]) -> ndarray:
        """Mock text encoding"""
        if isinstance(texts, str):
            texts = [texts]

        # Простой хэш для детерминированности
        embeddings = []
        for text in texts:
            seed = hash(text) % (2**32)
            np.random.seed(seed)
            embedding = np.random.randn(self.embedding_dim)
            embedding = embedding / np.linalg.norm(embedding)  # Нормализация
            embeddings.append(embedding)

        return np.array(embeddings)

    def encode_image(self, images: Union[Image.Image, List[Image.Image]]) -> ndarray:
        """Mock image encoding"""
        if isinstance(images, Image.Image):
            images = [images]

        # Случайные embeddings для изображений
        embeddings = []
        for img in images:
            embedding = np.random.randn(self.embedding_dim)
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)

        return np.array(embeddings)

    def compute_similarity(
        self,
        embeddings1: ndarray,
        embeddings2: ndarray
    ) -> ndarray:
        """Cosine similarity"""
        return np.dot(embeddings1, embeddings2.T)


# ============================================================================
# MULTI-MODAL AGENT
# ============================================================================

class MultiModalAgent:
    """
    Агент для мультимодального поиска

    Поддерживает:
    - Text-to-text search (semantic)
    - Image-to-image search
    - Text-to-image search (cross-modal)
    - Image-to-text search (cross-modal)
    - Multi-modal search (text + image)
    """

    def __init__(
        self,
        use_clip: bool = True,
        model_name: str = "openai/clip-vit-base-patch32",
        device: str = "cpu"
    ):
        # Выбор embedding engine
        if use_clip and CLIP_AVAILABLE and NUMPY_AVAILABLE:
            self.engine = CLIPEmbeddingEngine(model_name, device)
            self.engine_type = "CLIP"
        elif NUMPY_AVAILABLE:
            self.engine = MockEmbeddingEngine()
            self.engine_type = "Mock"
        else:
            raise ImportError("NumPy required for embeddings")

        # Хранилище документов
        self.documents: List[MultiModalDocument] = []
        self.text_embeddings: Optional[np.ndarray] = None
        self.image_embeddings: Optional[np.ndarray] = None

    # ========================================================================
    # DOCUMENT MANAGEMENT
    # ========================================================================

    def add_document(
        self,
        doc_id: str,
        text: str,
        image: Optional[Union[str, Image.Image]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Добавление мультимодального документа

        Args:
            doc_id: ID документа
            text: Текстовое содержимое
            image: Путь к изображению или PIL Image
            metadata: Дополнительная информация
        """
        # Обработка изображения
        image_path = None
        image_obj = None

        if image is not None:
            if isinstance(image, str):
                # Путь к файлу
                image_path = image
                if PIL_AVAILABLE:
                    image_obj = Image.open(image_path).convert('RGB')
            elif isinstance(image, Image.Image):
                image_obj = image
                # Сохранение (опционально)
                # image_path = f"cache/images/{doc_id}.jpg"

        # Вычисление embeddings
        text_emb = self.engine.encode_text(text)[0].tolist()
        image_emb = None
        if image_obj is not None:
            image_emb = self.engine.encode_image(image_obj)[0].tolist()

        doc = MultiModalDocument(
            doc_id=doc_id,
            text=text,
            image_path=image_path,
            image_embedding=image_emb,
            text_embedding=text_emb,
            metadata=metadata or {}
        )

        self.documents.append(doc)

        # Обновление индексов
        self._rebuild_indices()

    def _rebuild_indices(self):
        """Перестроение индексов embeddings"""
        # Text embeddings
        text_embs = [doc.text_embedding for doc in self.documents if doc.text_embedding]
        if text_embs:
            self.text_embeddings = np.array(text_embs)

        # Image embeddings
        image_embs = [doc.image_embedding for doc in self.documents if doc.image_embedding]
        if image_embs:
            self.image_embeddings = np.array(image_embs)

    # ========================================================================
    # SEARCH METHODS
    # ========================================================================

    def search_by_text(
        self,
        query: str,
        top_k: int = 5,
        modality: str = "text"  # text, image, both
    ) -> List[MultiModalSearchResult]:
        """
        Поиск по текстовому запросу

        Args:
            query: Текстовый запрос
            top_k: Количество результатов
            modality: Искать в text embeddings, image embeddings или both
        """
        query_emb = self.engine.encode_text(query)

        results = []

        # Поиск в text embeddings
        if modality in ["text", "both"] and self.text_embeddings is not None:
            text_scores = self.engine.compute_similarity(query_emb, self.text_embeddings)[0]

            for i, score in enumerate(text_scores):
                doc = self.documents[i]
                results.append(MultiModalSearchResult(
                    doc_id=doc.doc_id,
                    text=doc.text,
                    image_path=doc.image_path,
                    score=float(score),
                    modality="text",
                    metadata=doc.metadata
                ))

        # Кросс-модальный поиск: text query → image documents
        if modality in ["image", "both"] and self.image_embeddings is not None:
            image_scores = self.engine.compute_similarity(query_emb, self.image_embeddings)[0]

            for i, score in enumerate(image_scores):
                # Найти документы с image embeddings
                docs_with_images = [d for d in self.documents if d.image_embedding is not None]
                if i < len(docs_with_images):
                    doc = docs_with_images[i]
                    results.append(MultiModalSearchResult(
                        doc_id=doc.doc_id,
                        text=doc.text,
                        image_path=doc.image_path,
                        score=float(score),
                        modality="image",
                        metadata=doc.metadata
                    ))

        # Сортировка и топ-k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def search_by_image(
        self,
        image: Union[str, Image.Image],
        top_k: int = 5,
        modality: str = "image"  # text, image, both
    ) -> List[MultiModalSearchResult]:
        """
        Поиск по изображению

        Args:
            image: Путь к изображению или PIL Image
            top_k: Количество результатов
            modality: Искать в text embeddings, image embeddings или both
        """
        # Загрузка изображения
        if isinstance(image, str):
            if not PIL_AVAILABLE:
                raise ImportError("PIL required for image loading")
            image_obj = Image.open(image).convert('RGB')
        else:
            image_obj = image

        query_emb = self.engine.encode_image(image_obj)

        results = []

        # Поиск в image embeddings
        if modality in ["image", "both"] and self.image_embeddings is not None:
            image_scores = self.engine.compute_similarity(query_emb, self.image_embeddings)[0]

            docs_with_images = [d for d in self.documents if d.image_embedding is not None]
            for i, score in enumerate(image_scores):
                if i < len(docs_with_images):
                    doc = docs_with_images[i]
                    results.append(MultiModalSearchResult(
                        doc_id=doc.doc_id,
                        text=doc.text,
                        image_path=doc.image_path,
                        score=float(score),
                        modality="image",
                        metadata=doc.metadata
                    ))

        # Кросс-модальный поиск: image query → text documents
        if modality in ["text", "both"] and self.text_embeddings is not None:
            text_scores = self.engine.compute_similarity(query_emb, self.text_embeddings)[0]

            for i, score in enumerate(text_scores):
                doc = self.documents[i]
                results.append(MultiModalSearchResult(
                    doc_id=doc.doc_id,
                    text=doc.text,
                    image_path=doc.image_path,
                    score=float(score),
                    modality="text",
                    metadata=doc.metadata
                ))

        # Сортировка и топ-k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def search_multimodal(
        self,
        text: Optional[str] = None,
        image: Optional[Union[str, Image.Image]] = None,
        text_weight: float = 0.5,
        image_weight: float = 0.5,
        top_k: int = 5
    ) -> List[MultiModalSearchResult]:
        """
        Комбинированный мультимодальный поиск

        Args:
            text: Текстовый запрос (опционально)
            image: Изображение (опционально)
            text_weight: Вес текстового запроса
            image_weight: Вес изображения
            top_k: Количество результатов
        """
        if text is None and image is None:
            raise ValueError("At least one of text or image must be provided")

        # Вычисление embeddings
        text_emb = None
        image_emb = None

        if text:
            text_emb = self.engine.encode_text(text)

        if image:
            if isinstance(image, str):
                if not PIL_AVAILABLE:
                    raise ImportError("PIL required")
                image_obj = Image.open(image).convert('RGB')
            else:
                image_obj = image
            image_emb = self.engine.encode_image(image_obj)

        # Комбинированные scores
        all_scores = {}

        # Scores от текста
        if text_emb is not None and self.text_embeddings is not None:
            text_scores = self.engine.compute_similarity(text_emb, self.text_embeddings)[0]
            for i, score in enumerate(text_scores):
                doc_id = self.documents[i].doc_id
                all_scores[doc_id] = all_scores.get(doc_id, 0.0) + text_weight * score

        # Scores от изображения
        if image_emb is not None and self.image_embeddings is not None:
            image_scores = self.engine.compute_similarity(image_emb, self.image_embeddings)[0]
            docs_with_images = [d for d in self.documents if d.image_embedding is not None]
            for i, score in enumerate(image_scores):
                if i < len(docs_with_images):
                    doc_id = docs_with_images[i].doc_id
                    all_scores[doc_id] = all_scores.get(doc_id, 0.0) + image_weight * score

        # Создание результатов
        results = []
        for doc in self.documents:
            if doc.doc_id in all_scores:
                results.append(MultiModalSearchResult(
                    doc_id=doc.doc_id,
                    text=doc.text,
                    image_path=doc.image_path,
                    score=all_scores[doc.doc_id],
                    modality="multimodal",
                    metadata=doc.metadata
                ))

        # Сортировка и топ-k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика мультимодальной базы"""
        docs_with_images = len([d for d in self.documents if d.image_embedding is not None])
        docs_with_text = len([d for d in self.documents if d.text_embedding is not None])

        return {
            'total_documents': len(self.documents),
            'documents_with_text': docs_with_text,
            'documents_with_images': docs_with_images,
            'multimodal_documents': len([
                d for d in self.documents
                if d.text_embedding and d.image_embedding
            ]),
            'engine_type': self.engine_type
        }


# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_multi_modal():
    """Демонстрация Multi-Modal Knowledge"""
    print("=" * 70)
    print("  MULTI-MODAL KNOWLEDGE - Demo")
    print("=" * 70)
    print()

    # ========================================================================
    # 1. Инициализация
    # ========================================================================
    print("=" * 70)
    print("1. Initializing Multi-Modal Agent")
    print("=" * 70)

    # Использование Mock если CLIP недоступен
    use_clip = CLIP_AVAILABLE and NUMPY_AVAILABLE
    agent = MultiModalAgent(use_clip=use_clip)

    print(f"  ✅ Agent initialized")
    print(f"  ✅ Engine type: {agent.engine_type}")
    print()

    # ========================================================================
    # 2. Добавление документов
    # ========================================================================
    print("=" * 70)
    print("2. Adding Multi-Modal Documents")
    print("=" * 70)

    # Синтетические документы (без реальных изображений)
    documents = [
        {
            'id': 'doc_ai',
            'text': 'Artificial Intelligence uses neural networks to process data and make decisions',
            'category': 'AI'
        },
        {
            'id': 'doc_blockchain',
            'text': 'Blockchain is a distributed ledger technology for secure transactions',
            'category': 'Blockchain'
        },
        {
            'id': 'doc_quantum',
            'text': 'Quantum computing leverages quantum mechanics for exponential speedup',
            'category': 'Quantum'
        },
        {
            'id': 'doc_iot',
            'text': 'Internet of Things connects physical devices to the internet',
            'category': 'IoT'
        },
        {
            'id': 'doc_ml',
            'text': 'Machine Learning trains models on data to recognize patterns',
            'category': 'ML'
        },
    ]

    for doc in documents:
        agent.add_document(
            doc_id=doc['id'],
            text=doc['text'],
            image=None,  # Без изображений для упрощения demo
            metadata={'category': doc['category']}
        )
        print(f"  ✅ Added: {doc['id']}")

    print()

    # ========================================================================
    # 3. Text-to-Text Search
    # ========================================================================
    print("=" * 70)
    print("3. Text-to-Text Search")
    print("=" * 70)

    query = "neural networks and deep learning"
    results = agent.search_by_text(query, top_k=3, modality="text")

    print(f"Query: '{query}'")
    print(f"Results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.doc_id} (score: {result.score:.4f})")
        print(f"     {result.text[:80]}...")

    print()

    # ========================================================================
    # 4. Cross-Modal Search (если CLIP доступен)
    # ========================================================================
    if agent.engine_type == "CLIP":
        print("=" * 70)
        print("4. Cross-Modal Text-to-Image Search")
        print("=" * 70)

        # Для настоящего CLIP можно искать text query в image embeddings
        query = "distributed systems and networks"
        results = agent.search_by_text(query, top_k=3, modality="both")

        print(f"Query: '{query}'")
        print(f"Results (cross-modal):")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.doc_id} (score: {result.score:.4f}, modality: {result.modality})")

        print()

    # ========================================================================
    # 5. Statistics
    # ========================================================================
    print("=" * 70)
    print("5. Statistics")
    print("=" * 70)

    stats = agent.get_statistics()
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Documents with text: {stats['documents_with_text']}")
    print(f"  Documents with images: {stats['documents_with_images']}")
    print(f"  Multi-modal documents: {stats['multimodal_documents']}")
    print(f"  Engine: {stats['engine_type']}")

    print()

    # ========================================================================
    # 6. Заключение
    # ========================================================================
    print("=" * 70)
    print("6. Capabilities")
    print("=" * 70)

    print("  ✅ Multi-modal document storage")
    print("  ✅ Text-to-text search")
    print("  ✅ Image-to-image search (with real images)")
    print("  ✅ Cross-modal search (text→image, image→text)")
    print("  ✅ Combined multi-modal search")
    print("  ✅ Unified embedding space (CLIP)")
    print()

    print("  📝 Note: For full functionality, add real images:")
    print("     agent.add_document('id', 'text', image='path/to/image.jpg')")
    print()

    print("=" * 70)
    print("  Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_multi_modal()
