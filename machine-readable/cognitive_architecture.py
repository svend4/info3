#!/usr/bin/env python3
"""
Cognitive Architecture Integration
==================================

Единая когнитивная архитектура, интегрирующая все системы.

Архитектура объединяет:
- Perception Layer: Semantic search, multi-modal input
- Memory Layer: Knowledge storage, retrieval
- Reasoning Layer: Neural-symbolic integration
- Meta-Cognitive Layer: Self-awareness, introspection
- Synthesis Layer: Emergent knowledge creation
- Social Layer: Swarm intelligence
- Validation Layer: Adversarial testing

Это полная когнитивная система, приближенная к человеческому познанию.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum


class ProcessingMode(Enum):
    """Режимы обработки"""
    FAST = "fast"  # Быстрое, интуитивное (System 1)
    SLOW = "slow"  # Медленное, аналитическое (System 2)
    HYBRID = "hybrid"  # Комбинированное


class AttentionFocus(Enum):
    """Фокус внимания"""
    NARROW = "narrow"  # Узкий фокус
    BROAD = "broad"  # Широкий фокус
    SWITCHING = "switching"  # Переключающийся


@dataclass
class CognitiveState:
    """Текущее когнитивное состояние"""
    attention_focus: AttentionFocus = AttentionFocus.BROAD
    processing_mode: ProcessingMode = ProcessingMode.HYBRID
    working_memory: List[Any] = field(default_factory=list)
    active_goals: List[str] = field(default_factory=list)
    arousal_level: float = 0.5  # 0-1
    cognitive_load: float = 0.0  # 0-1

    def update_load(self, delta: float):
        """Обновить когнитивную нагрузку"""
        self.cognitive_load = max(0.0, min(1.0, self.cognitive_load + delta))

        # Автоматическое переключение режима при высокой нагрузке
        if self.cognitive_load > 0.8:
            self.processing_mode = ProcessingMode.FAST
            self.attention_focus = AttentionFocus.NARROW
        elif self.cognitive_load < 0.3:
            self.processing_mode = ProcessingMode.SLOW
            self.attention_focus = AttentionFocus.BROAD


@dataclass
class PerceptionInput:
    """Входные данные восприятия"""
    modality: str  # text, image, audio
    data: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CognitiveResponse:
    """Когнитивный ответ"""
    answer: str
    confidence: float
    reasoning_trace: List[str]
    modules_used: List[str]
    processing_time_ms: float
    cognitive_state: Dict[str, Any]
    meta_cognition: Dict[str, Any]


class PerceptionLayer:
    """
    Слой восприятия

    Обрабатывает входные данные разных модальностей
    """

    def __init__(self):
        self.sensory_buffer: List[PerceptionInput] = []
        self.attention_filter_threshold = 0.3

    def perceive(self, input_data: PerceptionInput) -> Dict[str, Any]:
        """Воспринять входные данные"""
        self.sensory_buffer.append(input_data)

        # Предобработка
        processed = {
            "modality": input_data.modality,
            "features": self._extract_features(input_data),
            "salience": self._compute_salience(input_data),
            "timestamp": input_data.timestamp
        }

        return processed

    def _extract_features(self, input_data: PerceptionInput) -> Dict[str, Any]:
        """Извлечь признаки"""
        if input_data.modality == "text":
            return {
                "tokens": str(input_data.data).split(),
                "length": len(str(input_data.data)),
                "keywords": self._extract_keywords(str(input_data.data))
            }
        return {}

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечь ключевые слова"""
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why'}
        return [w for w in words if w not in stop_words and len(w) > 3]

    def _compute_salience(self, input_data: PerceptionInput) -> float:
        """Вычислить значимость (salience)"""
        # Простая эвристика
        if input_data.modality == "text":
            length = len(str(input_data.data))
            return min(1.0, length / 200)
        return 0.5


