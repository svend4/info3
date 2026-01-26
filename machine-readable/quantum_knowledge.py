#!/usr/bin/env python3
"""
Quantum Knowledge Processing
============================

Использование квантовых вычислений для обработки знаний.

Основные компоненты:
- Квантовое кодирование знаний (superposition)
- Quantum entanglement для связей между концептами
- Алгоритм Гровера для поиска (O(√N) vs O(N))
- Квантовая интерференция для поиска паттернов

Преимущества:
- Superposition: поиск во всех состояниях одновременно
- √N speedup для поиска
- Entanglement для сложных связей

Ограничения:
- Квантовые компьютеры пока недоступны в масштабе
- Высокий error rate
- Сложность программирования
"""

import math
import random
import cmath
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Try to import qiskit, fallback to simulation if not available
try:
    from qiskit import QuantumCircuit, execute, Aer
    from qiskit.circuit.library import GroverOperator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️  Qiskit not available. Using simulated quantum backend.")


@dataclass
class QuantumState:
    """Квантовое состояние"""
    amplitudes: List[complex]  # Амплитуды вероятностей
    n_qubits: int

    def measure(self) -> int:
        """Измерить квантовое состояние (коллапс)"""
        probabilities = [abs(amp)**2 for amp in self.amplitudes]

        # Нормализация
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]

        # Измерение
        return random.choices(range(len(probabilities)), weights=probabilities)[0]

    def get_probabilities(self) -> List[float]:
        """Получить вероятности"""
        probs = [abs(amp)**2 for amp in self.amplitudes]
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        return probs


@dataclass
class Concept:
    """Концепт в knowledge base"""
    id: int
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    related_concepts: List[int] = field(default_factory=list)

    def similarity(self, other: 'Concept') -> float:
        """Семантическая схожесть"""
        if not other:
            return 0.0

        # Простая схожесть на основе общих свойств
        shared_props = set(self.properties.keys()) & set(other.properties.keys())
        all_props = set(self.properties.keys()) | set(other.properties.keys())

        if not all_props:
            return 0.0

        return len(shared_props) / len(all_props)


@dataclass
class SearchResult:
    """Результат квантового поиска"""
    concept: Concept
    probability: float
    iterations: int
    method: str  # "quantum" or "classical"


class SimulatedQuantumBackend:
    """
    Симуляция квантового бэкенда

    Для демонстрации когда qiskit недоступен
    """

    def __init__(self):
        self.name = "simulated_qasm"

    def simulate_grover(self, n_items: int, target_indices: List[int], iterations: int) -> Dict[str, int]:
        """Симуляция алгоритма Гровера"""
        # Начальное состояние: равномерная суперпозиция
        n_qubits = math.ceil(math.log2(n_items))
        n_states = 2 ** n_qubits

        # Инициализация амплитуд
        amplitudes = [1.0 / math.sqrt(n_states) for _ in range(n_states)]

        # Grover iterations
        for _ in range(iterations):
            # Oracle: инвертируем фазу целевых состояний
            for target in target_indices:
                if target < len(amplitudes):
                    amplitudes[target] *= -1

            # Diffusion operator (упрощённая версия)
            mean = sum(amplitudes) / len(amplitudes)
            amplitudes = [2 * mean - amp for amp in amplitudes]

        # Измерение (получаем counts)
        probabilities = [abs(amp)**2 for amp in amplitudes]
        total_prob = sum(probabilities)
        if total_prob > 0:
            probabilities = [p / total_prob for p in probabilities]

        # Симулируем 1000 shots
        shots = 1000
        counts = {}
        for _ in range(shots):
            # Сэмплируем состояние
            state = random.choices(range(len(probabilities)), weights=probabilities)[0]
            state_str = format(state, f'0{n_qubits}b')
            counts[state_str] = counts.get(state_str, 0) + 1

        return counts

    def simulate_interference(self, concept_a: Concept, concept_b: Concept) -> Dict[str, int]:
        """Симуляция квантовой интерференции"""
        # 2 qubits
        qc_sim = QuantumCircuitSimulator(2)

        # Hadamard на оба кубита
        qc_sim.h(0)
        qc_sim.h(1)

        # Если концепты похожи, применяем CNOT (entanglement)
        similarity = concept_a.similarity(concept_b)
        if similarity > 0.5:
            qc_sim.cx(0, 1)

        # Измерение
        return qc_sim.measure(shots=1000)


