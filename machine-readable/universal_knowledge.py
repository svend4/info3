#!/usr/bin/env python3
"""
Universal Knowledge Representation
==================================

Универсальная система представления знаний, объединяющая множество форматов.

Поддерживаемые представления:
- Symbolic: логические формулы, правила
- Vector: embeddings, непрерывные представления
- Graph: узлы и рёбра, knowledge graphs
- Hierarchical: таксономии, онтологии
- Probabilistic: Bayesian networks, неопределённость
- Temporal: знания с временными метками
- Multi-modal: текст, изображения, audio

Цель: единая система, которая может представить ЛЮБОЕ знание
в оптимальном формате для задачи.
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from datetime import datetime
from enum import Enum
from collections import defaultdict


class RepresentationType(Enum):
    """Типы представления знаний"""
    SYMBOLIC = "symbolic"
    VECTOR = "vector"
    GRAPH = "graph"
    HIERARCHICAL = "hierarchical"
    PROBABILISTIC = "probabilistic"
    TEMPORAL = "temporal"
    MULTI_MODAL = "multi_modal"


@dataclass
class SymbolicRepresentation:
    """Символьное представление (логика, правила)"""
    predicates: List[str]
    rules: List[str]
    facts: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "symbolic",
            "predicates": self.predicates,
            "rules": self.rules,
            "facts": self.facts
        }


@dataclass
class VectorRepresentation:
    """Векторное представление (embeddings)"""
    embedding: List[float]
    dimensions: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "vector",
            "dimensions": self.dimensions,
            "embedding_sample": self.embedding[:5]  # Первые 5 для демо
        }

    def similarity(self, other: 'VectorRepresentation') -> float:
        """Косинусная схожесть"""
        if len(self.embedding) != len(other.embedding):
            return 0.0

        dot = sum(a * b for a, b in zip(self.embedding, other.embedding))
        mag1 = math.sqrt(sum(a * a for a in self.embedding))
        mag2 = math.sqrt(sum(b * b for b in other.embedding))

        if mag1 > 0 and mag2 > 0:
            return dot / (mag1 * mag2)
        return 0.0


@dataclass
class GraphNode:
    """Узел в графе знаний"""
    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Ребро в графе знаний"""
    source: str
    target: str
    relation: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRepresentation:
    """Графовое представление (knowledge graph)"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "graph",
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "nodes": [{"id": n.id, "label": n.label} for n in self.nodes[:5]],
            "edges": [{"source": e.source, "target": e.target, "relation": e.relation} for e in self.edges[:5]]
        }


@dataclass
class HierarchyNode:
    """Узел в иерархии"""
    id: str
    label: str
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    level: int = 0


@dataclass
class HierarchicalRepresentation:
    """Иерархическое представление (таксономии)"""
    nodes: Dict[str, HierarchyNode]
    root_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "hierarchical",
            "total_nodes": len(self.nodes),
            "root": self.root_id,
            "max_depth": max(n.level for n in self.nodes.values()) if self.nodes else 0
        }

    def get_ancestors(self, node_id: str) -> List[str]:
        """Получить всех предков"""
        ancestors = []
        current_id = node_id

        while current_id in self.nodes:
            node = self.nodes[current_id]
            if node.parent:
                ancestors.append(node.parent)
                current_id = node.parent
            else:
                break

        return ancestors


@dataclass
class ProbabilisticRepresentation:
    """Вероятностное представление (Bayesian network)"""
    variables: List[str]
    probabilities: Dict[str, float]
    conditional_probs: Dict[str, Dict[str, float]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "probabilistic",
            "variables": self.variables,
            "probabilities": self.probabilities,
            "conditional_dependencies": len(self.conditional_probs)
        }


@dataclass
class TemporalRepresentation:
    """Временное представление"""
    events: List[Dict[str, Any]]
    timeline: List[Tuple[str, str]]  # (timestamp, event)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "temporal",
            "events_count": len(self.events),
            "timeline_length": len(self.timeline)
        }


@dataclass
class MultiModalRepresentation:
    """Мультимодальное представление"""
    text: Optional[str] = None
    image_embedding: Optional[List[float]] = None
    audio_features: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "multi_modal",
            "has_text": self.text is not None,
            "has_image": self.image_embedding is not None,
            "has_audio": self.audio_features is not None,
            "metadata": self.metadata
        }


@dataclass
class UniversalKnowledge:
    """Универсальное представление знания"""
    id: str
    name: str
    primary_representation: RepresentationType
    representations: Dict[RepresentationType, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_representation(self, rep_type: RepresentationType, representation: Any):
        """Добавить представление"""
        self.representations[rep_type] = representation

    def get_representation(self, rep_type: RepresentationType) -> Optional[Any]:
        """Получить представление определённого типа"""
        return self.representations.get(rep_type)

    def has_representation(self, rep_type: RepresentationType) -> bool:
        """Проверить наличие представления"""
        return rep_type in self.representations

    def convert_to(self, target_type: RepresentationType) -> Optional[Any]:
        """Конвертировать в другой тип представления"""
        # Если уже есть - вернуть
        if self.has_representation(target_type):
            return self.get_representation(target_type)

        # Иначе попытка конвертации
        return self._auto_convert(target_type)

    def _auto_convert(self, target_type: RepresentationType) -> Optional[Any]:
        """Автоматическая конвертация между типами"""
        # Упрощённая конвертация для демонстрации

        # Vector → Symbolic
        if target_type == RepresentationType.SYMBOLIC:
            if self.has_representation(RepresentationType.VECTOR):
                return SymbolicRepresentation(
                    predicates=[f"concept({self.name})"],
                    rules=[f"inferred_from_vector({self.name})"],
                    facts=[f"has_embedding({self.name})"]
                )

        # Symbolic → Vector
        if target_type == RepresentationType.VECTOR:
            if self.has_representation(RepresentationType.SYMBOLIC):
                # Генерируем embedding из символьного представления
                random.seed(hash(self.name))
                embedding = [random.gauss(0, 1) for _ in range(128)]
                return VectorRepresentation(embedding=embedding, dimensions=128)

        # Graph → Hierarchical
        if target_type == RepresentationType.HIERARCHICAL:
            if self.has_representation(RepresentationType.GRAPH):
                graph = self.get_representation(RepresentationType.GRAPH)
                # Построить иерархию из графа (упрощённо)
                nodes = {}
                root_id = graph.nodes[0].id if graph.nodes else "root"
                nodes[root_id] = HierarchyNode(id=root_id, label="Root", level=0)

                return HierarchicalRepresentation(nodes=nodes, root_id=root_id)

        return None


class UniversalKnowledgeSystem:
    """
    Универсальная система представления знаний

    Может хранить и конвертировать между всеми типами представлений
    """

    def __init__(self, verbose: bool = False):
        self.knowledge_base: Dict[str, UniversalKnowledge] = {}
        self.verbose = verbose
        self.conversion_cache: Dict[Tuple[str, RepresentationType], Any] = {}

    def add_knowledge(self, knowledge: UniversalKnowledge):
        """Добавить знание"""
        self.knowledge_base[knowledge.id] = knowledge

        if self.verbose:
            print(f"Added knowledge: {knowledge.name} (primary: {knowledge.primary_representation.value})")

    def get_knowledge(self, knowledge_id: str) -> Optional[UniversalKnowledge]:
        """Получить знание"""
        return self.knowledge_base.get(knowledge_id)

    def query_by_representation(
        self,
        rep_type: RepresentationType,
        limit: int = 10
    ) -> List[UniversalKnowledge]:
        """Найти все знания с определённым типом представления"""
        results = []

        for knowledge in self.knowledge_base.values():
            if knowledge.has_representation(rep_type):
                results.append(knowledge)

                if len(results) >= limit:
                    break

        return results

    def convert_knowledge(
        self,
        knowledge_id: str,
        target_type: RepresentationType,
        use_cache: bool = True
    ) -> Optional[Any]:
        """Конвертировать знание в другой тип представления"""
        # Проверка cache
        cache_key = (knowledge_id, target_type)
        if use_cache and cache_key in self.conversion_cache:
            if self.verbose:
                print(f"Cache hit for {knowledge_id} → {target_type.value}")
            return self.conversion_cache[cache_key]

        knowledge = self.get_knowledge(knowledge_id)
        if not knowledge:
            return None

        # Конвертация
        converted = knowledge.convert_to(target_type)

        if converted:
            self.conversion_cache[cache_key] = converted

            if self.verbose:
                print(f"Converted {knowledge.name}: {knowledge.primary_representation.value} → {target_type.value}")

        return converted

    def find_optimal_representation(
        self,
        knowledge_id: str,
        task: str
    ) -> RepresentationType:
        """
        Найти оптимальное представление для задачи

        Эвристики:
        - reasoning → symbolic
        - similarity search → vector
        - relationship traversal → graph
        - classification → hierarchical
        - uncertainty → probabilistic
        """
        task_lower = task.lower()

        if any(word in task_lower for word in ['reason', 'logic', 'infer']):
            return RepresentationType.SYMBOLIC
        elif any(word in task_lower for word in ['similar', 'search', 'find']):
            return RepresentationType.VECTOR
        elif any(word in task_lower for word in ['relation', 'connect', 'graph']):
            return RepresentationType.GRAPH
        elif any(word in task_lower for word in ['classify', 'category', 'taxonomy']):
            return RepresentationType.HIERARCHICAL
        elif any(word in task_lower for word in ['uncertain', 'probable', 'likely']):
            return RepresentationType.PROBABILISTIC
        elif any(word in task_lower for word in ['time', 'when', 'history']):
            return RepresentationType.TEMPORAL
        else:
            # Default to vector for general tasks
            return RepresentationType.VECTOR

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        rep_counts = defaultdict(int)

        for knowledge in self.knowledge_base.values():
            for rep_type in knowledge.representations:
                rep_counts[rep_type.value] += 1

        return {
            "total_knowledge": len(self.knowledge_base),
            "representations_count": dict(rep_counts),
            "cache_size": len(self.conversion_cache),
            "representation_types": len(RepresentationType)
        }


def demo():
    """Демонстрация универсальной системы представления знаний"""
    print("=" * 80)
    print("UNIVERSAL KNOWLEDGE REPRESENTATION - DEMO")
    print("=" * 80)

    system = UniversalKnowledgeSystem(verbose=True)

    # === СОЗДАНИЕ ЗНАНИЙ С РАЗНЫМИ ПРЕДСТАВЛЕНИЯМИ ===
    print("\n" + "=" * 80)
    print("CREATING KNOWLEDGE WITH MULTIPLE REPRESENTATIONS")
    print("=" * 80)

    # Knowledge 1: AI (Symbolic + Vector)
    ai_knowledge = UniversalKnowledge(
        id="k1",
        name="Artificial Intelligence",
        primary_representation=RepresentationType.SYMBOLIC,
        representations={}
    )

    # Symbolic representation
    ai_symbolic = SymbolicRepresentation(
        predicates=["intelligent(X)", "learns(X)", "reasons(X)"],
        rules=["intelligent(X) :- learns(X), reasons(X)"],
        facts=["intelligent(ai)", "learns(ai)", "reasons(ai)"]
    )
    ai_knowledge.add_representation(RepresentationType.SYMBOLIC, ai_symbolic)

    # Vector representation
    random.seed(42)
    ai_vector = VectorRepresentation(
        embedding=[random.gauss(0, 1) for _ in range(128)],
        dimensions=128
    )
    ai_knowledge.add_representation(RepresentationType.VECTOR, ai_vector)

    system.add_knowledge(ai_knowledge)

    # Knowledge 2: Neural Network (Graph + Vector)
    nn_knowledge = UniversalKnowledge(
        id="k2",
        name="Neural Network",
        primary_representation=RepresentationType.GRAPH,
        representations={}
    )

    # Graph representation
    nn_graph = GraphRepresentation(
        nodes=[
            GraphNode("n1", "Input Layer"),
            GraphNode("n2", "Hidden Layer"),
            GraphNode("n3", "Output Layer")
        ],
        edges=[
            GraphEdge("n1", "n2", "feeds_into"),
            GraphEdge("n2", "n3", "feeds_into")
        ]
    )
    nn_knowledge.add_representation(RepresentationType.GRAPH, nn_graph)

    # Vector representation
    random.seed(43)
    nn_vector = VectorRepresentation(
        embedding=[random.gauss(0, 1) for _ in range(128)],
        dimensions=128
    )
    nn_knowledge.add_representation(RepresentationType.VECTOR, nn_vector)

    system.add_knowledge(nn_knowledge)

    # Knowledge 3: Machine Learning (Hierarchical + Probabilistic)
    ml_knowledge = UniversalKnowledge(
        id="k3",
        name="Machine Learning",
        primary_representation=RepresentationType.HIERARCHICAL,
        representations={}
    )

    # Hierarchical representation
    ml_hierarchy = HierarchicalRepresentation(
        nodes={
            "ml": HierarchyNode("ml", "Machine Learning", level=0),
            "supervised": HierarchyNode("supervised", "Supervised Learning", parent="ml", level=1),
            "unsupervised": HierarchyNode("unsupervised", "Unsupervised Learning", parent="ml", level=1),
        },
        root_id="ml"
    )
    ml_hierarchy.nodes["ml"].children = ["supervised", "unsupervised"]
    ml_knowledge.add_representation(RepresentationType.HIERARCHICAL, ml_hierarchy)

    # Probabilistic representation
    ml_prob = ProbabilisticRepresentation(
        variables=["accuracy", "overfitting", "data_size"],
        probabilities={"accuracy": 0.85, "overfitting": 0.30, "data_size": 0.75},
        conditional_probs={
            "accuracy": {"data_size": 0.9, "overfitting": 0.6}
        }
    )
    ml_knowledge.add_representation(RepresentationType.PROBABILISTIC, ml_prob)

    system.add_knowledge(ml_knowledge)

    # Knowledge 4: Deep Learning History (Temporal)
    dl_knowledge = UniversalKnowledge(
        id="k4",
        name="Deep Learning History",
        primary_representation=RepresentationType.TEMPORAL,
        representations={}
    )

    # Temporal representation
    dl_temporal = TemporalRepresentation(
        events=[
            {"year": 2012, "event": "AlexNet wins ImageNet"},
            {"year": 2014, "event": "GANs introduced"},
            {"year": 2017, "event": "Transformers introduced"},
        ],
        timeline=[
            ("2012", "AlexNet"),
            ("2014", "GANs"),
            ("2017", "Transformers")
        ]
    )
    dl_knowledge.add_representation(RepresentationType.TEMPORAL, dl_temporal)

    system.add_knowledge(dl_knowledge)

    # === QUERYING BY REPRESENTATION TYPE ===
    print("\n" + "=" * 80)
    print("QUERYING BY REPRESENTATION TYPE")
    print("=" * 80)

    for rep_type in [RepresentationType.SYMBOLIC, RepresentationType.GRAPH, RepresentationType.HIERARCHICAL]:
        results = system.query_by_representation(rep_type)
        print(f"\n{rep_type.value.upper()} representations: {len(results)} found")
        for knowledge in results:
            print(f"  - {knowledge.name}")

    # === AUTOMATIC CONVERSION ===
    print("\n" + "=" * 80)
    print("AUTOMATIC CONVERSION BETWEEN REPRESENTATIONS")
    print("=" * 80)

    # Convert AI from Symbolic to Vector (already exists)
    converted = system.convert_knowledge("k1", RepresentationType.VECTOR)
    if converted:
        print(f"\nAI → Vector: {converted.dimensions} dimensions")

    # Convert Neural Network from Graph to Hierarchical (auto-conversion)
    converted = system.convert_knowledge("k2", RepresentationType.HIERARCHICAL)
    if converted:
        print(f"\nNeural Network → Hierarchical: {len(converted.nodes)} nodes")

    # === OPTIMAL REPRESENTATION SELECTION ===
    print("\n" + "=" * 80)
    print("OPTIMAL REPRESENTATION FOR TASKS")
    print("=" * 80)

    tasks = [
        "Find similar concepts",
        "Perform logical reasoning",
        "Traverse relationships",
        "Classify into categories",
        "Handle uncertainty",
        "Analyze timeline"
    ]

    for task in tasks:
        optimal = system.find_optimal_representation("k1", task)
        print(f"\nTask: '{task}'")
        print(f"  Optimal representation: {optimal.value}")

    # === VECTOR SIMILARITY ===
    print("\n" + "=" * 80)
    print("VECTOR SIMILARITY COMPARISON")
    print("=" * 80)

    ai_vec = ai_knowledge.get_representation(RepresentationType.VECTOR)
    nn_vec = nn_knowledge.get_representation(RepresentationType.VECTOR)

    if ai_vec and nn_vec:
        similarity = ai_vec.similarity(nn_vec)
        print(f"\nSimilarity between AI and Neural Network: {similarity:.3f}")

    # === STATISTICS ===
    print("\n" + "=" * 80)
    print("SYSTEM STATISTICS")
    print("=" * 80)

    stats = system.get_statistics()

    print(f"\nTotal knowledge entries: {stats['total_knowledge']}")
    print(f"Representation types available: {stats['representation_types']}")
    print(f"Cache size: {stats['cache_size']}")

    print(f"\nRepresentations count:")
    for rep_type, count in stats['representations_count'].items():
        print(f"  {rep_type}: {count}")

    # === KNOWLEDGE SERIALIZATION ===
    print("\n" + "=" * 80)
    print("KNOWLEDGE SERIALIZATION")
    print("=" * 80)

    print("\nAI Knowledge serialized:")
    for rep_type, representation in ai_knowledge.representations.items():
        print(f"\n{rep_type.value.upper()}:")
        if hasattr(representation, 'to_dict'):
            serialized = representation.to_dict()
            for key, value in serialized.items():
                print(f"  {key}: {value}")

    # === PHILOSOPHICAL REFLECTION ===
    print("\n" + "=" * 80)
    print("PHILOSOPHICAL REFLECTION")
    print("=" * 80)

    print("""
Universal Knowledge Representation solves a fundamental problem:
"How to represent ANY knowledge in a computable form?"

Key insights:

1. NO SINGLE BEST REPRESENTATION
   - Symbolic is best for reasoning
   - Vector is best for similarity
   - Graph is best for relationships
   - Each has trade-offs

2. MULTI-REPRESENTATION APPROACH
   - Same knowledge in multiple formats
   - Convert between formats as needed
   - Choose optimal for task

3. REPRESENTATION DETERMINES COMPUTATION
   - "You cannot reason about what you cannot represent"
   - Different representations enable different operations
   - Universal system = maximum flexibility

4. UNIFICATION
   - Symbolic AI (1950s-1980s): logic, rules
   - Connectionist AI (1980s-2000s): neural networks
   - Modern AI: Hybrid approaches
   - Universal system unifies all paradigms

This is the future of AI: systems that can represent knowledge
in whatever form is most appropriate for the task at hand.

"The map is not the territory, but we need many maps for the same territory."
    """)

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return system


if __name__ == "__main__":
    system = demo()