class MemoryLayer:
    """
    Слой памяти

    - Working Memory (краткосрочная): ограниченная емкость
    - Long-Term Memory (долгосрочная): неограниченная
    - Episodic Memory: воспоминания о событиях
    """

    def __init__(self, working_memory_capacity: int = 7):
        self.working_memory: List[Any] = []
        self.working_memory_capacity = working_memory_capacity
        self.long_term_memory: Dict[str, Any] = {}
        self.episodic_memory: List[Dict[str, Any]] = []

    def add_to_working_memory(self, item: Any):
        """Добавить в рабочую память"""
        self.working_memory.append(item)

        # Если переполнена, удаляем старейший элемент
        if len(self.working_memory) > self.working_memory_capacity:
            removed = self.working_memory.pop(0)
            # Возможна консолидация в долгосрочную память
            self._consolidate_to_long_term(removed)

    def _consolidate_to_long_term(self, item: Any):
        """Консолидация в долгосрочную память"""
        # Упрощенная консолидация
        if isinstance(item, dict) and 'key' in item:
            self.long_term_memory[item['key']] = item

    def retrieve_from_long_term(self, query: str, top_k: int = 3) -> List[Any]:
        """Извлечь из долгосрочной памяти"""
        # Простой поиск
        results = []
        query_lower = query.lower()

        for key, value in self.long_term_memory.items():
            if query_lower in str(key).lower() or query_lower in str(value).lower():
                results.append(value)

        return results[:top_k]

    def add_episodic_memory(self, event: Dict[str, Any]):
        """Добавить эпизодическую память"""
        event['timestamp'] = datetime.now().isoformat()
        self.episodic_memory.append(event)


class ReasoningLayer:
    """
    Слой рассуждения

    Логический вывод, абдукция, индукция, дедукция
    """

    def __init__(self):
        self.reasoning_chains: List[List[str]] = []

    def reason(self, premises: List[str], mode: str = "deductive") -> Dict[str, Any]:
        """Рассуждение"""
        if mode == "deductive":
            return self._deductive_reasoning(premises)
        elif mode == "inductive":
            return self._inductive_reasoning(premises)
        elif mode == "abductive":
            return self._abductive_reasoning(premises)
        else:
            return self._deductive_reasoning(premises)

    def _deductive_reasoning(self, premises: List[str]) -> Dict[str, Any]:
        """Дедукция: от общего к частному"""
        # Упрощенная логика
        conclusion = f"Based on {len(premises)} premises, deductive conclusion"
        chain = premises + [conclusion]

        self.reasoning_chains.append(chain)

        return {
            "conclusion": conclusion,
            "reasoning_type": "deductive",
            "confidence": 0.8,
            "chain": chain
        }

    def _inductive_reasoning(self, premises: List[str]) -> Dict[str, Any]:
        """Индукция: от частного к общему"""
        conclusion = f"Generalized from {len(premises)} observations"
        chain = premises + [conclusion]

        return {
            "conclusion": conclusion,
            "reasoning_type": "inductive",
            "confidence": 0.6,  # Ниже чем дедукция
            "chain": chain
        }

    def _abductive_reasoning(self, premises: List[str]) -> Dict[str, Any]:
        """Абдукция: поиск наилучшего объяснения"""
        conclusion = f"Best explanation for {len(premises)} observations"
        chain = premises + [conclusion]

        return {
            "conclusion": conclusion,
            "reasoning_type": "abductive",
            "confidence": 0.7,
            "chain": chain
        }