class QuantumCircuitSimulator:
    """Простая симуляция квантового circuit"""

    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        n_states = 2 ** n_qubits
        # Начальное состояние |00...0>
        self.amplitudes = [0.0+0.0j for _ in range(n_states)]
        self.amplitudes[0] = 1.0+0.0j

    def h(self, qubit: int):
        """Hadamard gate"""
        # Упрощённая реализация
        new_amplitudes = [0.0+0.0j for _ in range(len(self.amplitudes))]

        for i, amp in enumerate(self.amplitudes):
            if amp != 0:
                # Hadamard: |0> -> (|0> + |1>)/√2, |1> -> (|0> - |1>)/√2
                bit = (i >> qubit) & 1
                if bit == 0:
                    i0 = i
                    i1 = i | (1 << qubit)
                    new_amplitudes[i0] += amp / math.sqrt(2)
                    new_amplitudes[i1] += amp / math.sqrt(2)
                else:
                    i0 = i & ~(1 << qubit)
                    i1 = i
                    new_amplitudes[i0] += amp / math.sqrt(2)
                    new_amplitudes[i1] -= amp / math.sqrt(2)

        self.amplitudes = new_amplitudes

    def cx(self, control: int, target: int):
        """CNOT gate"""
        new_amplitudes = self.amplitudes.copy()

        for i, amp in enumerate(self.amplitudes):
            if amp != 0:
                control_bit = (i >> control) & 1
                if control_bit == 1:
                    # Flip target bit
                    target_bit = (i >> target) & 1
                    new_i = i ^ (1 << target)
                    new_amplitudes[new_i] = amp
                    new_amplitudes[i] = 0.0+0.0j

        self.amplitudes = new_amplitudes

    def measure(self, shots: int = 1000) -> Dict[str, int]:
        """Измерение"""
        probabilities = [abs(amp)**2 for amp in self.amplitudes]
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]

        counts = {}
        for _ in range(shots):
            state = random.choices(range(len(probabilities)), weights=probabilities)[0]
            state_str = format(state, f'0{self.n_qubits}b')
            counts[state_str] = counts.get(state_str, 0) + 1

        return counts


