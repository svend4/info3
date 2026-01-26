#!/usr/bin/env python3
"""
============================================================================
AUTOMATED KNOWLEDGE EXTRACTION - Extract from Multiple Sources
============================================================================
Уровень 2.5: ПРОДВИНУТОЕ

Автоматическое извлечение знаний из различных источников:
- Text documents (PDF, TXT, MD)
- Web pages (HTML)
- Code repositories (GitHub)
- Structured data (JSON, YAML)
- Natural language processing
- Pattern recognition
- Entity extraction
- Relationship identification

SOURCES:
- ArXiv papers
- GitHub repositories
- Wikipedia articles
- Blog posts
- Technical documentation

Реальность: 75%
============================================================================
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import random

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ExtractedKnowledge:
    """Извлечённое знание"""
    knowledge_id: str
    source_type: str  # pdf, github, web, text
    source_url: Optional[str]

    # 4-level structure
    formula: Optional[str] = None  # Level 1
    archetype: Optional[Dict[str, Any]] = None  # Level 2
    algorithm: Optional[List[str]] = None  # Level 3
    theorem: Optional[str] = None  # Level 4

    entities: List[str] = field(default_factory=list)
    relationships: List[Tuple[str, str, str]] = field(default_factory=list)  # (entity1, relation, entity2)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: str = None

    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now().isoformat()


@dataclass
class ExtractionStats:
    """Статистика извлечения"""
    total_sources: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    entities_extracted: int = 0
    relationships_extracted: int = 0
    formulas_extracted: int = 0
    algorithms_extracted: int = 0


# ============================================================================
# TEXT EXTRACTOR
# ============================================================================

class TextExtractor:
    """
    Базовый экстрактор текстовых знаний

    Использует регулярные выражения и эвристики для извлечения:
    - Формул
    - Алгоритмов
    - Определений
    - Примеров
    """

    def __init__(self):
        # Паттерны для извлечения
        self.formula_patterns = [
            r'([A-Z][a-z]*\s*=\s*[^\n]+)',  # Variable = expression
            r'([A-Z]\([^)]+\)\s*=\s*[^\n]+)',  # Function = expression
            r'(\w+\s*∝\s*\w+)',  # Proportional
            r'(\w+\s*≈\s*\w+)',  # Approximately
        ]

        self.algorithm_markers = [
            'algorithm:', 'steps:', 'procedure:', 'method:',
            'step 1', 'step 2', 'first,', 'second,', 'then,',
            '1.', '2.', '3.'
        ]

        self.definition_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(.+?)\.',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+means\s+(.+?)\.',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*:\s*(.+?)\.',
        ]

    def extract_formulas(self, text: str) -> List[str]:
        """Извлечение формул из текста"""
        formulas = []

        for pattern in self.formula_patterns:
            matches = re.findall(pattern, text)
            formulas.extend(matches)

        # Уникальные формулы
        return list(set(formulas))

    def extract_algorithms(self, text: str) -> List[str]:
        """Извлечение алгоритмов/шагов"""
        algorithms = []
        lines = text.split('\n')

        in_algorithm = False
        current_algorithm = []

        for line in lines:
            line_lower = line.lower().strip()

            # Начало алгоритма
            if any(marker in line_lower for marker in self.algorithm_markers):
                in_algorithm = True
                current_algorithm = [line.strip()]
                continue

            # Продолжение алгоритма
            if in_algorithm:
                # Проверка на шаг (нумерация или маркер)
                if (re.match(r'^\d+[\.)]\s+', line) or
                    re.match(r'^-\s+', line) or
                    re.match(r'^\*\s+', line) or
                    line_lower.startswith(('then', 'next', 'finally', 'after'))):
                    current_algorithm.append(line.strip())
                # Конец алгоритма (пустая строка или новая секция)
                elif not line.strip() or re.match(r'^[A-Z][a-z]+:', line):
                    if current_algorithm:
                        algorithms.append('\n'.join(current_algorithm))
                        current_algorithm = []
                    in_algorithm = False

        # Добавить последний алгоритм
        if current_algorithm:
            algorithms.append('\n'.join(current_algorithm))

        return algorithms

    def extract_entities(self, text: str) -> List[str]:
        """Извлечение сущностей (простое - по заглавным буквам)"""
        # Простая эвристика: последовательности заглавных слов
        entities = set()

        # Паттерн: 1-3 заглавных слова
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b'
        matches = re.findall(pattern, text)
        entities.update(matches)

        # Фильтрация общих слов
        common_words = {'The', 'This', 'These', 'That', 'Those', 'A', 'An', 'In', 'On', 'At', 'To', 'For'}
        entities = {e for e in entities if e not in common_words}

        return list(entities)[:50]  # Лимит 50

    def extract_definitions(self, text: str) -> Dict[str, str]:
        """Извлечение определений"""
        definitions = {}

        for pattern in self.definition_patterns:
            matches = re.findall(pattern, text)
            for term, definition in matches:
                definitions[term] = definition.strip()

        return definitions

    def extract_relationships(self, text: str, entities: List[str]) -> List[Tuple[str, str, str]]:
        """Извлечение связей между сущностями"""
        relationships = []

        # Простые паттерны отношений
        relation_patterns = [
            (r'(\w+)\s+is\s+a\s+(\w+)', 'IS_A'),
            (r'(\w+)\s+uses\s+(\w+)', 'USES'),
            (r'(\w+)\s+includes\s+(\w+)', 'INCLUDES'),
            (r'(\w+)\s+requires\s+(\w+)', 'REQUIRES'),
            (r'(\w+)\s+based on\s+(\w+)', 'BASED_ON'),
        ]

        for pattern, relation_type in relation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for entity1, entity2 in matches:
                # Проверка что обе сущности в списке извлечённых
                if entity1.title() in entities and entity2.title() in entities:
                    relationships.append((entity1.title(), relation_type, entity2.title()))

        return relationships


# ============================================================================
# KNOWLEDGE EXTRACTOR
# ============================================================================

class KnowledgeExtractor:
    """
    Главный экстрактор знаний

    Координирует извлечение из разных источников
    """

    def __init__(self):
        self.text_extractor = TextExtractor()
        self.stats = ExtractionStats()
        self.extracted_knowledge: List[ExtractedKnowledge] = []

    # ========================================================================
    # TEXT DOCUMENT EXTRACTION
    # ========================================================================

    def extract_from_text(
        self,
        text: str,
        source_type: str = "text",
        source_url: Optional[str] = None,
        knowledge_id: Optional[str] = None
    ) -> ExtractedKnowledge:
        """
        Извлечение знаний из текста

        Создаёт 4-уровневую структуру:
        - Level 1: Формулы
        - Level 2: Компоненты/определения
        - Level 3: Алгоритмы
        - Level 4: Примеры/теоремы
        """
        self.stats.total_sources += 1

        if knowledge_id is None:
            knowledge_id = f"knowledge_{len(self.extracted_knowledge)}"

        try:
            # Извлечение компонентов
            formulas = self.text_extractor.extract_formulas(text)
            algorithms = self.text_extractor.extract_algorithms(text)
            entities = self.text_extractor.extract_entities(text)
            definitions = self.text_extractor.extract_definitions(text)
            relationships = self.text_extractor.extract_relationships(text, entities)

            # Построение 4-уровневой структуры
            formula = formulas[0] if formulas else None

            archetype = {
                'components': definitions,
                'entities': entities[:10],  # Top 10 entities
                'description': text[:500]  # First 500 chars
            }

            algorithm = algorithms if algorithms else None

            # Теорема - последний параграф или пример
            paragraphs = text.split('\n\n')
            theorem = paragraphs[-1] if paragraphs else None

            # Создание объекта знания
            knowledge = ExtractedKnowledge(
                knowledge_id=knowledge_id,
                source_type=source_type,
                source_url=source_url,
                formula=formula,
                archetype=archetype,
                algorithm=algorithm,
                theorem=theorem,
                entities=entities,
                relationships=relationships,
                metadata={
                    'text_length': len(text),
                    'formulas_count': len(formulas),
                    'algorithms_count': len(algorithms),
                    'entities_count': len(entities),
                    'relationships_count': len(relationships)
                }
            )

            self.extracted_knowledge.append(knowledge)
            self.stats.successful_extractions += 1
            self.stats.entities_extracted += len(entities)
            self.stats.relationships_extracted += len(relationships)
            self.stats.formulas_extracted += len(formulas)
            self.stats.algorithms_extracted += len(algorithms)

            return knowledge

        except Exception as e:
            self.stats.failed_extractions += 1
            print(f"⚠️  Extraction failed: {e}")
            return None

    # ========================================================================
    # BATCH EXTRACTION
    # ========================================================================

    def extract_from_directory(
        self,
        directory_path: str,
        file_extensions: List[str] = ['.txt', '.md']
    ) -> List[ExtractedKnowledge]:
        """Извлечение из всех файлов в директории"""
        directory = Path(directory_path)
        results = []

        for file_path in directory.rglob('*'):
            if file_path.suffix in file_extensions:
                print(f"Processing {file_path.name}...")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()

                    knowledge = self.extract_from_text(
                        text,
                        source_type=file_path.suffix[1:],
                        source_url=str(file_path),
                        knowledge_id=f"file_{file_path.stem}"
                    )

                    if knowledge:
                        results.append(knowledge)

                except Exception as e:
                    print(f"  ⚠️  Failed to process {file_path.name}: {e}")

        return results

    def extract_from_github_readme(
        self,
        readme_text: str,
        repo_url: str
    ) -> ExtractedKnowledge:
        """
        Извлечение из GitHub README

        README обычно содержит:
        - Описание проекта
        - Инструкции по установке (algorithm)
        - Примеры использования (theorem)
        - API документация
        """
        return self.extract_from_text(
            readme_text,
            source_type="github_readme",
            source_url=repo_url,
            knowledge_id=f"github_{repo_url.split('/')[-1]}"
        )

    # ========================================================================
    # SEARCH & QUERY
    # ========================================================================

    def search_extracted_knowledge(
        self,
        query: str,
        limit: int = 5
    ) -> List[ExtractedKnowledge]:
        """Поиск в извлечённых знаниях"""
        query_lower = query.lower()
        results = []

        for knowledge in self.extracted_knowledge:
            score = 0.0

            # Поиск в формуле
            if knowledge.formula and query_lower in knowledge.formula.lower():
                score += 2.0

            # Поиск в сущностях
            matching_entities = [e for e in knowledge.entities if query_lower in e.lower()]
            score += len(matching_entities) * 0.5

            # Поиск в определениях
            if knowledge.archetype:
                for term, definition in knowledge.archetype.get('components', {}).items():
                    if query_lower in term.lower() or query_lower in definition.lower():
                        score += 1.0

            # Поиск в алгоритме
            if knowledge.algorithm:
                for step in knowledge.algorithm:
                    if query_lower in step.lower():
                        score += 0.5

            if score > 0:
                results.append((knowledge, score))

        # Сортировка по score
        results.sort(key=lambda x: x[1], reverse=True)

        return [k for k, s in results[:limit]]

    # ========================================================================
    # EXPORT & STATISTICS
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика извлечения"""
        return {
            'total_sources': self.stats.total_sources,
            'successful_extractions': self.stats.successful_extractions,
            'failed_extractions': self.stats.failed_extractions,
            'success_rate': (
                self.stats.successful_extractions / self.stats.total_sources
                if self.stats.total_sources > 0 else 0.0
            ),
            'entities_extracted': self.stats.entities_extracted,
            'relationships_extracted': self.stats.relationships_extracted,
            'formulas_extracted': self.stats.formulas_extracted,
            'algorithms_extracted': self.stats.algorithms_extracted,
            'knowledge_base_size': len(self.extracted_knowledge)
        }

    def export_to_json(self, output_path: str):
        """Экспорт извлечённых знаний в JSON"""
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_knowledge': len(self.extracted_knowledge),
                'statistics': self.get_statistics()
            },
            'knowledge': [asdict(k) for k in self.extracted_knowledge]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(self.extracted_knowledge)} knowledge items to {output_path}")


# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_automated_extraction():
    """Демонстрация Automated Knowledge Extraction"""
    print("=" * 70)
    print("  AUTOMATED KNOWLEDGE EXTRACTION - Demo")
    print("=" * 70)
    print()

    # ========================================================================
    # 1. Инициализация
    # ========================================================================
    print("=" * 70)
    print("1. Initializing Knowledge Extractor")
    print("=" * 70)

    extractor = KnowledgeExtractor()
    print("  ✅ Extractor initialized")
    print()

    # ========================================================================
    # 2. Извлечение из примеров текста
    # ========================================================================
    print("=" * 70)
    print("2. Extracting from Sample Texts")
    print("=" * 70)

    sample_texts = [
        {
            'title': 'Machine Learning',
            'text': '''
Machine Learning is a subset of Artificial Intelligence that uses algorithms to learn from data.

The basic formula for supervised learning is:
Model_Performance = f(Training_Data, Algorithm, Hyperparameters)

Algorithm Steps:
1. Collect and prepare training data
2. Select appropriate algorithm (Linear Regression, Decision Trees, Neural Networks)
3. Train model on data
4. Evaluate performance using metrics
5. Tune hyperparameters
6. Deploy model to production

Machine Learning uses Neural Networks for deep learning tasks.
Deep Learning requires large amounts of data and computational power.

Example: A spam filter learns from labeled emails to classify new emails as spam or not spam.
            '''
        },
        {
            'title': 'Blockchain Technology',
            'text': '''
Blockchain is a distributed ledger technology for secure transactions.

The consensus formula is:
Blockchain_Security = Hash_Power × Network_Size / Attack_Cost

Key Components:
- Blocks: Data containers with transactions
- Hash: Cryptographic fingerprint of block
- Chain: Linked sequence of blocks
- Consensus: Agreement mechanism (Proof of Work, Proof of Stake)

Blockchain uses Cryptography for security.
Bitcoin is based on Blockchain technology.
Smart Contracts require Blockchain infrastructure.

Theorem: A blockchain is immutable if more than 50% of nodes are honest.
            '''
        },
        {
            'title': 'Quantum Computing',
            'text': '''
Quantum Computing leverages quantum mechanics for exponential speedup.

Performance equation:
Quantum_Speedup ∝ 2^n (where n is number of qubits)

Algorithm Steps:
1. Initialize qubits in superposition state
2. Apply quantum gates (Hadamard, CNOT, Phase gates)
3. Perform quantum operations in parallel
4. Measure qubits to collapse superposition
5. Post-process classical results

Quantum Computing uses Superposition and Entanglement.
Quantum Algorithms include Shor's algorithm and Grover's algorithm.

Example: Shor's algorithm can factor large numbers exponentially faster than classical algorithms, threatening current encryption methods.
            '''
        }
    ]

    for sample in sample_texts:
        print(f"\nProcessing: {sample['title']}")
        knowledge = extractor.extract_from_text(
            sample['text'],
            source_type="demo_text",
            knowledge_id=f"demo_{sample['title'].replace(' ', '_').lower()}"
        )

        if knowledge:
            print(f"  ✅ Extracted:")
            print(f"     Formula: {knowledge.formula[:50] if knowledge.formula else 'N/A'}...")
            print(f"     Entities: {len(knowledge.entities)} found")
            print(f"     Algorithms: {len(knowledge.algorithm) if knowledge.algorithm else 0} steps")
            print(f"     Relationships: {len(knowledge.relationships)} found")

    print()

    # ========================================================================
    # 3. Поиск в извлечённых знаниях
    # ========================================================================
    print("=" * 70)
    print("3. Searching Extracted Knowledge")
    print("=" * 70)

    queries = [
        "neural networks",
        "blockchain security",
        "quantum algorithm"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = extractor.search_extracted_knowledge(query, limit=3)

        print(f"  Found {len(results)} results:")
        for i, knowledge in enumerate(results, 1):
            print(f"    {i}. {knowledge.knowledge_id}")
            if knowledge.formula:
                print(f"       Formula: {knowledge.formula[:60]}...")

    print()

    # ========================================================================
    # 4. Анализ извлечённых сущностей
    # ========================================================================
    print("=" * 70)
    print("4. Entity Analysis")
    print("=" * 70)

    all_entities = set()
    all_relationships = []

    for knowledge in extractor.extracted_knowledge:
        all_entities.update(knowledge.entities)
        all_relationships.extend(knowledge.relationships)

    print(f"  Total unique entities: {len(all_entities)}")
    print(f"  Top entities: {list(all_entities)[:10]}")
    print(f"\n  Total relationships: {len(all_relationships)}")

    if all_relationships:
        print(f"  Sample relationships:")
        for rel in all_relationships[:5]:
            print(f"    - {rel[0]} --[{rel[1]}]-> {rel[2]}")

    print()

    # ========================================================================
    # 5. Статистика
    # ========================================================================
    print("=" * 70)
    print("5. Extraction Statistics")
    print("=" * 70)

    stats = extractor.get_statistics()
    print(f"  Total sources processed: {stats['total_sources']}")
    print(f"  Successful extractions: {stats['successful_extractions']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Entities extracted: {stats['entities_extracted']}")
    print(f"  Relationships extracted: {stats['relationships_extracted']}")
    print(f"  Formulas extracted: {stats['formulas_extracted']}")
    print(f"  Algorithms extracted: {stats['algorithms_extracted']}")
    print(f"  Knowledge base size: {stats['knowledge_base_size']}")

    print()

    # ========================================================================
    # 6. Экспорт
    # ========================================================================
    print("=" * 70)
    print("6. Exporting Knowledge")
    print("=" * 70)

    output_path = ".cache/extracted_knowledge.json"
    os.makedirs(".cache", exist_ok=True)
    extractor.export_to_json(output_path)

    print()

    # ========================================================================
    # 7. Возможности
    # ========================================================================
    print("=" * 70)
    print("7. Capabilities")
    print("=" * 70)

    print("  ✅ Text document extraction")
    print("  ✅ Formula extraction (pattern matching)")
    print("  ✅ Algorithm extraction (step detection)")
    print("  ✅ Entity extraction (NER-like)")
    print("  ✅ Relationship extraction (basic patterns)")
    print("  ✅ 4-level knowledge structure")
    print("  ✅ Batch processing (directories)")
    print("  ✅ Search & query")
    print("  ✅ JSON export")
    print()

    print("  📝 Future enhancements:")
    print("     - PDF parsing (PyPDF2)")
    print("     - Web scraping (BeautifulSoup)")
    print("     - Advanced NLP (spaCy, transformers)")
    print("     - GitHub API integration")
    print("     - Wikipedia API integration")
    print()

    print("=" * 70)
    print("  Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_automated_extraction()