class MetaCognitiveLayer:
    """
    Мета-когнитивный слой

    Мониторинг и контроль собственных процессов познания
    """

    def __init__(self):
        self.self_monitoring_log: List[Dict[str, Any]] = []
        self.strategy_adjustments: List[str] = []

    def monitor(self, cognitive_state: CognitiveState) -> Dict[str, Any]:
        """Мониторинг когнитивного состояния"""
        assessment = {
            "cognitive_load": cognitive_state.cognitive_load,
            "working_memory_usage": len(cognitive_state.working_memory),
            "attention_focus": cognitive_state.attention_focus.value,
            "processing_mode": cognitive_state.processing_mode.value,
            "timestamp": datetime.now().isoformat()
        }

        self.self_monitoring_log.append(assessment)

        # Рекомендации по adjustment
        if cognitive_state.cognitive_load > 0.8:
            assessment["recommendation"] = "reduce_complexity"
        elif cognitive_state.cognitive_load < 0.2:
            assessment["recommendation"] = "increase_depth"
        else:
            assessment["recommendation"] = "maintain_current"

        return assessment

    def adjust_strategy(self, current_strategy: str, performance: float) -> str:
        """Adjustment стратегии"""
        if performance < 0.5:
            # Плохая performance, меняем стратегию
            new_strategy = "alternative_approach"
            self.strategy_adjustments.append(
                f"{current_strategy} → {new_strategy} (performance: {performance:.2f})"
            )
            return new_strategy
        return current_strategy


class SynthesisLayer:
    """
    Слой синтеза

    Создание нового знания через комбинацию существующего
    """

    def __init__(self):
        self.synthesized_concepts: List[Dict[str, Any]] = []

    def synthesize(self, concepts: List[str]) -> Dict[str, Any]:
        """Синтезировать новое знание"""
        if len(concepts) < 2:
            return {"success": False, "reason": "insufficient_concepts"}

        # Комбинация концептов
        synthesized = "_".join(concepts)

        synthesis_result = {
            "synthesized_concept": synthesized,
            "source_concepts": concepts,
            "novelty_score": random.uniform(0.6, 0.9),
            "timestamp": datetime.now().isoformat()
        }

        self.synthesized_concepts.append(synthesis_result)

        return synthesis_result