class QuantumKnowledgeAgent:
    """
    Агент с квантовой обработкой знаний

    Использует квантовые алгоритмы:
    - Grover's algorithm для поиска (O(√N))
    - Quantum interference для similarity
    - Quantum superposition для параллельного поиска
    """

    def __init__(self, use_qiskit: bool = True, verbose: bool = False):
        self.verbose = verbose
        self.concepts: List[Concept] = []
        self.concept_by_id: Dict[int, Concept] = {}

        # Выбор бэкенда
        if use_qiskit and QISKIT_AVAILABLE:
            self.backend = Aer.get_backend('qasm_simulator')
            self.use_qiskit = True
            if verbose:
                print("Using Qiskit quantum backend")
        else:
            self.backend = SimulatedQuantumBackend()
            self.use_qiskit = False
            if verbose:
                print("Using simulated quantum backend")

        self.search_history: List[Dict[str, Any]] = []

    def add_concept(self, concept: Concept):
        """Добавить концепт в knowledge base"""
        self.concepts.append(concept)
        self.concept_by_id[concept.id] = concept

        if self.verbose:
            print(f"Added concept: {concept.name} (id: {concept.id})")

    def encode_knowledge(self) -> Any:
        """
        Кодирование знаний в квантовое состояние

        Создаёт суперпозицию всех концептов
        """
        n_concepts = len(self.concepts)
        n_qubits = math.ceil(math.log2(max(n_concepts, 1)))

        if self.use_qiskit:
            qc = QuantumCircuit(n_qubits)

            # Hadamard gates для создания суперпозиции
            for i in range(n_qubits):
                qc.h(i)

            # Entanglement для связанных концептов
            for concept in self.concepts:
                for related_id in concept.related_concepts:
                    if related_id < len(self.concepts):
                        # CNOT между связанными концептами
                        q1 = concept.id % n_qubits
                        q2 = related_id % n_qubits
                        if q1 != q2:
                            qc.cx(q1, q2)

            return qc
        else:
            # Симуляция
            qc_sim = QuantumCircuitSimulator(n_qubits)
            for i in range(n_qubits):
                qc_sim.h(i)

            return qc_sim

    def quantum_search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Квантовый поиск с использованием алгоритма Гровера

        Complexity: O(√N) vs O(N) для классического поиска
        """
        if self.verbose:
            print(f"\n=== Quantum Search: '{query}' ===")

        # Найти релевантные концепты (oracle)
        relevant_indices = []
        for i, concept in enumerate(self.concepts):
            if self._is_relevant(concept, query):
                relevant_indices.append(i)

        if not relevant_indices:
            if self.verbose:
                print("No relevant concepts found")
            return []

        n_concepts = len(self.concepts)
        n_qubits = math.ceil(math.log2(n_concepts))

        # Вычислить оптимальное количество итераций Гровера
        # iterations = π/4 * √(N/M), где N = total items, M = marked items
        if len(relevant_indices) > 0:
            iterations = int(math.pi / 4 * math.sqrt(n_concepts / len(relevant_indices)))
        else:
            iterations = 1

        iterations = max(1, min(iterations, 10))  # Ограничение 1-10

        if self.verbose:
            print(f"Total concepts: {n_concepts}")
            print(f"Relevant concepts: {len(relevant_indices)}")
            print(f"Grover iterations: {iterations}")

        # Выполнить квантовый поиск
        if self.use_qiskit:
            counts = self._grover_search_qiskit(n_concepts, relevant_indices, iterations)
        else:
            counts = self.backend.simulate_grover(n_concepts, relevant_indices, iterations)

        # Интерпретация результатов
        results = []
        for state_str, count in counts.items():
            state_int = int(state_str, 2)
            if state_int < len(self.concepts):
                concept = self.concepts[state_int]
                probability = count / sum(counts.values())

                results.append(SearchResult(
                    concept=concept,
                    probability=probability,
                    iterations=iterations,
                    method="quantum"
                ))

        # Сортировка по вероятности
        results.sort(key=lambda x: x.probability, reverse=True)

        # Записать в историю
        self.search_history.append({
            "query": query,
            "method": "quantum",
            "iterations": iterations,
            "results_count": len(results),
            "timestamp": datetime.now().isoformat()
        })

        return results[:max_results]

    def _grover_search_qiskit(
        self,
        n_items: int,
        target_indices: List[int],
        iterations: int
    ) -> Dict[str, int]:
        """Grover search using Qiskit"""
        n_qubits = math.ceil(math.log2(n_items))

        qc = QuantumCircuit(n_qubits, n_qubits)

        # Начальная суперпозиция
        for i in range(n_qubits):
            qc.h(i)

        # Grover iterations
        for _ in range(iterations):
            # Oracle: маркируем целевые состояния
            for target in target_indices:
                if target < 2**n_qubits:
                    target_binary = format(target, f'0{n_qubits}b')

                    # X gates на 0 bits
                    for i, bit in enumerate(target_binary):
                        if bit == '0':
                            qc.x(n_qubits - 1 - i)

                    # Multi-controlled Z
                    if n_qubits == 1:
                        qc.z(0)
                    else:
                        qc.h(n_qubits - 1)
                        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
                        qc.h(n_qubits - 1)

                    # Undo X gates
                    for i, bit in enumerate(target_binary):
                        if bit == '0':
                            qc.x(n_qubits - 1 - i)

            # Diffusion operator
            for i in range(n_qubits):
                qc.h(i)
            for i in range(n_qubits):
                qc.x(i)

            qc.h(n_qubits - 1)
            qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            qc.h(n_qubits - 1)

            for i in range(n_qubits):
                qc.x(i)
            for i in range(n_qubits):
                qc.h(i)

        # Измерение
        qc.measure(range(n_qubits), range(n_qubits))

        # Выполнение
        job = execute(qc, self.backend, shots=1000)
        result = job.result()
        counts = result.get_counts()

        return counts

    def classical_search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Классический поиск для сравнения"""
        if self.verbose:
            print(f"\n=== Classical Search: '{query}' ===")

        results = []

        # Линейный поиск O(N)
        for concept in self.concepts:
            if self._is_relevant(concept, query):
                results.append(SearchResult(
                    concept=concept,
                    probability=1.0,
                    iterations=len(self.concepts),
                    method="classical"
                ))

        # Записать в историю
        self.search_history.append({
            "query": query,
            "method": "classical",
            "iterations": len(self.concepts),
            "results_count": len(results),
            "timestamp": datetime.now().isoformat()
        })

        return results[:max_results]

    def quantum_interference(self, concept_a: Concept, concept_b: Concept) -> float:
        """
        Квантовая интерференция для измерения схожести

        Конструктивная интерференция (|00>, |11>) = похожи
        Деструктивная интерференция (|01>, |10>) = не похожи
        """
        if self.verbose:
            print(f"\n=== Quantum Interference: {concept_a.name} ↔ {concept_b.name} ===")

        if self.use_qiskit:
            qc = QuantumCircuit(2, 2)

            # Hadamard на оба кубита
            qc.h(0)
            qc.h(1)

            # Если концепты похожи, создаём entanglement
            similarity = concept_a.similarity(concept_b)
            if similarity > 0.5:
                qc.cx(0, 1)

            # Измерение
            qc.measure([0, 1], [0, 1])

            # Выполнение
            job = execute(qc, self.backend, shots=1000)
            result = job.result()
            counts = result.get_counts()
        else:
            counts = self.backend.simulate_interference(concept_a, concept_b)

        # Интерпретация
        constructive = counts.get('00', 0) + counts.get('11', 0)
        total = sum(counts.values())

        similarity_quantum = constructive / total if total > 0 else 0.0

        if self.verbose:
            print(f"Quantum similarity: {similarity_quantum:.2f}")
            print(f"Counts: {counts}")

        return similarity_quantum

    def _is_relevant(self, concept: Concept, query: str) -> bool:
        """Проверить релевантность концепта"""
        query_lower = query.lower()

        # Поиск в имени
        if query_lower in concept.name.lower():
            return True

        # Поиск в свойствах
        for key, value in concept.properties.items():
            if query_lower in str(key).lower() or query_lower in str(value).lower():
                return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        quantum_searches = [s for s in self.search_history if s['method'] == 'quantum']
        classical_searches = [s for s in self.search_history if s['method'] == 'classical']

        return {
            "total_concepts": len(self.concepts),
            "total_searches": len(self.search_history),
            "quantum_searches": len(quantum_searches),
            "classical_searches": len(classical_searches),
            "backend": "qiskit" if self.use_qiskit else "simulated"
        }


