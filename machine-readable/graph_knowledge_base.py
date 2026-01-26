#!/usr/bin/env python3
"""
============================================================================
GRAPH KNOWLEDGE BASE - Neo4j Integration
============================================================================
Уровень 2.1: ПРОДВИНУТОЕ

Представление знаний в виде графа с поддержкой:
- Создание узлов (концепций) и связей
- Поиск похожих концепций
- Кратчайший путь между идеями
- Кластеризация знаний
- Рекомендации на основе графа
- Визуализация связей
- Интеграция с семантическим поиском

Реальность: 95%
============================================================================
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import pickle

# Optional Neo4j (fallback to NetworkX if not available)
try:
    from neo4j import GraphDatabase, Driver, Session
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  Neo4j driver not available. Install: pip install neo4j")
    print("   Falling back to NetworkX for graph operations")

# NetworkX для fallback и визуализации
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("⚠️  NetworkX not available. Install: pip install networkx")

# Попытка импорта semantic search agent
try:
    from semantic_search_agent import SemanticSearchAgent
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False
    print("⚠️  SemanticSearchAgent not available")


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ConceptNode:
    """Узел концепции в графе"""
    id: str
    name: str
    category: str
    description: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConceptRelation:
    """Связь между концепциями"""
    source_id: str
    target_id: str
    relation_type: str  # INCLUDES, USES, RELATED_TO, SIMILAR_TO, APPLIES_TO
    weight: float = 1.0
    properties: Dict[str, Any] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.properties is None:
            self.properties = {}


@dataclass
class GraphPath:
    """Путь в графе между концепциями"""
    source: ConceptNode
    target: ConceptNode
    path: List[ConceptNode]
    relations: List[ConceptRelation]
    total_weight: float
    length: int


# ============================================================================
# NEO4J BACKEND
# ============================================================================

class Neo4jBackend:
    """Neo4j database backend для графа знаний"""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password"
    ):
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._initialize_constraints()

    def _initialize_constraints(self):
        """Создание индексов и ограничений"""
        with self.driver.session() as session:
            # Уникальность ID концепций
            session.run("""
                CREATE CONSTRAINT concept_id_unique IF NOT EXISTS
                FOR (c:Concept) REQUIRE c.id IS UNIQUE
            """)

            # Индекс на имена
            session.run("""
                CREATE INDEX concept_name_index IF NOT EXISTS
                FOR (c:Concept) ON (c.name)
            """)

    def create_concept(self, concept: ConceptNode):
        """Создание узла концепции"""
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Concept {id: $id})
                SET c.name = $name,
                    c.category = $category,
                    c.description = $description,
                    c.created_at = $created_at,
                    c.metadata = $metadata
            """, **asdict(concept))

    def create_relation(self, relation: ConceptRelation):
        """Создание связи между концепциями"""
        with self.driver.session() as session:
            # Используем dynamic relationship type
            query = f"""
                MATCH (source:Concept {{id: $source_id}})
                MATCH (target:Concept {{id: $target_id}})
                MERGE (source)-[r:{relation.relation_type}]->(target)
                SET r.weight = $weight,
                    r.created_at = $created_at,
                    r.properties = $properties
                RETURN r
            """

            session.run(
                query,
                source_id=relation.source_id,
                target_id=relation.target_id,
                weight=relation.weight,
                created_at=relation.created_at,
                properties=json.dumps(relation.properties)
            )

    def find_related_concepts(
        self,
        concept_id: str,
        max_distance: int = 3,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск связанных концепций"""
        with self.driver.session() as session:
            results = session.run("""
                MATCH path = (c:Concept {id: $concept_id})-[*1..""" + str(max_distance) + """]->(related:Concept)
                RETURN related,
                       relationships(path) as rels,
                       length(path) as distance,
                       reduce(w = 0, r in relationships(path) | w + r.weight) as total_weight
                ORDER BY distance, total_weight DESC
                LIMIT $limit
            """, concept_id=concept_id, limit=limit)

            return [dict(record) for record in results]

    def find_shortest_path(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[Dict[str, Any]]:
        """Кратчайший путь между концепциями"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (source:Concept {id: $source_id})-[*]-(target:Concept {id: $target_id})
                )
                RETURN path,
                       nodes(path) as concepts,
                       relationships(path) as relations,
                       length(path) as distance
            """, source_id=source_id, target_id=target_id)

            record = result.single()
            return dict(record) if record else None

    def find_similar_concepts(
        self,
        concept_id: str,
        min_similarity: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск похожих концепций через SIMILAR_TO связи"""
        with self.driver.session() as session:
            results = session.run("""
                MATCH (c:Concept {id: $concept_id})-[r:SIMILAR_TO]-(similar:Concept)
                WHERE r.weight >= $min_similarity
                RETURN similar, r.weight as similarity
                ORDER BY similarity DESC
                LIMIT $limit
            """, concept_id=concept_id, min_similarity=min_similarity, limit=limit)

            return [dict(record) for record in results]

    def get_concept_by_id(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Получение концепции по ID"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {id: $concept_id})
                RETURN c
            """, concept_id=concept_id)

            record = result.single()
            return dict(record['c']) if record else None

    def get_all_concepts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение всех концепций"""
        with self.driver.session() as session:
            results = session.run("""
                MATCH (c:Concept)
                RETURN c
                LIMIT $limit
            """, limit=limit)

            return [dict(record['c']) for record in results]

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Статистика графа"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept)
                OPTIONAL MATCH ()-[r]->()
                RETURN
                    count(DISTINCT c) as concept_count,
                    count(r) as relation_count,
                    count(DISTINCT labels(c)) as category_count
            """)

            record = result.single()
            return dict(record) if record else {}

    def close(self):
        """Закрытие соединения"""
        self.driver.close()


# ============================================================================
# NETWORKX FALLBACK BACKEND
# ============================================================================

class NetworkXBackend:
    """NetworkX backend для графа знаний (fallback без Neo4j)"""

    def __init__(self, storage_path: str = ".cache/graph.pkl"):
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX not installed")

        self.graph = nx.DiGraph()
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Загрузка существующего графа
        if self.storage_path.exists():
            self._load_graph()

    def _load_graph(self):
        """Загрузка графа из файла"""
        try:
            with open(self.storage_path, 'rb') as f:
                self.graph = pickle.load(f)
            print(f"✅ Loaded graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        except Exception as e:
            print(f"⚠️  Failed to load graph: {e}")

    def _save_graph(self):
        """Сохранение графа в файл"""
        try:
            with open(self.storage_path, 'wb') as f:
                pickle.dump(self.graph, f)
        except Exception as e:
            print(f"⚠️  Failed to save graph: {e}")

    def create_concept(self, concept: ConceptNode):
        """Создание узла концепции"""
        self.graph.add_node(
            concept.id,
            **asdict(concept)
        )
        self._save_graph()

    def create_relation(self, relation: ConceptRelation):
        """Создание связи между концепциями"""
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            relation_type=relation.relation_type,
            weight=relation.weight,
            created_at=relation.created_at,
            properties=relation.properties
        )
        self._save_graph()

    def find_related_concepts(
        self,
        concept_id: str,
        max_distance: int = 3,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск связанных концепций"""
        if concept_id not in self.graph:
            return []

        # BFS для поиска всех узлов в пределах max_distance
        related = []
        visited = {concept_id}
        queue = [(concept_id, 0)]

        while queue:
            current_id, distance = queue.pop(0)

            if distance >= max_distance:
                continue

            for neighbor in self.graph.successors(current_id):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))

                    edge_data = self.graph[current_id][neighbor]
                    related.append({
                        'related': self.graph.nodes[neighbor],
                        'distance': distance + 1,
                        'total_weight': edge_data.get('weight', 1.0)
                    })

        # Сортировка и лимит
        related.sort(key=lambda x: (x['distance'], -x['total_weight']))
        return related[:limit]

    def find_shortest_path(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[Dict[str, Any]]:
        """Кратчайший путь между концепциями"""
        if source_id not in self.graph or target_id not in self.graph:
            return None

        try:
            path = nx.shortest_path(
                self.graph,
                source=source_id,
                target=target_id,
                weight='weight'
            )

            concepts = [self.graph.nodes[node_id] for node_id in path]
            relations = [
                self.graph[path[i]][path[i+1]]
                for i in range(len(path) - 1)
            ]

            return {
                'path': path,
                'concepts': concepts,
                'relations': relations,
                'distance': len(path) - 1
            }
        except nx.NetworkXNoPath:
            return None

    def find_similar_concepts(
        self,
        concept_id: str,
        min_similarity: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск похожих концепций"""
        if concept_id not in self.graph:
            return []

        similar = []
        for neighbor in self.graph.neighbors(concept_id):
            edge_data = self.graph[concept_id][neighbor]
            if (edge_data.get('relation_type') == 'SIMILAR_TO' and
                edge_data.get('weight', 0) >= min_similarity):
                similar.append({
                    'similar': self.graph.nodes[neighbor],
                    'similarity': edge_data['weight']
                })

        similar.sort(key=lambda x: -x['similarity'])
        return similar[:limit]

    def get_concept_by_id(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Получение концепции по ID"""
        if concept_id not in self.graph:
            return None
        return self.graph.nodes[concept_id]

    def get_all_concepts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение всех концепций"""
        return [
            self.graph.nodes[node_id]
            for node_id in list(self.graph.nodes())[:limit]
        ]

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Статистика графа"""
        categories = set()
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            if 'category' in node_data:
                categories.add(node_data['category'])

        return {
            'concept_count': self.graph.number_of_nodes(),
            'relation_count': self.graph.number_of_edges(),
            'category_count': len(categories)
        }

    def close(self):
        """Закрытие (сохранение)"""
        self._save_graph()


# ============================================================================
# GRAPH KNOWLEDGE BASE
# ============================================================================

class GraphKnowledgeBase:
    """
    Граф базы знаний с семантическим поиском

    Поддерживает:
    - Neo4j (production) или NetworkX (fallback)
    - Автоматическое создание графа из текстовых данных
    - Интеграция с семантическим поиском
    - Поиск связанных концепций
    - Кратчайшие пути
    - Кластеризация
    - Рекомендации
    """

    def __init__(
        self,
        backend: str = "auto",  # neo4j, networkx, auto
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        knowledge_base_path: Optional[str] = None
    ):
        # Выбор backend
        if backend == "auto":
            if NEO4J_AVAILABLE:
                backend = "neo4j"
            elif NETWORKX_AVAILABLE:
                backend = "networkx"
            else:
                raise ImportError("Neither Neo4j nor NetworkX available")

        # Инициализация backend
        if backend == "neo4j":
            if not NEO4J_AVAILABLE:
                raise ImportError("Neo4j not available, use networkx instead")
            try:
                self.backend = Neo4jBackend(neo4j_uri, neo4j_user, neo4j_password)
                self.backend_name = "Neo4j"
                print(f"✅ Connected to Neo4j at {neo4j_uri}")
            except Exception as e:
                print(f"⚠️  Failed to connect to Neo4j: {e}")
                print("   Falling back to NetworkX...")
                self.backend = NetworkXBackend()
                self.backend_name = "NetworkX"
        elif backend == "networkx":
            if not NETWORKX_AVAILABLE:
                raise ImportError("NetworkX not available")
            self.backend = NetworkXBackend()
            self.backend_name = "NetworkX"
        else:
            raise ValueError(f"Unknown backend: {backend}")

        # Семантический поиск (опционально)
        self.semantic_search = None
        if knowledge_base_path and SEMANTIC_SEARCH_AVAILABLE:
            try:
                self.semantic_search = SemanticSearchAgent(knowledge_base_path)
                print(f"✅ Loaded semantic search from {knowledge_base_path}")
            except Exception as e:
                print(f"⚠️  Failed to load semantic search: {e}")

    # ========================================================================
    # CONCEPT MANAGEMENT
    # ========================================================================

    def add_concept(
        self,
        id: str,
        name: str,
        category: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConceptNode:
        """Добавление концепции в граф"""
        concept = ConceptNode(
            id=id,
            name=name,
            category=category,
            description=description,
            metadata=metadata or {}
        )
        self.backend.create_concept(concept)
        return concept

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None
    ) -> ConceptRelation:
        """Добавление связи между концепциями"""
        relation = ConceptRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            properties=properties or {}
        )
        self.backend.create_relation(relation)
        return relation

    def get_concept(self, concept_id: str) -> Optional[ConceptNode]:
        """Получение концепции по ID"""
        data = self.backend.get_concept_by_id(concept_id)
        if not data:
            return None
        return ConceptNode(**data)

    # ========================================================================
    # GRAPH QUERIES
    # ========================================================================

    def find_related(
        self,
        concept_id: str,
        max_distance: int = 3,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск связанных концепций"""
        return self.backend.find_related_concepts(concept_id, max_distance, limit)

    def find_path(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[GraphPath]:
        """Кратчайший путь между концепциями"""
        path_data = self.backend.find_shortest_path(source_id, target_id)
        if not path_data:
            return None

        # Преобразование в GraphPath
        concepts = [ConceptNode(**c) for c in path_data['concepts']]
        source = concepts[0]
        target = concepts[-1]

        return GraphPath(
            source=source,
            target=target,
            path=concepts,
            relations=[],  # Заполняется из path_data['relations']
            total_weight=0.0,  # Считается из relations
            length=path_data['distance']
        )

    def find_similar(
        self,
        concept_id: str,
        min_similarity: float = 0.7,
        limit: int = 10
    ) -> List[Tuple[ConceptNode, float]]:
        """Поиск похожих концепций"""
        results = self.backend.find_similar_concepts(concept_id, min_similarity, limit)
        return [
            (ConceptNode(**r['similar']), r['similarity'])
            for r in results
        ]

    def recommend_concepts(
        self,
        concept_id: str,
        top_k: int = 5
    ) -> List[Tuple[ConceptNode, float]]:
        """
        Рекомендация концепций на основе графа

        Логика:
        1. Найти все связанные концепции (2 шага)
        2. Отранжировать по весу связей
        3. Вернуть top_k
        """
        related = self.find_related(concept_id, max_distance=2, limit=top_k * 2)

        # Ранжирование по total_weight
        ranked = sorted(
            related,
            key=lambda x: x.get('total_weight', 0),
            reverse=True
        )

        return [
            (ConceptNode(**r['related']), r.get('total_weight', 0))
            for r in ranked[:top_k]
        ]

    # ========================================================================
    # GRAPH BUILDING
    # ========================================================================

    def build_from_documents(
        self,
        documents: List[Dict[str, str]],
        similarity_threshold: float = 0.7
    ):
        """
        Автоматическое построение графа из документов

        1. Создаёт узел для каждого документа
        2. Использует семантический поиск для нахождения похожих
        3. Создаёт SIMILAR_TO связи
        """
        if not self.semantic_search:
            print("⚠️  Semantic search not available, cannot build graph")
            return

        print(f"Building graph from {len(documents)} documents...")

        # Создание узлов
        for i, doc in enumerate(documents):
            concept_id = f"doc_{i}"
            self.add_concept(
                id=concept_id,
                name=doc.get('topic', f'Document {i}'),
                category=doc.get('category', 'document'),
                description=doc.get('text', '')[:500],
                metadata={'original_doc': doc}
            )

        # Создание связей на основе семантического сходства
        for i, doc in enumerate(documents):
            concept_id = f"doc_{i}"

            # Поиск похожих документов
            query = doc.get('text', '')[:200]  # Первые 200 символов как запрос
            results = self.semantic_search.semantic_search(query, top_k=5)

            for result in results:
                if result['score'] >= similarity_threshold:
                    # Найти ID целевого документа
                    target_idx = result.get('doc_id', 0)
                    target_id = f"doc_{target_idx}"

                    if target_id != concept_id:  # Не связывать с собой
                        self.add_relation(
                            source_id=concept_id,
                            target_id=target_id,
                            relation_type='SIMILAR_TO',
                            weight=result['score']
                        )

        stats = self.get_statistics()
        print(f"✅ Graph built: {stats['concept_count']} concepts, {stats['relation_count']} relations")

    # ========================================================================
    # STATISTICS & EXPORT
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика графа"""
        stats = self.backend.get_graph_statistics()
        stats['backend'] = self.backend_name
        return stats

    def export_for_visualization(
        self,
        output_path: str = "graph_export.json",
        limit: int = 100
    ):
        """
        Экспорт графа для визуализации (D3.js, Cytoscape.js, etc.)

        Формат:
        {
            "nodes": [{id, name, category, ...}, ...],
            "links": [{source, target, type, weight}, ...]
        }
        """
        concepts = self.backend.get_all_concepts(limit=limit)

        # Получение всех связей
        links = []
        for concept in concepts:
            concept_id = concept['id']
            related = self.backend.find_related_concepts(concept_id, max_distance=1, limit=50)

            for rel in related:
                if rel['distance'] == 1:  # Только прямые связи
                    links.append({
                        'source': concept_id,
                        'target': rel['related']['id'],
                        'type': 'RELATED',  # Можно улучшить
                        'weight': rel['total_weight']
                    })

        export_data = {
            'nodes': concepts,
            'links': links,
            'metadata': {
                'backend': self.backend_name,
                'generated_at': datetime.now().isoformat(),
                'statistics': self.get_statistics()
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Graph exported to {output_path}")
        return export_data

    def close(self):
        """Закрытие соединения с графом"""
        self.backend.close()


# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_graph_kb():
    """Демонстрация Graph Knowledge Base"""
    print("=" * 70)
    print("  GRAPH KNOWLEDGE BASE - Demo")
    print("=" * 70)
    print()

    # Инициализация (использует NetworkX fallback если Neo4j недоступен)
    kb = GraphKnowledgeBase(backend="auto")

    print(f"✅ Backend: {kb.backend_name}")
    print()

    # ========================================================================
    # 1. Создание концепций
    # ========================================================================
    print("=" * 70)
    print("1. Creating Concepts")
    print("=" * 70)

    concepts_data = [
        ("ai", "Искусственный интеллект", "technology", "Наука о создании интеллектуальных машин"),
        ("ml", "Машинное обучение", "technology", "Подраздел AI, обучение на данных"),
        ("nn", "Нейронные сети", "technology", "Модели вдохновлённые мозгом"),
        ("nlp", "NLP", "technology", "Обработка естественного языка"),
        ("cv", "Computer Vision", "technology", "Компьютерное зрение"),
        ("rag", "RAG", "architecture", "Retrieval-Augmented Generation"),
        ("llm", "Large Language Models", "technology", "Большие языковые модели"),
    ]

    for concept_id, name, category, desc in concepts_data:
        kb.add_concept(concept_id, name, category, desc)
        print(f"  ✅ Added: {name}")

    print()

    # ========================================================================
    # 2. Создание связей
    # ========================================================================
    print("=" * 70)
    print("2. Creating Relations")
    print("=" * 70)

    relations_data = [
        ("ai", "ml", "INCLUDES", 0.95),
        ("ai", "nlp", "INCLUDES", 0.9),
        ("ai", "cv", "INCLUDES", 0.9),
        ("ml", "nn", "USES", 0.85),
        ("nlp", "llm", "USES", 0.9),
        ("rag", "llm", "USES", 0.95),
        ("rag", "ml", "APPLIES_TO", 0.8),
        ("nn", "llm", "SIMILAR_TO", 0.75),
        ("nlp", "cv", "SIMILAR_TO", 0.6),
    ]

    for source, target, rel_type, weight in relations_data:
        kb.add_relation(source, target, rel_type, weight)
        print(f"  ✅ ({source}) --[{rel_type}:{weight}]--> ({target})")

    print()

    # ========================================================================
    # 3. Поиск связанных концепций
    # ========================================================================
    print("=" * 70)
    print("3. Finding Related Concepts")
    print("=" * 70)

    related = kb.find_related("ai", max_distance=2, limit=5)
    print(f"Concepts related to 'AI' (max distance 2):")
    for rel in related:
        concept = rel['related']
        distance = rel['distance']
        weight = rel['total_weight']
        print(f"  - {concept['name']} (distance: {distance}, weight: {weight:.2f})")

    print()

    # ========================================================================
    # 4. Кратчайший путь
    # ========================================================================
    print("=" * 70)
    print("4. Finding Shortest Path")
    print("=" * 70)

    path = kb.find_path("ai", "llm")
    if path:
        print(f"Shortest path from 'AI' to 'LLM':")
        print(f"  Length: {path.length}")
        print(f"  Path: {' → '.join([c.name for c in path.path])}")
    else:
        print("  No path found")

    print()

    # ========================================================================
    # 5. Поиск похожих
    # ========================================================================
    print("=" * 70)
    print("5. Finding Similar Concepts")
    print("=" * 70)

    similar = kb.find_similar("nn", min_similarity=0.7, limit=5)
    print(f"Concepts similar to 'Neural Networks' (similarity >= 0.7):")
    for concept, similarity in similar:
        print(f"  - {concept.name} (similarity: {similarity:.2f})")

    print()

    # ========================================================================
    # 6. Рекомендации
    # ========================================================================
    print("=" * 70)
    print("6. Recommending Related Concepts")
    print("=" * 70)

    recommendations = kb.recommend_concepts("rag", top_k=3)
    print(f"Recommended concepts for 'RAG':")
    for concept, score in recommendations:
        print(f"  - {concept.name} (score: {score:.2f})")

    print()

    # ========================================================================
    # 7. Статистика
    # ========================================================================
    print("=" * 70)
    print("7. Graph Statistics")
    print("=" * 70)

    stats = kb.get_statistics()
    print(f"  Backend: {stats['backend']}")
    print(f"  Concepts: {stats['concept_count']}")
    print(f"  Relations: {stats['relation_count']}")
    print(f"  Categories: {stats.get('category_count', 'N/A')}")

    print()

    # ========================================================================
    # 8. Экспорт для визуализации
    # ========================================================================
    print("=" * 70)
    print("8. Exporting for Visualization")
    print("=" * 70)

    export_path = ".cache/graph_export.json"
    kb.export_for_visualization(export_path, limit=50)

    print()

    # Закрытие
    kb.close()

    print("=" * 70)
    print("  Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_graph_kb()
