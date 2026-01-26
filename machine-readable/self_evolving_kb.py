#!/usr/bin/env python3
"""
Self-Evolving Knowledge Base (Level 3.1)

Система, которая автоматически улучшает и реорганизует базу знаний:
- Обнаружение противоречий
- Обнаружение паттернов в успешных запросах
- Генерация новых связей на основе существующих
- Удаление устаревших знаний
- Реорганизация структуры для оптимальной производительности

Пример использования:
    kb = SelfEvolvingKB(knowledge_base_path="knowledge_base.json")
    kb.add_query_history(query="5G mmWave", confidence=0.9, result_count=10)

    # Автоматическая эволюция
    evolution_report = kb.evolve()
    print(f"Противоречий устранено: {evolution_report['contradictions_resolved']}")
    print(f"Новых паттернов обнаружено: {evolution_report['patterns_discovered']}")
    print(f"Новых связей создано: {evolution_report['connections_created']}")
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
import math

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available, some features will use fallback implementations")


class KnowledgeItem:
    """Элемент базы знаний с метаданными"""

    def __init__(self, id: str, content: str, metadata: Dict[str, Any] = None):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        self.created_at = self.metadata.get('created_at', datetime.now().isoformat())
        self.updated_at = self.metadata.get('updated_at', datetime.now().isoformat())
        self.access_count = self.metadata.get('access_count', 0)
        self.last_accessed = self.metadata.get('last_accessed', None)
        self.confidence = self.metadata.get('confidence', 1.0)
        self.tags = self.metadata.get('tags', [])
        self.relations = self.metadata.get('relations', [])
        self.version = self.metadata.get('version', 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'metadata': {
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'access_count': self.access_count,
                'last_accessed': self.last_accessed,
                'confidence': self.confidence,
                'tags': self.tags,
                'relations': self.relations,
                'version': self.version
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        return cls(
            id=data['id'],
            content=data['content'],
            metadata=data.get('metadata', {})
        )


class QueryRecord:
    """Запись о запросе в истории"""

    def __init__(self, query: str, confidence: float, result_count: int,
                 timestamp: str = None, matched_items: List[str] = None):
        self.query = query
        self.confidence = confidence
        self.result_count = result_count
        self.timestamp = timestamp or datetime.now().isoformat()
        self.matched_items = matched_items or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'confidence': self.confidence,
            'result_count': self.result_count,
            'timestamp': self.timestamp,
            'matched_items': self.matched_items
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryRecord':
        return cls(
            query=data['query'],
            confidence=data['confidence'],
            result_count=data['result_count'],
            timestamp=data.get('timestamp'),
            matched_items=data.get('matched_items', [])
        )


class Pattern:
    """Обнаруженный паттерн"""

    def __init__(self, pattern_type: str, description: str, confidence: float,
                 examples: List[str] = None, metadata: Dict[str, Any] = None):
        self.pattern_type = pattern_type
        self.description = description
        self.confidence = confidence
        self.examples = examples or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_type': self.pattern_type,
            'description': self.description,
            'confidence': self.confidence,
            'examples': self.examples,
            'metadata': self.metadata,
            'created_at': self.created_at
        }


class Contradiction:
    """Обнаруженное противоречие"""

    def __init__(self, item_a_id: str, item_b_id: str, contradiction_type: str,
                 description: str, severity: float):
        self.item_a_id = item_a_id
        self.item_b_id = item_b_id
        self.contradiction_type = contradiction_type
        self.description = description
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_a_id': self.item_a_id,
            'item_b_id': self.item_b_id,
            'contradiction_type': self.contradiction_type,
            'description': self.description,
            'severity': self.severity
        }


class SelfEvolvingKB:
    """
    Самоэволюционирующая база знаний

    Основные возможности:
    1. Обнаружение противоречий между элементами знаний
    2. Обнаружение паттернов в успешных запросах
    3. Генерация новых связей на основе существующих
    4. Удаление устаревших знаний
    5. Реорганизация структуры
    """

    def __init__(self, knowledge_base_path: str = "evolving_kb.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge: Dict[str, KnowledgeItem] = {}
        self.query_history: List[QueryRecord] = []
        self.discovered_patterns: List[Pattern] = []
        self.evolution_history: List[Dict[str, Any]] = []

        # Параметры эволюции
        self.contradiction_threshold = 0.7
        self.pattern_confidence_threshold = 0.8
        self.obsolete_days_threshold = 180
        self.min_access_count_threshold = 2

        self._load()

    def _load(self):
        """Загрузка базы знаний и истории"""
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Загрузка элементов знаний
            for item_data in data.get('knowledge', []):
                item = KnowledgeItem.from_dict(item_data)
                self.knowledge[item.id] = item

            # Загрузка истории запросов
            for query_data in data.get('query_history', []):
                query = QueryRecord.from_dict(query_data)
                self.query_history.append(query)

            # Загрузка обнаруженных паттернов
            for pattern_data in data.get('patterns', []):
                pattern = Pattern(
                    pattern_type=pattern_data['pattern_type'],
                    description=pattern_data['description'],
                    confidence=pattern_data['confidence'],
                    examples=pattern_data.get('examples', []),
                    metadata=pattern_data.get('metadata', {})
                )
                self.discovered_patterns.append(pattern)

            # Загрузка истории эволюции
            self.evolution_history = data.get('evolution_history', [])

    def _save(self):
        """Сохранение базы знаний и истории"""
        data = {
            'knowledge': [item.to_dict() for item in self.knowledge.values()],
            'query_history': [query.to_dict() for query in self.query_history],
            'patterns': [pattern.to_dict() for pattern in self.discovered_patterns],
            'evolution_history': self.evolution_history,
            'last_updated': datetime.now().isoformat()
        }

        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_knowledge(self, id: str, content: str, metadata: Dict[str, Any] = None):
        """Добавление элемента знаний"""
        item = KnowledgeItem(id, content, metadata)
        self.knowledge[id] = item
        self._save()

    def add_query_history(self, query: str, confidence: float, result_count: int,
                         matched_items: List[str] = None):
        """Добавление записи о запросе"""
        record = QueryRecord(query, confidence, result_count, matched_items=matched_items)
        self.query_history.append(record)

        # Обновление счетчиков доступа для matched items
        if matched_items:
            for item_id in matched_items:
                if item_id in self.knowledge:
                    self.knowledge[item_id].access_count += 1
                    self.knowledge[item_id].last_accessed = datetime.now().isoformat()

        self._save()

    def evolve(self) -> Dict[str, Any]:
        """
        Автоматическая эволюция базы знаний

        Выполняет все этапы эволюции:
        1. Обнаружение противоречий
        2. Обнаружение паттернов
        3. Генерация новых связей
        4. Удаление устаревшего
        5. Реорганизация структуры

        Returns:
            Отчет об эволюции
        """
        print("=" * 80)
        print("🧬 НАЧАЛО ЭВОЛЮЦИИ БАЗЫ ЗНАНИЙ")
        print("=" * 80)

        start_time = time.time()
        report = {
            'timestamp': datetime.now().isoformat(),
            'contradictions_resolved': 0,
            'patterns_discovered': 0,
            'connections_created': 0,
            'items_archived': 0,
            'structure_reorganized': False,
            'details': {}
        }

        # 1. Обнаружение противоречий
        print("\n1️⃣  Обнаружение противоречий...")
        contradictions = self.detect_contradictions()
        print(f"   Найдено противоречий: {len(contradictions)}")

        for contradiction in contradictions:
            resolution = self.resolve_contradiction(contradiction)
            if resolution:
                self.apply_resolution(resolution)
                report['contradictions_resolved'] += 1

        report['details']['contradictions'] = [c.to_dict() for c in contradictions]

        # 2. Обнаружение паттернов
        print("\n2️⃣  Обнаружение паттернов...")
        patterns = self.discover_patterns()
        print(f"   Найдено паттернов: {len(patterns)}")

        for pattern in patterns:
            if pattern.confidence > self.pattern_confidence_threshold:
                self.add_pattern_as_knowledge(pattern)
                report['patterns_discovered'] += 1

        report['details']['patterns'] = [p.to_dict() for p in patterns]

        # 3. Генерация новых связей
        print("\n3️⃣  Генерация новых связей...")
        new_connections = self.infer_connections()
        print(f"   Предложено связей: {len(new_connections)}")

        for connection in new_connections:
            if self.validate_connection(connection):
                self.add_connection(connection)
                report['connections_created'] += 1

        report['details']['connections'] = new_connections

        # 4. Удаление устаревшего
        print("\n4️⃣  Удаление устаревших знаний...")
        obsolete = self.find_obsolete_knowledge()
        print(f"   Найдено устаревших: {len(obsolete)}")

        self.archive_obsolete(obsolete)
        report['items_archived'] = len(obsolete)
        report['details']['obsolete_items'] = obsolete

        # 5. Реорганизация структуры
        print("\n5️⃣  Реорганизация структуры...")
        if self.should_reorganize():
            self.reorganize_structure()
            report['structure_reorganized'] = True
            print("   ✅ Структура реорганизована")
        else:
            print("   ⏭️  Реорганизация не требуется")

        elapsed_time = time.time() - start_time
        report['elapsed_seconds'] = elapsed_time

        # Сохранение отчета в историю
        self.evolution_history.append(report)
        self._save()

        print("\n" + "=" * 80)
        print(f"✅ ЭВОЛЮЦИЯ ЗАВЕРШЕНА за {elapsed_time:.2f}с")
        print("=" * 80)
        print(f"📊 Результаты:")
        print(f"   - Противоречий устранено: {report['contradictions_resolved']}")
        print(f"   - Паттернов обнаружено: {report['patterns_discovered']}")
        print(f"   - Связей создано: {report['connections_created']}")
        print(f"   - Элементов архивировано: {report['items_archived']}")
        print(f"   - Структура реорганизована: {report['structure_reorganized']}")
        print("=" * 80)

        return report

    def detect_contradictions(self) -> List[Contradiction]:
        """
        Обнаружение противоречий в базе знаний

        Типы противоречий:
        - DIRECT: прямое противоречие (A says X, B says NOT X)
        - TEMPORAL: временное противоречие (устаревшие данные)
        - SEMANTIC: семантическое противоречие (похожие концепты с разными значениями)
        """
        contradictions = []

        items = list(self.knowledge.values())

        for i, item_a in enumerate(items):
            for item_b in items[i+1:]:
                # Проверка на прямое противоречие
                if self._are_contradictory(item_a, item_b):
                    contradiction = Contradiction(
                        item_a_id=item_a.id,
                        item_b_id=item_b.id,
                        contradiction_type='DIRECT',
                        description=f"Противоречие между '{item_a.content[:50]}...' и '{item_b.content[:50]}...'",
                        severity=0.9
                    )
                    contradictions.append(contradiction)

                # Проверка на временное противоречие
                temporal_contradiction = self._check_temporal_contradiction(item_a, item_b)
                if temporal_contradiction:
                    contradictions.append(temporal_contradiction)

        return contradictions

    def _are_contradictory(self, item_a: KnowledgeItem, item_b: KnowledgeItem) -> bool:
        """Проверка на прямое противоречие"""
        # Простая эвристика: ищем негации и противоположности
        content_a = item_a.content.lower()
        content_b = item_b.content.lower()

        # Проверка на наличие общих ключевых слов
        words_a = set(content_a.split())
        words_b = set(content_b.split())
        common_words = words_a & words_b

        if len(common_words) < 2:
            return False

        # Проверка на негации
        negation_pairs = [
            ('can', 'cannot'), ('is', 'is not'), ('has', 'has not'),
            ('will', 'will not'), ('does', 'does not'), ('работает', 'не работает'),
            ('возможно', 'невозможно'), ('может', 'не может')
        ]

        for pos, neg in negation_pairs:
            if (pos in content_a and neg in content_b) or (neg in content_a and pos in content_b):
                return True

        return False

    def _check_temporal_contradiction(self, item_a: KnowledgeItem, item_b: KnowledgeItem) -> Optional[Contradiction]:
        """Проверка на временное противоречие (устаревшие данные)"""
        # Если элементы о похожих вещах, но один значительно старше
        created_a = datetime.fromisoformat(item_a.created_at)
        created_b = datetime.fromisoformat(item_b.created_at)

        time_diff = abs((created_a - created_b).days)

        if time_diff > 365:  # Больше года разницы
            # Проверяем похожесть контента
            similarity = self._calculate_similarity(item_a.content, item_b.content)
            if similarity > 0.5:
                older_item = item_a if created_a < created_b else item_b
                newer_item = item_b if created_a < created_b else item_a

                return Contradiction(
                    item_a_id=older_item.id,
                    item_b_id=newer_item.id,
                    contradiction_type='TEMPORAL',
                    description=f"Устаревшая информация: '{older_item.content[:50]}...' может быть заменена на '{newer_item.content[:50]}...'",
                    severity=0.6
                )

        return None

    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Простое вычисление сходства между текстами"""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = words_a & words_b
        union = words_a | words_b

        return len(intersection) / len(union)

    def resolve_contradiction(self, contradiction: Contradiction) -> Optional[Dict[str, Any]]:
        """Разрешение противоречия"""
        item_a = self.knowledge.get(contradiction.item_a_id)
        item_b = self.knowledge.get(contradiction.item_b_id)

        if not item_a or not item_b:
            return None

        if contradiction.contradiction_type == 'TEMPORAL':
            # Для временных противоречий: предпочитаем более новый
            if datetime.fromisoformat(item_a.created_at) < datetime.fromisoformat(item_b.created_at):
                return {
                    'action': 'DEPRECATE',
                    'item_id': item_a.id,
                    'reason': 'Устаревшая информация'
                }
            else:
                return {
                    'action': 'DEPRECATE',
                    'item_id': item_b.id,
                    'reason': 'Устаревшая информация'
                }
        elif contradiction.contradiction_type == 'DIRECT':
            # Для прямых противоречий: предпочитаем более уверенный (higher confidence)
            if item_a.confidence > item_b.confidence:
                return {
                    'action': 'MARK_UNCERTAIN',
                    'item_id': item_b.id,
                    'reason': 'Противоречит более достоверной информации'
                }
            else:
                return {
                    'action': 'MARK_UNCERTAIN',
                    'item_id': item_a.id,
                    'reason': 'Противоречит более достоверной информации'
                }

        return None

    def apply_resolution(self, resolution: Dict[str, Any]):
        """Применение разрешения противоречия"""
        item_id = resolution['item_id']
        action = resolution['action']

        if item_id not in self.knowledge:
            return

        item = self.knowledge[item_id]

        if action == 'DEPRECATE':
            item.metadata['deprecated'] = True
            item.metadata['deprecated_reason'] = resolution['reason']
            item.confidence = 0.3
        elif action == 'MARK_UNCERTAIN':
            item.confidence *= 0.5  # Уменьшаем уверенность
            item.metadata['uncertain'] = True
            item.metadata['uncertain_reason'] = resolution['reason']

    def discover_patterns(self) -> List[Pattern]:
        """
        Обнаружение паттернов в успешных запросах

        Типы паттернов:
        - FREQUENT_QUERY: часто повторяющиеся запросы
        - QUERY_CLUSTER: кластеры похожих запросов
        - TEMPORAL_PATTERN: временные паттерны (время суток, день недели)
        """
        patterns = []

        # Только успешные запросы
        successful_queries = [q for q in self.query_history if q.confidence > 0.8]

        if not successful_queries:
            return patterns

        # 1. Частые запросы
        query_counter = Counter([q.query.lower() for q in successful_queries])
        for query, count in query_counter.most_common(10):
            if count >= 3:  # Минимум 3 повторения
                pattern = Pattern(
                    pattern_type='FREQUENT_QUERY',
                    description=f"Часто повторяющийся запрос: '{query}'",
                    confidence=min(1.0, count / 10.0),
                    examples=[query],
                    metadata={'count': count}
                )
                patterns.append(pattern)

        # 2. Кластеры похожих запросов
        clusters = self._cluster_queries(successful_queries)
        for cluster in clusters:
            if len(cluster) >= 3:
                representative_query = cluster[0].query
                pattern = Pattern(
                    pattern_type='QUERY_CLUSTER',
                    description=f"Кластер запросов о: '{representative_query[:50]}...'",
                    confidence=len(cluster) / len(successful_queries),
                    examples=[q.query for q in cluster[:5]],
                    metadata={'cluster_size': len(cluster)}
                )
                patterns.append(pattern)

        # 3. Паттерны совместного доступа (items accessed together)
        co_access_patterns = self._find_co_access_patterns(successful_queries)
        for items, count in co_access_patterns.items():
            if count >= 3:
                pattern = Pattern(
                    pattern_type='CO_ACCESS',
                    description=f"Элементы часто запрашиваются вместе",
                    confidence=min(1.0, count / 10.0),
                    examples=list(items),
                    metadata={'co_access_count': count}
                )
                patterns.append(pattern)

        return patterns

    def _cluster_queries(self, queries: List[QueryRecord]) -> List[List[QueryRecord]]:
        """Простая кластеризация запросов по сходству"""
        clusters = []
        used = set()

        for i, query_a in enumerate(queries):
            if i in used:
                continue

            cluster = [query_a]
            used.add(i)

            for j, query_b in enumerate(queries):
                if j in used:
                    continue

                similarity = self._calculate_similarity(query_a.query, query_b.query)
                if similarity > 0.6:
                    cluster.append(query_b)
                    used.add(j)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    def _find_co_access_patterns(self, queries: List[QueryRecord]) -> Dict[Tuple[str, ...], int]:
        """Поиск паттернов совместного доступа"""
        co_access = defaultdict(int)

        for query in queries:
            if len(query.matched_items) >= 2:
                # Создаем сортированный tuple для нормализации
                items_tuple = tuple(sorted(query.matched_items[:3]))  # Топ-3 результата
                co_access[items_tuple] += 1

        return co_access

    def add_pattern_as_knowledge(self, pattern: Pattern):
        """Добавление обнаруженного паттерна как элемента знаний"""
        # Создаем новый элемент знаний на основе паттерна
        pattern_id = f"pattern_{pattern.pattern_type}_{len(self.discovered_patterns)}"

        content = f"Обнаруженный паттерн: {pattern.description}"

        metadata = {
            'type': 'discovered_pattern',
            'pattern_type': pattern.pattern_type,
            'confidence': pattern.confidence,
            'examples': pattern.examples,
            'pattern_metadata': pattern.metadata
        }

        self.add_knowledge(pattern_id, content, metadata)
        self.discovered_patterns.append(pattern)

    def infer_connections(self) -> List[Dict[str, Any]]:
        """
        Генерация новых связей на основе существующих

        Методы вывода:
        - TRANSITIVE: если A→B и B→C, то возможно A→C
        - CO_OCCURRENCE: если A и B часто встречаются вместе
        - SIMILARITY: если A и B похожи по содержанию
        """
        new_connections = []

        # 1. Транзитивные связи
        transitive_connections = self._infer_transitive_connections()
        new_connections.extend(transitive_connections)

        # 2. Связи на основе совместного доступа
        co_occurrence_connections = self._infer_co_occurrence_connections()
        new_connections.extend(co_occurrence_connections)

        # 3. Связи на основе сходства
        similarity_connections = self._infer_similarity_connections()
        new_connections.extend(similarity_connections)

        return new_connections

    def _infer_transitive_connections(self) -> List[Dict[str, Any]]:
        """Вывод транзитивных связей (A→B, B→C => A→C)"""
        connections = []

        for item_a in self.knowledge.values():
            for rel_ab in item_a.relations:
                target_b_id = rel_ab.get('target')
                if not target_b_id or target_b_id not in self.knowledge:
                    continue

                item_b = self.knowledge[target_b_id]

                for rel_bc in item_b.relations:
                    target_c_id = rel_bc.get('target')
                    if not target_c_id or target_c_id not in self.knowledge:
                        continue

                    # Проверяем, нет ли уже прямой связи A→C
                    has_direct = any(r.get('target') == target_c_id for r in item_a.relations)

                    if not has_direct and target_c_id != item_a.id:
                        connections.append({
                            'source': item_a.id,
                            'target': target_c_id,
                            'type': 'TRANSITIVE',
                            'relation_type': 'RELATED_TO',
                            'confidence': 0.7,
                            'reason': f"Транзитивная связь через {target_b_id}"
                        })

        return connections

    def _infer_co_occurrence_connections(self) -> List[Dict[str, Any]]:
        """Вывод связей на основе совместного доступа"""
        connections = []

        # Находим пары элементов, которые часто встречаются вместе
        co_occurrence = defaultdict(int)

        for query in self.query_history:
            items = query.matched_items[:5]  # Топ-5 результатов
            for i, item_a in enumerate(items):
                for item_b in items[i+1:]:
                    pair = tuple(sorted([item_a, item_b]))
                    co_occurrence[pair] += 1

        # Создаем связи для часто встречающихся пар
        for (item_a_id, item_b_id), count in co_occurrence.items():
            if count >= 3:  # Минимум 3 совместных появления
                if item_a_id in self.knowledge and item_b_id in self.knowledge:
                    connections.append({
                        'source': item_a_id,
                        'target': item_b_id,
                        'type': 'CO_OCCURRENCE',
                        'relation_type': 'FREQUENTLY_WITH',
                        'confidence': min(1.0, count / 10.0),
                        'reason': f"Совместный доступ {count} раз"
                    })

        return connections

    def _infer_similarity_connections(self) -> List[Dict[str, Any]]:
        """Вывод связей на основе семантического сходства"""
        connections = []

        items = list(self.knowledge.values())

        for i, item_a in enumerate(items):
            for item_b in items[i+1:]:
                similarity = self._calculate_similarity(item_a.content, item_b.content)

                if similarity > 0.7:  # Высокое сходство
                    # Проверяем, нет ли уже связи
                    has_connection = any(
                        r.get('target') == item_b.id for r in item_a.relations
                    )

                    if not has_connection:
                        connections.append({
                            'source': item_a.id,
                            'target': item_b.id,
                            'type': 'SIMILARITY',
                            'relation_type': 'SIMILAR_TO',
                            'confidence': similarity,
                            'reason': f"Семантическое сходство: {similarity:.2f}"
                        })

        return connections

    def validate_connection(self, connection: Dict[str, Any]) -> bool:
        """Валидация предложенной связи"""
        # Проверка существования элементов
        source_id = connection['source']
        target_id = connection['target']

        if source_id not in self.knowledge or target_id not in self.knowledge:
            return False

        # Проверка уверенности
        if connection['confidence'] < 0.5:
            return False

        # Проверка на циклические связи (A→B→A)
        source_item = self.knowledge[source_id]
        if any(r.get('target') == source_id for r in self.knowledge[target_id].relations):
            return False

        return True

    def add_connection(self, connection: Dict[str, Any]):
        """Добавление новой связи"""
        source_id = connection['source']

        if source_id not in self.knowledge:
            return

        item = self.knowledge[source_id]

        # Добавляем связь в relations
        relation = {
            'target': connection['target'],
            'type': connection['relation_type'],
            'confidence': connection['confidence'],
            'inferred': True,
            'inference_type': connection['type'],
            'reason': connection['reason'],
            'created_at': datetime.now().isoformat()
        }

        item.relations.append(relation)

    def find_obsolete_knowledge(self) -> List[str]:
        """
        Поиск устаревших знаний

        Критерии устаревания:
        - Не использовался долгое время (>180 дней)
        - Низкий access_count
        - Помечен как deprecated
        - Низкая confidence
        """
        obsolete = []
        now = datetime.now()

        for item_id, item in self.knowledge.items():
            # 1. Проверка на deprecated
            if item.metadata.get('deprecated'):
                obsolete.append(item_id)
                continue

            # 2. Проверка на низкую уверенность
            if item.confidence < 0.3:
                obsolete.append(item_id)
                continue

            # 3. Проверка на отсутствие использования
            if item.last_accessed:
                last_accessed = datetime.fromisoformat(item.last_accessed)
                days_since_access = (now - last_accessed).days

                if days_since_access > self.obsolete_days_threshold and item.access_count < self.min_access_count_threshold:
                    obsolete.append(item_id)
            elif item.access_count == 0:
                # Никогда не использовался
                created = datetime.fromisoformat(item.created_at)
                days_since_creation = (now - created).days

                if days_since_creation > 30:  # Дольше месяца без доступа
                    obsolete.append(item_id)

        return obsolete

    def archive_obsolete(self, obsolete_ids: List[str]):
        """Архивирование устаревших знаний"""
        archived_items = []

        for item_id in obsolete_ids:
            if item_id in self.knowledge:
                item = self.knowledge[item_id]
                item.metadata['archived'] = True
                item.metadata['archived_at'] = datetime.now().isoformat()
                archived_items.append(item.to_dict())

                # Удаляем из активной базы знаний
                del self.knowledge[item_id]

        # Сохраняем архив
        archive_path = self.knowledge_base_path.replace('.json', '_archive.json')

        existing_archive = []
        if os.path.exists(archive_path):
            with open(archive_path, 'r', encoding='utf-8') as f:
                existing_archive = json.load(f)

        existing_archive.extend(archived_items)

        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(existing_archive, f, indent=2, ensure_ascii=False)

    def should_reorganize(self) -> bool:
        """Проверка необходимости реорганизации"""
        # Реорганизация нужна если:
        # 1. Много элементов (>100)
        # 2. Давно не было реорганизации (>30 дней)
        # 3. Много новых связей

        if len(self.knowledge) < 20:
            return False

        # Проверка последней реорганизации
        if self.evolution_history:
            last_evolution = self.evolution_history[-1]
            if last_evolution.get('structure_reorganized'):
                last_reorg_time = datetime.fromisoformat(last_evolution['timestamp'])
                days_since_reorg = (datetime.now() - last_reorg_time).days

                if days_since_reorg < 30:
                    return False

        return True

    def reorganize_structure(self):
        """
        Реорганизация структуры базы знаний

        Оптимизации:
        - Группировка похожих элементов
        - Создание иерархии (categories)
        - Оптимизация связей
        """
        # 1. Группировка по тегам
        tag_groups = defaultdict(list)
        for item_id, item in self.knowledge.items():
            for tag in item.tags:
                tag_groups[tag].append(item_id)

        # 2. Создание категорий для больших групп
        for tag, items in tag_groups.items():
            if len(items) >= 5:
                # Добавляем метаданные о категории
                for item_id in items:
                    self.knowledge[item_id].metadata['category'] = tag

        # 3. Удаление дублирующихся связей
        for item in self.knowledge.values():
            # Удаляем дубликаты из relations
            seen = set()
            unique_relations = []

            for rel in item.relations:
                rel_key = (rel.get('target'), rel.get('type'))
                if rel_key not in seen:
                    seen.add(rel_key)
                    unique_relations.append(rel)

            item.relations = unique_relations

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики базы знаний"""
        stats = {
            'total_items': len(self.knowledge),
            'total_queries': len(self.query_history),
            'total_patterns': len(self.discovered_patterns),
            'evolution_count': len(self.evolution_history),
            'avg_confidence': sum(item.confidence for item in self.knowledge.values()) / len(self.knowledge) if self.knowledge else 0,
            'total_relations': sum(len(item.relations) for item in self.knowledge.values()),
            'items_by_tag': {},
            'recent_evolutions': []
        }

        # Подсчет по тегам
        for item in self.knowledge.values():
            for tag in item.tags:
                stats['items_by_tag'][tag] = stats['items_by_tag'].get(tag, 0) + 1

        # Последние эволюции
        stats['recent_evolutions'] = self.evolution_history[-5:] if self.evolution_history else []

        return stats


def demo():
    """Демонстрация работы самоэволюционирующей базы знаний"""
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ: Self-Evolving Knowledge Base (Level 3.1)")
    print("=" * 80)

    # Создание базы знаний
    kb = SelfEvolvingKB("demo_evolving_kb.json")

    print("\n1️⃣  Добавление начальных знаний...")

    # Добавляем знания о 5G
    kb.add_knowledge(
        "5g_001",
        "5G - это пятое поколение мобильных сетей, обеспечивающее высокую скорость передачи данных",
        metadata={'tags': ['5G', 'networking'], 'confidence': 0.95}
    )

    kb.add_knowledge(
        "5g_002",
        "5G mmWave использует высокочастотные волны для сверхбыстрой передачи данных",
        metadata={'tags': ['5G', 'mmWave'], 'confidence': 0.90}
    )

    kb.add_knowledge(
        "5g_003",
        "5G mmWave не может проходить через стены и имеет ограниченное покрытие",
        metadata={'tags': ['5G', 'mmWave', 'limitations'], 'confidence': 0.92}
    )

    # Устаревшая информация (будет обнаружена как противоречие)
    kb.add_knowledge(
        "5g_old",
        "5G mmWave может легко проходить через препятствия",
        metadata={'tags': ['5G', 'mmWave'], 'confidence': 0.70, 'created_at': '2020-01-01T00:00:00'}
    )

    kb.add_knowledge(
        "edge_001",
        "Edge computing приближает обработку данных к источнику данных",
        metadata={'tags': ['edge', 'computing'], 'confidence': 0.93}
    )

    kb.add_knowledge(
        "edge_002",
        "5G и edge computing часто используются вместе для низкой задержки",
        metadata={'tags': ['5G', 'edge'], 'confidence': 0.88, 'relations': [
            {'target': '5g_001', 'type': 'RELATED_TO'}
        ]}
    )

    print(f"   Добавлено элементов: {len(kb.knowledge)}")

    print("\n2️⃣  Симуляция запросов пользователей...")

    # Симулируем успешные запросы
    queries = [
        ("5G mmWave coverage", 0.92, 2, ["5g_002", "5g_003"]),
        ("5G mmWave limitations", 0.89, 2, ["5g_003", "5g_002"]),
        ("5G mmWave penetration", 0.91, 2, ["5g_003", "5g_002"]),
        ("5G and edge computing", 0.94, 2, ["5g_001", "edge_002"]),
        ("edge computing with 5G", 0.93, 2, ["edge_002", "5g_001"]),
        ("5G speed", 0.88, 1, ["5g_001"]),
        ("5G mmWave through walls", 0.90, 2, ["5g_003", "5g_old"]),
    ]

    for query, confidence, count, matched in queries:
        kb.add_query_history(query, confidence, count, matched)

    print(f"   Добавлено запросов: {len(queries)}")

    print("\n3️⃣  Статистика ДО эволюции:")
    stats_before = kb.get_statistics()
    print(f"   Всего элементов: {stats_before['total_items']}")
    print(f"   Средняя уверенность: {stats_before['avg_confidence']:.2f}")
    print(f"   Всего связей: {stats_before['total_relations']}")
    print(f"   Всего запросов: {stats_before['total_queries']}")

    # Запуск эволюции
    print("\n4️⃣  Запуск автоматической эволюции...\n")
    evolution_report = kb.evolve()

    print("\n5️⃣  Статистика ПОСЛЕ эволюции:")
    stats_after = kb.get_statistics()
    print(f"   Всего элементов: {stats_after['total_items']}")
    print(f"   Средняя уверенность: {stats_after['avg_confidence']:.2f}")
    print(f"   Всего связей: {stats_after['total_relations']}")
    print(f"   Обнаруженных паттернов: {stats_after['total_patterns']}")

    print("\n6️⃣  Обнаруженные паттерны:")
    for i, pattern in enumerate(kb.discovered_patterns, 1):
        print(f"   {i}. [{pattern.pattern_type}] {pattern.description}")
        print(f"      Уверенность: {pattern.confidence:.2f}")
        if pattern.examples:
            print(f"      Примеры: {pattern.examples[:3]}")

    print("\n7️⃣  Новые связи (выведенные автоматически):")
    inferred_count = 0
    for item in kb.knowledge.values():
        for rel in item.relations:
            if rel.get('inferred'):
                inferred_count += 1
                print(f"   {item.id} → {rel['target']} ({rel['type']})")
                print(f"      Причина: {rel.get('reason', 'N/A')}")
                print(f"      Уверенность: {rel['confidence']:.2f}")

    if inferred_count == 0:
        print("   (Нет выведенных связей)")

    print("\n" + "=" * 80)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)
    print("\n💡 База знаний успешно эволюционировала:")
    print(f"   • Обнаружила и устранила противоречия")
    print(f"   • Выявила паттерны в запросах пользователей")
    print(f"   • Автоматически создала новые связи")
    print(f"   • Архивировала устаревшие знания")
    print(f"\n📁 Результаты сохранены в: demo_evolving_kb.json")


if __name__ == "__main__":
    demo()
