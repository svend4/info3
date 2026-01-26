#!/usr/bin/env python3
"""
Meta-Learning Across Domains
============================

Система обучения переносу знаний между доменами.

Основные компоненты:
- Извлечение абстрактных паттернов из специфичного знания
- Адаптация паттернов к новым доменам
- Few-shot learning для быстрой адаптации
- Transfer learning между доменами

Пример:
    Домен 1: 5G Сети
    Паттерн: "mmWave = высокая скорость, но малое покрытие"
    Абстракция: "Trade-off между производительностью и масштабом"

    Домен 2: Blockchain
    Применение: "Proof-of-Work = высокая безопасность, но низкая пропускная способность"
"""

import json
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from enum import Enum


class PatternType(Enum):
    """Типы абстрактных паттернов"""
    TRADE_OFF = "trade_off"  # Компромисс между двумя характеристиками
    CAUSALITY = "causality"  # Причинно-следственная связь
    DEPENDENCY = "dependency"  # Зависимость одного от другого
    INVERSE_RELATION = "inverse_relation"  # Обратная зависимость
    SCALING = "scaling"  # Масштабирование
    OPTIMIZATION = "optimization"  # Оптимизация параметров
    CONSTRAINT = "constraint"  # Ограничение
    HIERARCHY = "hierarchy"  # Иерархия компонентов


@dataclass
class Concept:
    """Концепт в домене"""
    name: str
    domain: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relations: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

    def similarity(self, other: 'Concept') -> float:
        """Семантическая схожесть концептов"""
        if not other:
            return 0.0

        # Простая схожесть на основе свойств
        shared_props = set(self.properties.keys()) & set(other.properties.keys())
        all_props = set(self.properties.keys()) | set(other.properties.keys())

        if not all_props:
            return 0.0

        return len(shared_props) / len(all_props)