def demo():
    """Демонстрация quantum knowledge processing"""
    print("=" * 80)
    print("QUANTUM KNOWLEDGE PROCESSING - DEMO")
    print("=" * 80)

    agent = QuantumKnowledgeAgent(use_qiskit=QISKIT_AVAILABLE, verbose=True)

    # === СОЗДАНИЕ KNOWLEDGE BASE ===
    print("\n" + "=" * 80)
    print("CREATING KNOWLEDGE BASE")
    print("=" * 80)

    concepts = [
        Concept(0, "5G", {"type": "network", "generation": 5, "speed": "high"}),
        Concept(1, "mmWave", {"type": "frequency", "range": "30-300 GHz", "penetration": "low"}),
        Concept(2, "4G", {"type": "network", "generation": 4, "speed": "medium"}),
        Concept(3, "WiFi", {"type": "network", "frequency": "2.4-5 GHz"}),
        Concept(4, "Blockchain", {"type": "technology", "security": "high"}),
        Concept(5, "AI", {"type": "technology", "intelligence": "artificial"}),
        Concept(6, "IoT", {"type": "network", "devices": "connected"}),
        Concept(7, "Cloud", {"type": "infrastructure", "storage": "remote"}),
    ]

    # Добавить связи
    concepts[0].related_concepts = [1, 2]  # 5G связан с mmWave и 4G
    concepts[1].related_concepts = [0]  # mmWave связан с 5G
    concepts[2].related_concepts = [0]  # 4G связан с 5G
    concepts[3].related_concepts = [0, 6]  # WiFi связан с 5G и IoT

    for concept in concepts:
        agent.add_concept(concept)

    # === QUANTUM ENCODING ===
    print("\n" + "=" * 80)
    print("QUANTUM ENCODING")
    print("=" * 80)

    qc = agent.encode_knowledge()
    print(f"Encoded {len(concepts)} concepts into quantum state")
    print(f"Qubits required: {math.ceil(math.log2(len(concepts)))}")

    # === QUANTUM SEARCH vs CLASSICAL SEARCH ===
    print("\n" + "=" * 80)
    print("QUANTUM SEARCH vs CLASSICAL SEARCH")
    print("=" * 80)

    query = "network"

    # Quantum search
    quantum_results = agent.quantum_search(query)
    print(f"\nQuantum Results:")
    for i, result in enumerate(quantum_results, 1):
        print(f"{i}. {result.concept.name} (probability: {result.probability:.2%}, iterations: {result.iterations})")

    # Classical search
    classical_results = agent.classical_search(query)
    print(f"\nClassical Results:")
    for i, result in enumerate(classical_results, 1):
        print(f"{i}. {result.concept.name} (iterations: {result.iterations})")

    # === SPEEDUP ANALYSIS ===
    print("\n" + "=" * 80)
    print("SPEEDUP ANALYSIS")
    print("=" * 80)

    n = len(concepts)
    if quantum_results:
        quantum_iterations = quantum_results[0].iterations
    else:
        quantum_iterations = int(math.pi / 4 * math.sqrt(n))

    classical_iterations = n

    speedup = classical_iterations / max(quantum_iterations, 1)

    print(f"\nDatabase size: {n} concepts")
    print(f"Classical search: {classical_iterations} iterations (O(N))")
    print(f"Quantum search: {quantum_iterations} iterations (O(√N))")
    print(f"Speedup: {speedup:.1f}x")

    # Projection for larger databases
    print(f"\nProjection for larger databases:")
    for size in [100, 1000, 10000, 100000, 1000000]:
        classical_ops = size
        quantum_ops = int(math.pi / 4 * math.sqrt(size))
        speedup_proj = classical_ops / quantum_ops
        print(f"  {size:>7} concepts: Classical={classical_ops:>7}, Quantum={quantum_ops:>5}, Speedup={speedup_proj:>6.1f}x")

    # === QUANTUM INTERFERENCE ===
    print("\n" + "=" * 80)
    print("QUANTUM INTERFERENCE (Similarity)")
    print("=" * 80)

    concept_pairs = [
        (concepts[0], concepts[1]),  # 5G & mmWave (related)
        (concepts[0], concepts[2]),  # 5G & 4G (related)
        (concepts[0], concepts[4]),  # 5G & Blockchain (unrelated)
    ]

    for concept_a, concept_b in concept_pairs:
        similarity_quantum = agent.quantum_interference(concept_a, concept_b)
        similarity_classical = concept_a.similarity(concept_b)

        print(f"\n{concept_a.name} ↔ {concept_b.name}:")
        print(f"  Quantum similarity: {similarity_quantum:.2f}")
        print(f"  Classical similarity: {similarity_classical:.2f}")

    # === STATISTICS ===
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)

    stats = agent.get_statistics()
    print(f"\nTotal concepts: {stats['total_concepts']}")
    print(f"Total searches: {stats['total_searches']}")
    print(f"Quantum searches: {stats['quantum_searches']}")
    print(f"Classical searches: {stats['classical_searches']}")
    print(f"Backend: {stats['backend']}")

    # === THEORETICAL ADVANTAGES ===
    print("\n" + "=" * 80)
    print("THEORETICAL ADVANTAGES")
    print("=" * 80)

    print("""
Quantum Computing Advantages:

1. SUPERPOSITION
   - Explore all possible states simultaneously
   - Parallel search across entire knowledge base

2. GROVER'S ALGORITHM
   - O(√N) complexity vs O(N) classical
   - Quadratic speedup for search
   - Example: 1M concepts → 1000x faster

3. ENTANGLEMENT
   - Encode complex relationships between concepts
   - Non-local correlations
   - Richer knowledge representation

4. QUANTUM INTERFERENCE
   - Constructive interference → similar concepts
   - Destructive interference → dissimilar concepts
   - Natural similarity measure

Limitations:
- Quantum computers not widely available yet
- High error rates (decoherence)
- Complex programming model
- Quantum advantage requires specific problems
    """)

    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)

    return agent


if __name__ == "__main__":
    agent = demo()