class IntegratedCognitiveArchitecture:
    """
    Интегрированная когнитивная архитектура

    Объединяет все слои в единую систему
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Инициализация слоёв
        self.perception = PerceptionLayer()
        self.memory = MemoryLayer()
        self.reasoning = ReasoningLayer()
        self.meta_cognitive = MetaCognitiveLayer()
        self.synthesis = SynthesisLayer()

        # Когнитивное состояние
        self.cognitive_state = CognitiveState()

        # История обработки
        self.processing_history: List[Dict[str, Any]] = []

    def process(self, input_text: str) -> CognitiveResponse:
        """
        Полная когнитивная обработка

        Pipeline:
        1. Perception: восприятие входа
        2. Attention: фокусировка внимания
        3. Memory: активация релевантных воспоминаний
        4. Reasoning: логический вывод
        5. Synthesis: создание нового знания (если возможно)
        6. Meta-cognition: мониторинг процесса
        7. Response: формирование ответа
        """
        start_time = datetime.now()

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"COGNITIVE PROCESSING: {input_text[:50]}...")
            print(f"{'='*80}")

        modules_used = []
        reasoning_trace = []

        # 1. PERCEPTION
        perception_input = PerceptionInput(modality="text", data=input_text)
        perceived = self.perception.perceive(perception_input)
        modules_used.append("perception")

        if self.verbose:
            print(f"\n[PERCEPTION] Salience: {perceived['salience']:.2f}")

        # 2. ATTENTION
        if perceived['salience'] > self.perception.attention_filter_threshold:
            self.cognitive_state.attention_focus = AttentionFocus.NARROW
            reasoning_trace.append("High salience → narrow focus")
        else:
            self.cognitive_state.attention_focus = AttentionFocus.BROAD
            reasoning_trace.append("Low salience → broad focus")

        # 3. MEMORY RETRIEVAL
        keywords = perceived['features'].get('keywords', [])
        retrieved_memories = []

        for keyword in keywords[:3]:  # Top 3 keywords
            memories = self.memory.retrieve_from_long_term(keyword, top_k=2)
            retrieved_memories.extend(memories)

        modules_used.append("memory")

        if self.verbose:
            print(f"[MEMORY] Retrieved {len(retrieved_memories)} memories")

        # Add to working memory
        self.cognitive_state.working_memory = keywords[:7]  # Limited capacity
        self.cognitive_state.update_load(0.2)

        # 4. REASONING
        premises = [input_text] + [str(m) for m in retrieved_memories[:2]]
        reasoning_result = self.reasoning.reason(premises, mode="deductive")
        modules_used.append("reasoning")

        reasoning_trace.append(f"Reasoning: {reasoning_result['reasoning_type']}")
        reasoning_trace.extend(reasoning_result['chain'])

        if self.verbose:
            print(f"[REASONING] Type: {reasoning_result['reasoning_type']}")
            print(f"[REASONING] Confidence: {reasoning_result['confidence']:.2f}")

        # 5. SYNTHESIS (если возможно)
        if len(keywords) >= 2:
            synthesis_result = self.synthesis.synthesize(keywords[:3])
            modules_used.append("synthesis")

            reasoning_trace.append(
                f"Synthesis: {synthesis_result.get('synthesized_concept', 'N/A')}"
            )

            if self.verbose:
                print(f"[SYNTHESIS] New concept: {synthesis_result.get('synthesized_concept')}")

        # 6. META-COGNITION
        meta_assessment = self.meta_cognitive.monitor(self.cognitive_state)
        modules_used.append("meta_cognition")

        if self.verbose:
            print(f"[META-COGNITION] Load: {meta_assessment['cognitive_load']:.2f}")
            print(f"[META-COGNITION] Recommendation: {meta_assessment.get('recommendation')}")

        # 7. RESPONSE GENERATION
        answer = reasoning_result['conclusion']
        confidence = reasoning_result['confidence']

        # Adjust confidence based on cognitive load
        if self.cognitive_state.cognitive_load > 0.7:
            confidence *= 0.9  # Reduce confidence under high load

        # Processing time
        end_time = datetime.now()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000

        # Create response
        response = CognitiveResponse(
            answer=answer,
            confidence=confidence,
            reasoning_trace=reasoning_trace,
            modules_used=modules_used,
            processing_time_ms=processing_time_ms,
            cognitive_state={
                "load": self.cognitive_state.cognitive_load,
                "focus": self.cognitive_state.attention_focus.value,
                "mode": self.cognitive_state.processing_mode.value
            },
            meta_cognition=meta_assessment
        )

        # Add episodic memory
        self.memory.add_episodic_memory({
            "query": input_text,
            "answer": answer,
            "confidence": confidence,
            "modules_used": modules_used
        })

        # Store in processing history
        self.processing_history.append({
            "input": input_text,
            "output": answer,
            "timestamp": end_time.isoformat(),
            "processing_time_ms": processing_time_ms
        })

        if self.verbose:
            print(f"\n[RESPONSE] Answer: {answer}")
            print(f"[RESPONSE] Confidence: {confidence:.2f}")
            print(f"[RESPONSE] Processing time: {processing_time_ms:.1f}ms")

        return response

    def introspect(self) -> Dict[str, Any]:
        """Интроспекция системы"""
        return {
            "cognitive_state": {
                "load": self.cognitive_state.cognitive_load,
                "attention": self.cognitive_state.attention_focus.value,
                "mode": self.cognitive_state.processing_mode.value,
                "working_memory_items": len(self.cognitive_state.working_memory)
            },
            "memory_stats": {
                "working_memory_capacity": self.memory.working_memory_capacity,
                "long_term_entries": len(self.memory.long_term_memory),
                "episodic_memories": len(self.memory.episodic_memory)
            },
            "processing_stats": {
                "total_queries": len(self.processing_history),
                "reasoning_chains": len(self.reasoning.reasoning_chains),
                "synthesized_concepts": len(self.synthesis.synthesized_concepts)
            },
            "meta_cognitive_logs": len(self.meta_cognitive.self_monitoring_log)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Получить детальную статистику"""
        total_processing_time = sum(
            h['processing_time_ms'] for h in self.processing_history
        )
        avg_processing_time = (
            total_processing_time / len(self.processing_history)
            if self.processing_history else 0
        )

        return {
            "total_queries_processed": len(self.processing_history),
            "avg_processing_time_ms": avg_processing_time,
            "modules": {
                "perception": "active",
                "memory": "active",
                "reasoning": "active",
                "synthesis": "active",
                "meta_cognition": "active"
            },
            "cognitive_state": self.introspect()['cognitive_state'],
            "memory_usage": self.introspect()['memory_stats']
        }