@dataclass
class AbstractPattern:
    """Абстрактный паттерн, извлечённый из домена"""
    pattern_id: str
    pattern_type: PatternType
    source_domain: str
    template: str  # Абстрактный шаблон
    variables: List[str]  # Переменные в шаблоне
    constraints: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    examples: List[Dict[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def instantiate(self, bindings: Dict[str, str]) -> str:
        """Инстанцировать паттерн с конкретными значениями"""
        result = self.template
        for var, value in bindings.items():
            result = result.replace(f"{{{var}}}", value)
        return result

    def matches(self, statement: str, threshold: float = 0.6) -> bool:
        """Проверить, соответствует ли утверждение этому паттерну"""
        # Простая проверка на наличие ключевых слов
        template_words = set(self.template.lower().split())
        statement_words = set(statement.lower().split())

        # Удаляем переменные
        for var in self.variables:
            template_words.discard(f"{{{var.lower()}}}")

        if not template_words:
            return False

        overlap = len(template_words & statement_words) / len(template_words)
        return overlap >= threshold


@dataclass
class DomainKnowledge:
    """Знания о конкретном домене"""
    domain_name: str
    concepts: List[Concept] = field(default_factory=list)
    facts: List[str] = field(default_factory=list)
    patterns: List[AbstractPattern] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_concept(self, concept: Concept):
        """Добавить концепт в домен"""
        self.concepts.append(concept)

    def add_fact(self, fact: str):
        """Добавить факт в домен"""
        self.facts.append(fact)

    def get_concept(self, name: str) -> Optional[Concept]:
        """Получить концепт по имени"""
        for concept in self.concepts:
            if concept.name.lower() == name.lower():
                return concept
        return None

    def find_similar_concepts(self, concept: Concept, top_k: int = 3) -> List[Tuple[Concept, float]]:
        """Найти схожие концепты в домене"""
        similarities = []
        for c in self.concepts:
            if c.name != concept.name:
                sim = concept.similarity(c)
                similarities.append((c, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


@dataclass
class TransferResult:
    """Результат переноса знаний"""
    from_domain: str
    to_domain: str
    patterns_transferred: List[AbstractPattern]
    instantiated_facts: List[str]
    confidence: float
    transfer_time: str = field(default_factory=lambda: datetime.now().isoformat())

    def summary(self) -> Dict[str, Any]:
        """Краткое описание переноса"""
        return {
            "from": self.from_domain,
            "to": self.to_domain,
            "patterns_count": len(self.patterns_transferred),
            "facts_generated": len(self.instantiated_facts),
            "confidence": self.confidence,
            "time": self.transfer_time
        }


class MetaModel:
    """
    Мета-модель, которая обучается на множестве доменов
    и извлекает абстрактные паттерны
    """

    def __init__(self):
        self.abstract_patterns: List[AbstractPattern] = []
        self.domain_statistics: Dict[str, Dict[str, Any]] = {}
        self.pattern_success_rate: Dict[str, float] = {}  # pattern_id -> success_rate

    def extract_patterns_from_domain(self, domain: DomainKnowledge) -> List[AbstractPattern]:
        """Извлечь абстрактные паттерны из домена"""
        patterns = []

        # Анализ фактов для извлечения паттернов
        for fact in domain.facts:
            # Ищем trade-offs
            if "but" in fact.lower() or "however" in fact.lower():
                pattern = self._extract_tradeoff_pattern(fact, domain.domain_name)
                if pattern:
                    patterns.append(pattern)

            # Ищем причинно-следственные связи
            if "because" in fact.lower() or "leads to" in fact.lower() or "causes" in fact.lower():
                pattern = self._extract_causality_pattern(fact, domain.domain_name)
                if pattern:
                    patterns.append(pattern)

            # Ищем обратные зависимости
            if "more" in fact.lower() and "less" in fact.lower():
                pattern = self._extract_inverse_relation_pattern(fact, domain.domain_name)
                if pattern:
                    patterns.append(pattern)

            # Ищем ограничения
            if "limited" in fact.lower() or "constraint" in fact.lower() or "cannot" in fact.lower():
                pattern = self._extract_constraint_pattern(fact, domain.domain_name)
                if pattern:
                    patterns.append(pattern)

        # Обновляем глобальные паттерны
        for pattern in patterns:
            self.abstract_patterns.append(pattern)
            self.pattern_success_rate[pattern.pattern_id] = 0.5  # Initial success rate

        return patterns

    def _extract_tradeoff_pattern(self, fact: str, domain: str) -> Optional[AbstractPattern]:
        """Извлечь паттерн trade-off"""
        # Простой парсинг: "X = high Y, but low Z"
        fact_lower = fact.lower()

        if "but" in fact_lower:
            parts = fact_lower.split("but")
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()

                # Извлечь позитивное и негативное свойство
                positive_prop = None
                negative_prop = None

                if "high" in left or "good" in left or "fast" in left:
                    positive_prop = "high_performance"
                if "low" in right or "poor" in right or "small" in right:
                    negative_prop = "low_scale"

                if positive_prop and negative_prop:
                    pattern_id = f"tradeoff_{domain}_{len(self.abstract_patterns)}"
                    return AbstractPattern(
                        pattern_id=pattern_id,
                        pattern_type=PatternType.TRADE_OFF,
                        source_domain=domain,
                        template="{technology} provides {benefit}, but has {limitation}",
                        variables=["technology", "benefit", "limitation"],
                        constraints={
                            "benefit": "positive_property",
                            "limitation": "negative_property"
                        },
                        examples=[{"fact": fact}]
                    )

        return None

    def _extract_causality_pattern(self, fact: str, domain: str) -> Optional[AbstractPattern]:
        """Извлечь причинно-следственный паттерн"""
        fact_lower = fact.lower()

        if "leads to" in fact_lower or "causes" in fact_lower:
            pattern_id = f"causality_{domain}_{len(self.abstract_patterns)}"
            return AbstractPattern(
                pattern_id=pattern_id,
                pattern_type=PatternType.CAUSALITY,
                source_domain=domain,
                template="{cause} leads to {effect}",
                variables=["cause", "effect"],
                constraints={
                    "effect": "must_be_observable"
                },
                examples=[{"fact": fact}]
            )

        return None

    def _extract_inverse_relation_pattern(self, fact: str, domain: str) -> Optional[AbstractPattern]:
        """Извлечь паттерн обратной зависимости"""
        fact_lower = fact.lower()

        if "more" in fact_lower and "less" in fact_lower:
            pattern_id = f"inverse_{domain}_{len(self.abstract_patterns)}"
            return AbstractPattern(
                pattern_id=pattern_id,
                pattern_type=PatternType.INVERSE_RELATION,
                source_domain=domain,
                template="More {variable_x} leads to less {variable_y}",
                variables=["variable_x", "variable_y"],
                constraints={
                    "relationship": "inverse"
                },
                examples=[{"fact": fact}]
            )

        return None

    def _extract_constraint_pattern(self, fact: str, domain: str) -> Optional[AbstractPattern]:
        """Извлечь паттерн ограничения"""
        fact_lower = fact.lower()

        if "limited" in fact_lower or "cannot" in fact_lower:
            pattern_id = f"constraint_{domain}_{len(self.abstract_patterns)}"
            return AbstractPattern(
                pattern_id=pattern_id,
                pattern_type=PatternType.CONSTRAINT,
                source_domain=domain,
                template="{entity} has limitation in {aspect}",
                variables=["entity", "aspect"],
                constraints={
                    "limitation_type": "hard_constraint"
                },
                examples=[{"fact": fact}]
            )

        return None

    def find_applicable_patterns(self, target_domain: DomainKnowledge) -> List[AbstractPattern]:
        """Найти паттерны, применимые к целевому домену"""
        applicable = []

        for pattern in self.abstract_patterns:
            # Проверяем успешность паттерна
            success_rate = self.pattern_success_rate.get(pattern.pattern_id, 0.5)

            if success_rate > 0.3:  # Threshold для применимости
                # Проверяем, есть ли в целевом домене концепты для инстанциации
                if self._can_instantiate(pattern, target_domain):
                    applicable.append(pattern)

        return applicable

    def _can_instantiate(self, pattern: AbstractPattern, domain: DomainKnowledge) -> bool:
        """Проверить, можно ли инстанциировать паттерн в домене"""
        # Простая проверка: достаточно ли концептов в домене
        return len(domain.concepts) >= len(pattern.variables)

    def update_pattern_success(self, pattern_id: str, success: bool):
        """Обновить успешность паттерна"""
        if pattern_id in self.pattern_success_rate:
            current = self.pattern_success_rate[pattern_id]
            # Экспоненциальное скользящее среднее
            alpha = 0.3
            self.pattern_success_rate[pattern_id] = alpha * (1.0 if success else 0.0) + (1 - alpha) * current

    def adapt_to_domain(self, domain_examples: List[Dict[str, Any]]) -> 'DomainModel':
        """Быстрая адаптация к новому домену (few-shot)"""
        # Создаём domain model на основе небольшого количества примеров
        domain_model = DomainModel(
            domain_name=domain_examples[0].get('domain', 'unknown'),
            meta_model=self
        )

        # Быстрое обучение на примерах
        for example in domain_examples:
            if 'concept' in example:
                concept = Concept(
                    name=example['concept'],
                    domain=domain_model.domain_name,
                    properties=example.get('properties', {}),
                    examples=example.get('examples', [])
                )
                domain_model.knowledge.add_concept(concept)

            if 'fact' in example:
                domain_model.knowledge.add_fact(example['fact'])

        return domain_model


class DomainModel:
    """Модель для конкретного домена"""

    def __init__(self, domain_name: str, meta_model: MetaModel):
        self.domain_name = domain_name
        self.knowledge = DomainKnowledge(domain_name=domain_name)
        self.meta_model = meta_model
        self.trained_at = datetime.now().isoformat()

    def predict(self, query: str) -> Dict[str, Any]:
        """Предсказание для запроса"""
        # Простой поиск в фактах
        relevant_facts = []
        for fact in self.knowledge.facts:
            if any(word.lower() in fact.lower() for word in query.split()):
                relevant_facts.append(fact)

        # Поиск релевантных концептов
        relevant_concepts = []
        for concept in self.knowledge.concepts:
            if concept.name.lower() in query.lower():
                relevant_concepts.append(concept)

        confidence = min(1.0, (len(relevant_facts) + len(relevant_concepts)) * 0.2)

        return {
            "query": query,
            "domain": self.domain_name,
            "relevant_facts": relevant_facts,
            "relevant_concepts": [c.name for c in relevant_concepts],
            "confidence": confidence
        }

    def extract_patterns(self) -> List[AbstractPattern]:
        """Извлечь паттерны из знаний домена"""
        return self.meta_model.extract_patterns_from_domain(self.knowledge)


class MetaLearningAgent:
    """
    Агент для meta-learning across domains

    Умеет:
    - Обучаться на примерах из разных доменов
    - Извлекать абстрактные паттерны
    - Переносить знания между доменами
    - Быстро адаптироваться к новому домену (few-shot)
    """

    def __init__(self, verbose: bool = False):
        self.domain_models: Dict[str, DomainModel] = {}
        self.meta_model = MetaModel()
        self.verbose = verbose
        self.transfer_history: List[TransferResult] = []

    def learn_from_domain(self, domain: str, examples: List[Dict[str, Any]]) -> DomainModel:
        """
        Обучение на примерах из одного домена

        Args:
            domain: Название домена
            examples: Список примеров с концептами и фактами

        Returns:
            DomainModel для этого домена
        """
        if self.verbose:
            print(f"\n=== Learning from domain: {domain} ===")
            print(f"Examples: {len(examples)}")

        # Быстрая адаптация (few-shot)
        domain_model = self.meta_model.adapt_to_domain([
            {**ex, 'domain': domain} for ex in examples
        ])

        self.domain_models[domain] = domain_model

        # Извлечение паттернов из домена
        patterns = domain_model.extract_patterns()

        if self.verbose:
            print(f"Extracted patterns: {len(patterns)}")
            for pattern in patterns:
                print(f"  - {pattern.pattern_type.value}: {pattern.template}")

        # Обновление мета-модели
        self.meta_model.domain_statistics[domain] = {
            "concepts_count": len(domain_model.knowledge.concepts),
            "facts_count": len(domain_model.knowledge.facts),
            "patterns_count": len(patterns),
            "trained_at": domain_model.trained_at
        }

        return domain_model

    def transfer_knowledge(
        self,
        from_domain: str,
        to_domain: str,
        target_concepts: Optional[List[str]] = None
    ) -> TransferResult:
        """
        Перенос знаний между доменами

        Args:
            from_domain: Исходный домен
            to_domain: Целевой домен
            target_concepts: Концепты в целевом домене для инстанциации

        Returns:
            TransferResult с результатами переноса
        """
        if self.verbose:
            print(f"\n=== Transferring knowledge: {from_domain} → {to_domain} ===")

        # Проверка существования доменов
        if from_domain not in self.domain_models:
            raise ValueError(f"Source domain '{from_domain}' not found")
        if to_domain not in self.domain_models:
            raise ValueError(f"Target domain '{to_domain}' not found")

        source_model = self.domain_models[from_domain]
        target_model = self.domain_models[to_domain]

        # 1. Извлечение абстрактных паттернов из исходного домена
        abstract_patterns = self.extract_abstract_patterns(from_domain)

        if self.verbose:
            print(f"Abstract patterns from {from_domain}: {len(abstract_patterns)}")

        # 2. Адаптация паттернов к целевому домену
        adapted_patterns = self.adapt_patterns(abstract_patterns, to_domain, target_concepts)

        if self.verbose:
            print(f"Adapted patterns for {to_domain}: {len(adapted_patterns)}")

        # 3. Применение к целевому домену
        instantiated_facts = self.apply_patterns(to_domain, adapted_patterns)

        if self.verbose:
            print(f"Generated facts: {len(instantiated_facts)}")
            for fact in instantiated_facts:
                print(f"  - {fact}")

        # Вычисление confidence
        confidence = min(1.0, len(instantiated_facts) * 0.2)

        # Создание результата
        result = TransferResult(
            from_domain=from_domain,
            to_domain=to_domain,
            patterns_transferred=adapted_patterns,
            instantiated_facts=instantiated_facts,
            confidence=confidence
        )

        self.transfer_history.append(result)

        return result

    def extract_abstract_patterns(self, domain: str) -> List[AbstractPattern]:
        """
        Извлечение абстрактных паттернов из домена

        Преобразует специфичное знание домена в абстрактные паттерны
        """
        if domain not in self.domain_models:
            return []

        domain_model = self.domain_models[domain]

        # Получаем все паттерны, относящиеся к этому домену
        domain_patterns = [
            p for p in self.meta_model.abstract_patterns
            if p.source_domain == domain
        ]

        return domain_patterns

    def adapt_patterns(
        self,
        patterns: List[AbstractPattern],
        target_domain: str,
        target_concepts: Optional[List[str]] = None
    ) -> List[AbstractPattern]:
        """
        Адаптация паттернов к целевому домену

        Находит соответствия между концептами исходного и целевого доменов
        """
        if target_domain not in self.domain_models:
            return []

        target_model = self.domain_models[target_domain]
        adapted = []

        for pattern in patterns:
            # Создаём адаптированную копию паттерна
            adapted_pattern = AbstractPattern(
                pattern_id=f"{pattern.pattern_id}_adapted_to_{target_domain}",
                pattern_type=pattern.pattern_type,
                source_domain=f"{pattern.source_domain} → {target_domain}",
                template=pattern.template,
                variables=pattern.variables,
                constraints=pattern.constraints,
                confidence=pattern.confidence * 0.8,  # Снижаем confidence при адаптации
                examples=[]
            )

            # Пытаемся найти соответствия в целевом домене
            if target_concepts and len(target_concepts) >= len(pattern.variables):
                # Используем предоставленные концепты
                adapted_pattern.examples.append({
                    var: concept
                    for var, concept in zip(pattern.variables, target_concepts)
                })
            else:
                # Автоматически подбираем концепты из целевого домена
                if target_model.knowledge.concepts:
                    sample_concepts = random.sample(
                        target_model.knowledge.concepts,
                        min(len(pattern.variables), len(target_model.knowledge.concepts))
                    )
                    adapted_pattern.examples.append({
                        var: concept.name
                        for var, concept in zip(pattern.variables, sample_concepts)
                    })

            adapted.append(adapted_pattern)

        return adapted

    def apply_patterns(
        self,
        target_domain: str,
        patterns: List[AbstractPattern]
    ) -> List[str]:
        """
        Применение паттернов к целевому домену

        Инстанциирует паттерны с концептами целевого домена
        """
        if target_domain not in self.domain_models:
            return []

        target_model = self.domain_models[target_domain]
        instantiated_facts = []

        for pattern in patterns:
            # Инстанциируем паттерн с примерами
            for example in pattern.examples:
                if len(example) >= len(pattern.variables):
                    fact = pattern.instantiate(example)
                    instantiated_facts.append(fact)

                    # Добавляем факт в целевой домен
                    target_model.knowledge.add_fact(fact)

                    # Обновляем успешность паттерна
                    self.meta_model.update_pattern_success(pattern.pattern_id, True)

        return instantiated_facts

    def few_shot_adapt(
        self,
        new_domain: str,
        examples: List[Dict[str, Any]],
        num_shots: int = 5
    ) -> DomainModel:
        """
        Few-shot адаптация к новому домену

        Быстрое обучение на малом количестве примеров
        """
        # Берём только несколько примеров
        few_shot_examples = examples[:num_shots]

        if self.verbose:
            print(f"\n=== Few-shot learning: {new_domain} ({num_shots} shots) ===")

        # Обучаемся на этих примерах
        domain_model = self.learn_from_domain(new_domain, few_shot_examples)

        # Находим похожие домены
        similar_domains = self._find_similar_domains(new_domain)

        if self.verbose and similar_domains:
            print(f"Similar domains found: {', '.join(similar_domains)}")

        # Переносим знания из похожих доменов
        for similar_domain in similar_domains[:2]:  # Берём 2 самых похожих
            try:
                self.transfer_knowledge(similar_domain, new_domain)
            except Exception as e:
                if self.verbose:
                    print(f"Transfer from {similar_domain} failed: {e}")

        return domain_model

    def _find_similar_domains(self, target_domain: str) -> List[str]:
        """Найти похожие домены"""
        if target_domain not in self.domain_models:
            return []

        target_model = self.domain_models[target_domain]
        similarities = []

        for domain_name, domain_model in self.domain_models.items():
            if domain_name == target_domain:
                continue

            # Вычисляем схожесть доменов на основе общих паттернов
            common_pattern_types = set()

            target_patterns = [
                p for p in self.meta_model.abstract_patterns
                if p.source_domain == target_domain
            ]
            domain_patterns = [
                p for p in self.meta_model.abstract_patterns
                if p.source_domain == domain_name
            ]

            for tp in target_patterns:
                for dp in domain_patterns:
                    if tp.pattern_type == dp.pattern_type:
                        common_pattern_types.add(tp.pattern_type)

            if common_pattern_types:
                similarity = len(common_pattern_types) / max(len(target_patterns), len(domain_patterns), 1)
                similarities.append((domain_name, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in similarities]

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        return {
            "domains_count": len(self.domain_models),
            "total_patterns": len(self.meta_model.abstract_patterns),
            "transfers_count": len(self.transfer_history),
            "domain_stats": self.meta_model.domain_statistics,
            "pattern_types": {
                pt.value: len([p for p in self.meta_model.abstract_patterns if p.pattern_type == pt])
                for pt in PatternType
            }
        }


def demo():
    """Демонстрация meta-learning системы"""
    print("=" * 80)
    print("META-LEARNING ACROSS DOMAINS - DEMO")
    print("=" * 80)

    agent = MetaLearningAgent(verbose=True)

    # === ДОМЕН 1: 5G Networks ===
    print("\n" + "=" * 80)
    print("DOMAIN 1: 5G Networks")
    print("=" * 80)

    fiveg_examples = [
        {
            "concept": "mmWave",
            "properties": {"frequency": "high", "coverage": "low", "speed": "very_high"},
            "examples": ["30-300 GHz spectrum"]
        },
        {
            "concept": "Sub-6GHz",
            "properties": {"frequency": "medium", "coverage": "high", "speed": "medium"},
            "examples": ["Below 6 GHz spectrum"]
        },
        {
            "fact": "mmWave provides very high speed, but has poor coverage"
        },
        {
            "fact": "More frequency leads to less penetration through walls"
        },
        {
            "fact": "5G mmWave is limited by range and obstacles"
        },
        {
            "fact": "Massive MIMO leads to increased capacity"
        }
    ]

    agent.learn_from_domain("5G Networks", fiveg_examples)

    # === ДОМЕН 2: Blockchain ===
    print("\n" + "=" * 80)
    print("DOMAIN 2: Blockchain")
    print("=" * 80)

    blockchain_examples = [
        {
            "concept": "Proof-of-Work",
            "properties": {"security": "high", "energy": "high", "throughput": "low"},
            "examples": ["Bitcoin mining"]
        },
        {
            "concept": "Proof-of-Stake",
            "properties": {"security": "medium", "energy": "low", "throughput": "high"},
            "examples": ["Ethereum 2.0"]
        },
        {
            "fact": "Proof-of-Work provides high security, but has low throughput"
        },
        {
            "fact": "More decentralization leads to less transaction speed"
        },
        {
            "fact": "Blockchain consensus is limited by the slowest node"
        }
    ]

    agent.learn_from_domain("Blockchain", blockchain_examples)

    # === ДОМЕН 3: Quantum Computing ===
    print("\n" + "=" * 80)
    print("DOMAIN 3: Quantum Computing")
    print("=" * 80)

    quantum_examples = [
        {
            "concept": "Qubit",
            "properties": {"power": "high", "stability": "low", "cost": "very_high"},
            "examples": ["Superconducting qubit"]
        },
        {
            "concept": "Quantum Gate",
            "properties": {"speed": "very_fast", "error_rate": "high"},
            "examples": ["Hadamard gate, CNOT gate"]
        },
        {
            "fact": "More qubits provide higher computational power, but harder to control"
        },
        {
            "fact": "Quantum systems are limited by decoherence time"
        }
    ]

    agent.learn_from_domain("Quantum Computing", quantum_examples)

    # === TRANSFER LEARNING ===
    print("\n" + "=" * 80)
    print("KNOWLEDGE TRANSFER")
    print("=" * 80)

    # Transfer 1: 5G → Blockchain
    print("\n--- Transfer 1: 5G Networks → Blockchain ---")
    result1 = agent.transfer_knowledge(
        from_domain="5G Networks",
        to_domain="Blockchain",
        target_concepts=["Proof-of-Work", "high security", "low scalability"]
    )

    print(f"\nTransfer confidence: {result1.confidence:.2f}")
    print(f"Patterns transferred: {len(result1.patterns_transferred)}")

    # Transfer 2: Blockchain → Quantum Computing
    print("\n--- Transfer 2: Blockchain → Quantum Computing ---")
    result2 = agent.transfer_knowledge(
        from_domain="Blockchain",
        to_domain="Quantum Computing",
        target_concepts=["Qubit", "computational power", "error correction"]
    )

    print(f"\nTransfer confidence: {result2.confidence:.2f}")
    print(f"Patterns transferred: {len(result2.patterns_transferred)}")

    # === FEW-SHOT LEARNING ===
    print("\n" + "=" * 80)
    print("FEW-SHOT ADAPTATION")
    print("=" * 80)

    ml_examples = [
        {
            "concept": "Deep Learning",
            "properties": {"accuracy": "high", "data_required": "very_high", "interpretability": "low"},
        },
        {
            "concept": "Linear Regression",
            "properties": {"accuracy": "medium", "data_required": "low", "interpretability": "high"},
        },
        {
            "fact": "Deep Learning provides high accuracy, but requires massive datasets"
        },
        {
            "fact": "More model complexity leads to less interpretability"
        },
        {
            "fact": "Neural networks are limited by overfitting on small datasets"
        }
    ]

    # Few-shot learning (только 3 примера)
    agent.few_shot_adapt("Machine Learning", ml_examples, num_shots=3)

    # === STATISTICS ===
    print("\n" + "=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)

    stats = agent.get_statistics()
    print(f"\nTotal domains: {stats['domains_count']}")
    print(f"Total abstract patterns: {stats['total_patterns']}")
    print(f"Total transfers: {stats['transfers_count']}")

    print("\nPattern types distribution:")
    for pattern_type, count in stats['pattern_types'].items():
        if count > 0:
            print(f"  - {pattern_type}: {count}")

    print("\nDomain statistics:")
    for domain, domain_stats in stats['domain_stats'].items():
        print(f"\n{domain}:")
        print(f"  Concepts: {domain_stats['concepts_count']}")
        print(f"  Facts: {domain_stats['facts_count']}")
        print(f"  Patterns: {domain_stats['patterns_count']}")

    # === TRANSFER HISTORY ===
    print("\n" + "=" * 80)
    print("TRANSFER HISTORY")
    print("=" * 80)

    for i, transfer in enumerate(agent.transfer_history, 1):
        print(f"\n{i}. {transfer.from_domain} → {transfer.to_domain}")
        print(f"   Patterns: {len(transfer.patterns_transferred)}")
        print(f"   Facts generated: {len(transfer.instantiated_facts)}")
        print(f"   Confidence: {transfer.confidence:.2f}")

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return agent


if __name__ == "__main__":
    agent = demo()