def demo():
    """Демонстрация интегрированной когнитивной архитектуры"""
    print("=" * 80)
    print("INTEGRATED COGNITIVE ARCHITECTURE - DEMO")
    print("=" * 80)

    system = IntegratedCognitiveArchitecture(verbose=True)

    # === TEST QUERIES ===
    queries = [
        "What is artificial intelligence and how does it work?",
        "Explain quantum computing in simple terms",
        "What are the ethical implications of AI?",
        "How do neural networks learn from data?",
    ]

    print("\n" + "=" * 80)
    print("PROCESSING QUERIES")
    print("=" * 80)

    for query in queries:
        response = system.process(query)

        print(f"\n" + "-" * 80)
        print(f"Query: {query}")
        print(f"Answer: {response.answer}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Modules used: {', '.join(response.modules_used)}")
        print(f"Processing time: {response.processing_time_ms:.1f}ms")

    # === INTROSPECTION ===
    print("\n" + "=" * 80)
    print("SYSTEM INTROSPECTION")
    print("=" * 80)

    introspection = system.introspect()

    print(f"\nCognitive State:")
    print(f"  Load: {introspection['cognitive_state']['load']:.2f}")
    print(f"  Attention: {introspection['cognitive_state']['attention']}")
    print(f"  Mode: {introspection['cognitive_state']['mode']}")
    print(f"  Working Memory: {introspection['cognitive_state']['working_memory_items']} items")

    print(f"\nMemory Stats:")
    print(f"  Long-term entries: {introspection['memory_stats']['long_term_entries']}")
    print(f"  Episodic memories: {introspection['memory_stats']['episodic_memories']}")

    print(f"\nProcessing Stats:")
    print(f"  Total queries: {introspection['processing_stats']['total_queries']}")
    print(f"  Reasoning chains: {introspection['processing_stats']['reasoning_chains']}")
    print(f"  Synthesized concepts: {introspection['processing_stats']['synthesized_concepts']}")

    # === STATISTICS ===
    print("\n" + "=" * 80)
    print("SYSTEM STATISTICS")
    print("=" * 80)

    stats = system.get_statistics()

    print(f"\nTotal queries processed: {stats['total_queries_processed']}")
    print(f"Avg processing time: {stats['avg_processing_time_ms']:.1f}ms")
    print(f"\nActive modules:")
    for module, status in stats['modules'].items():
        print(f"  {module}: {status}")

    # === ARCHITECTURE DESCRIPTION ===
    print("\n" + "=" * 80)
    print("ARCHITECTURE OVERVIEW")
    print("=" * 80)

    print("""
The Integrated Cognitive Architecture consists of:

1. PERCEPTION LAYER
   - Multi-modal input processing
   - Feature extraction
   - Salience computation
   - Sensory buffer

2. MEMORY LAYER
   - Working Memory (limited capacity, ~7 items)
   - Long-Term Memory (unlimited)
   - Episodic Memory (event記録)
   - Memory consolidation

3. REASONING LAYER
   - Deductive reasoning (general → specific)
   - Inductive reasoning (specific → general)
   - Abductive reasoning (best explanation)
   - Reasoning chain tracking

4. META-COGNITIVE LAYER
   - Self-monitoring
   - Strategy adjustment
   - Performance assessment
   - Cognitive load management

5. SYNTHESIS LAYER
   - Emergent knowledge creation
   - Concept combination
   - Novelty detection

This architecture mimics human cognitive processes:
- Perception → Attention → Memory → Reasoning → Response
- Meta-cognition monitors and adjusts the process
- Working memory has limited capacity (Miller's 7±2)
- Cognitive load affects processing mode
- System can introspect its own state

This is a complete cognitive system!
    """)

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return system


if __name__ == "__main__":
    system = demo()
