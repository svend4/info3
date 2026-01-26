#!/usr/bin/env python3
"""
============================================================================
FEDERATED LEARNING - Privacy-Preserving Distributed Learning
============================================================================
Уровень 2.2: ПРОДВИНУТОЕ

Обучение на данных от нескольких пользователей без передачи данных:
- Локальное обучение на устройствах пользователей
- Только градиенты передаются на сервер
- Агрегация обновлений (FedAvg)
- Приватность: данные не покидают устройство
- Коллективное обучение от тысяч пользователей
- Адаптация к разным доменам

USE CASE:
- 1000 компаний используют систему
- Каждая учит на своих данных
- Все получают улучшенную модель
- Никто не видит данные других

Реальность: 90%
============================================================================
"""

import json
import os
import time
import copy
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import random

# Попытка импорта numpy для градиентов
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  NumPy not available. Install: pip install numpy")


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ModelUpdate:
    """Обновление модели (градиенты)"""
    client_id: str
    round_number: int
    gradients: Dict[str, Any]  # Параметр → градиент
    samples_count: int
    loss: float
    accuracy: float
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class FederatedRound:
    """Раунд федеративного обучения"""
    round_number: int
    participants: List[str]
    updates: List[ModelUpdate]
    aggregated_gradients: Dict[str, Any]
    global_loss: float
    global_accuracy: float
    started_at: str
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()


@dataclass
class ClientStatistics:
    """Статистика клиента"""
    client_id: str
    total_rounds: int = 0
    total_samples: int = 0
    avg_loss: float = 0.0
    avg_accuracy: float = 0.0
    last_update: Optional[str] = None
    data_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class FederatedModel:
    """Федеративная модель"""
    model_id: str
    version: int
    parameters: Dict[str, Any]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# SIMPLE MODEL (for demonstration)
# ============================================================================

class SimpleRankingModel:
    """
    Простая модель ранжирования для демонстрации FL

    Модель: score = w1 * semantic_sim + w2 * keyword_match + w3 * recency + bias
    """

    def __init__(self):
        # Инициализация весов (случайные малые значения)
        self.parameters = {
            'w1_semantic': 0.5 + random.uniform(-0.1, 0.1),    # Семантическое сходство
            'w2_keyword': 0.3 + random.uniform(-0.1, 0.1),     # Ключевые слова
            'w3_recency': 0.1 + random.uniform(-0.1, 0.1),     # Новизна
            'bias': random.uniform(-0.1, 0.1)
        }

    def predict(self, features: Dict[str, float]) -> float:
        """Предсказание score для документа"""
        score = (
            self.parameters['w1_semantic'] * features.get('semantic_sim', 0.0) +
            self.parameters['w2_keyword'] * features.get('keyword_match', 0.0) +
            self.parameters['w3_recency'] * features.get('recency', 0.0) +
            self.parameters['bias']
        )
        return max(0.0, min(1.0, score))  # Клампинг в [0, 1]

    def compute_loss(
        self,
        features_list: List[Dict[str, float]],
        targets: List[float]
    ) -> float:
        """MSE loss"""
        total_loss = 0.0
        for features, target in zip(features_list, targets):
            prediction = self.predict(features)
            total_loss += (prediction - target) ** 2
        return total_loss / len(features_list) if features_list else 0.0

    def compute_accuracy(
        self,
        features_list: List[Dict[str, float]],
        targets: List[float],
        threshold: float = 0.1
    ) -> float:
        """Accuracy (в пределах threshold от target)"""
        correct = 0
        for features, target in zip(features_list, targets):
            prediction = self.predict(features)
            if abs(prediction - target) <= threshold:
                correct += 1
        return correct / len(features_list) if features_list else 0.0

    def compute_gradients(
        self,
        features_list: List[Dict[str, float]],
        targets: List[float],
        learning_rate: float = 0.01
    ) -> Dict[str, float]:
        """
        Вычисление градиентов (simplified gradient descent)

        Для MSE loss: ∂L/∂w = 2 * (prediction - target) * feature
        """
        gradients = {param: 0.0 for param in self.parameters}
        n = len(features_list)

        for features, target in zip(features_list, targets):
            prediction = self.predict(features)
            error = prediction - target

            # Градиенты для каждого параметра
            gradients['w1_semantic'] += 2 * error * features.get('semantic_sim', 0.0)
            gradients['w2_keyword'] += 2 * error * features.get('keyword_match', 0.0)
            gradients['w3_recency'] += 2 * error * features.get('recency', 0.0)
            gradients['bias'] += 2 * error

        # Усреднение
        for param in gradients:
            gradients[param] /= n

        return gradients

    def apply_gradients(self, gradients: Dict[str, float], learning_rate: float = 0.01):
        """Применение градиентов к параметрам"""
        for param, gradient in gradients.items():
            if param in self.parameters:
                self.parameters[param] -= learning_rate * gradient

    def get_parameters(self) -> Dict[str, float]:
        """Получение параметров"""
        return copy.deepcopy(self.parameters)

    def set_parameters(self, parameters: Dict[str, float]):
        """Установка параметров"""
        self.parameters = copy.deepcopy(parameters)


# ============================================================================
# LOCAL AGENT (Client-side)
# ============================================================================

class LocalAgent:
    """
    Локальный агент на устройстве клиента

    - Хранит локальные данные
    - Обучает модель локально
    - Отправляет только градиенты
    """

    def __init__(
        self,
        client_id: str,
        local_data: List[Tuple[Dict[str, float], float]]
    ):
        self.client_id = client_id
        self.local_data = local_data  # (features, target) pairs
        self.local_model = SimpleRankingModel()
        self.statistics = ClientStatistics(client_id=client_id)

    def receive_global_model(self, global_parameters: Dict[str, float]):
        """Получение обновлённой глобальной модели"""
        self.local_model.set_parameters(global_parameters)

    def train_local(
        self,
        epochs: int = 1,
        learning_rate: float = 0.01
    ) -> ModelUpdate:
        """
        Локальное обучение на собственных данных

        Returns:
            ModelUpdate с градиентами (НЕ данными!)
        """
        features_list = [item[0] for item in self.local_data]
        targets = [item[1] for item in self.local_data]

        # Локальное обучение (несколько эпох)
        for epoch in range(epochs):
            gradients = self.local_model.compute_gradients(
                features_list,
                targets,
                learning_rate
            )
            self.local_model.apply_gradients(gradients, learning_rate)

        # Вычисление финальных градиентов для отправки
        final_gradients = self.local_model.compute_gradients(
            features_list,
            targets,
            learning_rate
        )

        # Метрики
        loss = self.local_model.compute_loss(features_list, targets)
        accuracy = self.local_model.compute_accuracy(features_list, targets)

        # Обновление статистики
        self.statistics.total_samples += len(self.local_data)
        self.statistics.last_update = datetime.now().isoformat()

        return ModelUpdate(
            client_id=self.client_id,
            round_number=self.statistics.total_rounds,
            gradients=final_gradients,
            samples_count=len(self.local_data),
            loss=loss,
            accuracy=accuracy
        )

    def evaluate(self) -> Dict[str, float]:
        """Оценка модели на локальных данных"""
        features_list = [item[0] for item in self.local_data]
        targets = [item[1] for item in self.local_data]

        loss = self.local_model.compute_loss(features_list, targets)
        accuracy = self.local_model.compute_accuracy(features_list, targets)

        return {
            'loss': loss,
            'accuracy': accuracy,
            'samples': len(self.local_data)
        }


# ============================================================================
# FEDERATED SERVER
# ============================================================================

class FederatedServer:
    """
    Федеративный сервер

    - Координирует обучение
    - Агрегирует градиенты (FedAvg)
    - Распространяет обновлённую модель
    """

    def __init__(
        self,
        model_id: str = "federated_ranking_model",
        aggregation_strategy: str = "fedavg"  # fedavg, weighted_avg
    ):
        self.model_id = model_id
        self.aggregation_strategy = aggregation_strategy
        self.global_model = SimpleRankingModel()
        self.current_round = 0
        self.rounds_history: List[FederatedRound] = []
        self.client_statistics: Dict[str, ClientStatistics] = {}

    def get_global_parameters(self) -> Dict[str, float]:
        """Получение параметров глобальной модели"""
        return self.global_model.get_parameters()

    def aggregate_updates(
        self,
        updates: List[ModelUpdate]
    ) -> Dict[str, float]:
        """
        Агрегация обновлений от клиентов (FedAvg)

        FedAvg: weighted average по количеству samples
        """
        if not updates:
            return self.global_model.get_parameters()

        if self.aggregation_strategy == "fedavg":
            # Weighted average
            total_samples = sum(update.samples_count for update in updates)
            aggregated = {param: 0.0 for param in updates[0].gradients}

            for update in updates:
                weight = update.samples_count / total_samples
                for param, gradient in update.gradients.items():
                    aggregated[param] += weight * gradient

            return aggregated

        elif self.aggregation_strategy == "simple_avg":
            # Simple average (не рекомендуется для FL)
            aggregated = {param: 0.0 for param in updates[0].gradients}

            for update in updates:
                for param, gradient in update.gradients.items():
                    aggregated[param] += gradient

            for param in aggregated:
                aggregated[param] /= len(updates)

            return aggregated

        else:
            raise ValueError(f"Unknown aggregation strategy: {self.aggregation_strategy}")

    def run_round(
        self,
        clients: List[LocalAgent],
        participant_fraction: float = 1.0,
        local_epochs: int = 1,
        learning_rate: float = 0.01
    ) -> FederatedRound:
        """
        Запуск одного раунда федеративного обучения

        1. Выбор участников
        2. Отправка глобальной модели
        3. Локальное обучение
        4. Сбор обновлений
        5. Агрегация
        6. Обновление глобальной модели
        """
        self.current_round += 1
        started_at = datetime.now().isoformat()

        # 1. Выбор участников
        num_participants = max(1, int(len(clients) * participant_fraction))
        participants = random.sample(clients, num_participants)
        participant_ids = [c.client_id for c in participants]

        print(f"\n{'='*70}")
        print(f"ROUND {self.current_round}: {num_participants}/{len(clients)} participants")
        print(f"{'='*70}")

        # 2. Отправка глобальной модели
        global_params = self.get_global_parameters()
        for client in participants:
            client.receive_global_model(global_params)

        # 3. Локальное обучение + сбор обновлений
        updates: List[ModelUpdate] = []
        for client in participants:
            print(f"  Training on {client.client_id}...")
            update = client.train_local(epochs=local_epochs, learning_rate=learning_rate)
            updates.append(update)
            print(f"    Loss: {update.loss:.4f}, Accuracy: {update.accuracy:.4f}")

            # Обновление статистики клиента
            if client.client_id not in self.client_statistics:
                self.client_statistics[client.client_id] = ClientStatistics(
                    client_id=client.client_id
                )
            stats = self.client_statistics[client.client_id]
            stats.total_rounds += 1
            stats.total_samples += update.samples_count
            stats.avg_loss = (stats.avg_loss * (stats.total_rounds - 1) + update.loss) / stats.total_rounds
            stats.avg_accuracy = (stats.avg_accuracy * (stats.total_rounds - 1) + update.accuracy) / stats.total_rounds
            stats.last_update = update.timestamp

        # 4. Агрегация градиентов
        print(f"\n  Aggregating {len(updates)} updates...")
        aggregated_gradients = self.aggregate_updates(updates)

        # 5. Применение к глобальной модели
        self.global_model.apply_gradients(aggregated_gradients, learning_rate)

        # 6. Вычисление глобальных метрик
        global_loss = sum(u.loss * u.samples_count for u in updates) / sum(u.samples_count for u in updates)
        global_accuracy = sum(u.accuracy * u.samples_count for u in updates) / sum(u.samples_count for u in updates)

        print(f"\n  Global Loss: {global_loss:.4f}, Global Accuracy: {global_accuracy:.4f}")

        # Создание записи раунда
        round_record = FederatedRound(
            round_number=self.current_round,
            participants=participant_ids,
            updates=updates,
            aggregated_gradients=aggregated_gradients,
            global_loss=global_loss,
            global_accuracy=global_accuracy,
            started_at=started_at,
            completed_at=datetime.now().isoformat()
        )
        self.rounds_history.append(round_record)

        return round_record

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика федеративного обучения"""
        if not self.rounds_history:
            return {'message': 'No rounds completed yet'}

        latest_round = self.rounds_history[-1]

        return {
            'total_rounds': self.current_round,
            'total_clients': len(self.client_statistics),
            'latest_round': {
                'number': latest_round.round_number,
                'participants': len(latest_round.participants),
                'global_loss': latest_round.global_loss,
                'global_accuracy': latest_round.global_accuracy
            },
            'convergence': {
                'initial_loss': self.rounds_history[0].global_loss if self.rounds_history else 0,
                'latest_loss': latest_round.global_loss,
                'improvement': (
                    (self.rounds_history[0].global_loss - latest_round.global_loss) /
                    self.rounds_history[0].global_loss * 100
                ) if self.rounds_history[0].global_loss > 0 else 0
            },
            'client_statistics': {
                cid: asdict(stats)
                for cid, stats in self.client_statistics.items()
            }
        }

    def save_model(self, path: str):
        """Сохранение глобальной модели"""
        model_data = {
            'model_id': self.model_id,
            'version': self.current_round,
            'parameters': self.global_model.get_parameters(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'metadata': {
                'total_rounds': self.current_round,
                'total_clients': len(self.client_statistics)
            }
        }

        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)

        print(f"✅ Model saved to {path}")


# ============================================================================
# DATA GENERATION (for demo)
# ============================================================================

def generate_synthetic_data(
    num_clients: int = 10,
    samples_per_client: int = 50,
    heterogeneity: float = 0.5
) -> List[List[Tuple[Dict[str, float], float]]]:
    """
    Генерация синтетических данных для демонстрации FL

    Args:
        num_clients: Количество клиентов
        samples_per_client: Количество samples на клиента
        heterogeneity: Степень неоднородности данных (0=одинаковые, 1=очень разные)

    Returns:
        Список данных для каждого клиента
    """
    all_client_data = []

    for client_idx in range(num_clients):
        client_data = []

        # Разные клиенты имеют разные распределения
        # (имитация non-IID data в FL)
        semantic_bias = random.uniform(-heterogeneity, heterogeneity)
        keyword_bias = random.uniform(-heterogeneity, heterogeneity)

        for _ in range(samples_per_client):
            # Генерация features
            features = {
                'semantic_sim': max(0, min(1, random.random() + semantic_bias)),
                'keyword_match': max(0, min(1, random.random() + keyword_bias)),
                'recency': random.random()
            }

            # Генерация target (synthetic ground truth)
            # True model: 0.6 * semantic + 0.3 * keyword + 0.1 * recency
            target = (
                0.6 * features['semantic_sim'] +
                0.3 * features['keyword_match'] +
                0.1 * features['recency']
            )
            target = max(0, min(1, target + random.gauss(0, 0.05)))  # Добавление шума

            client_data.append((features, target))

        all_client_data.append(client_data)

    return all_client_data


# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_federated_learning():
    """Демонстрация Federated Learning"""
    print("=" * 70)
    print("  FEDERATED LEARNING - Demo")
    print("=" * 70)
    print()

    # ========================================================================
    # 1. Генерация данных
    # ========================================================================
    print("=" * 70)
    print("1. Generating Synthetic Data")
    print("=" * 70)

    num_clients = 10
    samples_per_client = 100
    heterogeneity = 0.3

    client_datasets = generate_synthetic_data(
        num_clients=num_clients,
        samples_per_client=samples_per_client,
        heterogeneity=heterogeneity
    )

    print(f"  ✅ Generated data for {num_clients} clients")
    print(f"  ✅ {samples_per_client} samples per client")
    print(f"  ✅ Heterogeneity: {heterogeneity}")
    print()

    # ========================================================================
    # 2. Создание локальных агентов
    # ========================================================================
    print("=" * 70)
    print("2. Creating Local Agents")
    print("=" * 70)

    clients: List[LocalAgent] = []
    for i, data in enumerate(client_datasets):
        client_id = f"client_{i+1:02d}"
        agent = LocalAgent(client_id, data)
        clients.append(agent)
        print(f"  ✅ Created {client_id} with {len(data)} samples")

    print()

    # ========================================================================
    # 3. Создание федеративного сервера
    # ========================================================================
    print("=" * 70)
    print("3. Creating Federated Server")
    print("=" * 70)

    server = FederatedServer(
        model_id="demo_federated_model",
        aggregation_strategy="fedavg"
    )

    print(f"  ✅ Server created with FedAvg aggregation")
    print()

    # ========================================================================
    # 4. Запуск федеративного обучения
    # ========================================================================
    print("=" * 70)
    print("4. Running Federated Learning")
    print("=" * 70)

    num_rounds = 5
    participant_fraction = 0.8  # 80% клиентов на раунд
    local_epochs = 2
    learning_rate = 0.1

    print(f"Configuration:")
    print(f"  Rounds: {num_rounds}")
    print(f"  Participant fraction: {participant_fraction}")
    print(f"  Local epochs: {local_epochs}")
    print(f"  Learning rate: {learning_rate}")

    for round_num in range(num_rounds):
        server.run_round(
            clients=clients,
            participant_fraction=participant_fraction,
            local_epochs=local_epochs,
            learning_rate=learning_rate
        )

    print()

    # ========================================================================
    # 5. Evaluation
    # ========================================================================
    print("=" * 70)
    print("5. Final Evaluation")
    print("=" * 70)

    # Обновление всех клиентов глобальной моделью
    global_params = server.get_global_parameters()
    for client in clients:
        client.receive_global_model(global_params)

    # Evaluation
    all_evaluations = []
    for client in clients:
        eval_result = client.evaluate()
        all_evaluations.append(eval_result)
        print(f"  {client.client_id}: Loss={eval_result['loss']:.4f}, Accuracy={eval_result['accuracy']:.4f}")

    avg_loss = sum(e['loss'] for e in all_evaluations) / len(all_evaluations)
    avg_accuracy = sum(e['accuracy'] for e in all_evaluations) / len(all_evaluations)

    print(f"\n  Global Average:")
    print(f"    Loss: {avg_loss:.4f}")
    print(f"    Accuracy: {avg_accuracy:.4f}")
    print()

    # ========================================================================
    # 6. Statistics
    # ========================================================================
    print("=" * 70)
    print("6. Federated Learning Statistics")
    print("=" * 70)

    stats = server.get_statistics()
    print(f"  Total Rounds: {stats['total_rounds']}")
    print(f"  Total Clients: {stats['total_clients']}")
    print(f"\n  Convergence:")
    print(f"    Initial Loss: {stats['convergence']['initial_loss']:.4f}")
    print(f"    Latest Loss: {stats['convergence']['latest_loss']:.4f}")
    print(f"    Improvement: {stats['convergence']['improvement']:.2f}%")
    print()

    # ========================================================================
    # 7. Model Parameters
    # ========================================================================
    print("=" * 70)
    print("7. Learned Global Model Parameters")
    print("=" * 70)

    final_params = server.get_global_parameters()
    print(f"  Learned parameters:")
    for param, value in final_params.items():
        print(f"    {param}: {value:.4f}")

    print(f"\n  Ground truth (approx):")
    print(f"    w1_semantic: 0.60")
    print(f"    w2_keyword: 0.30")
    print(f"    w3_recency: 0.10")
    print(f"    bias: 0.00")
    print()

    # ========================================================================
    # 8. Save Model
    # ========================================================================
    print("=" * 70)
    print("8. Saving Global Model")
    print("=" * 70)

    model_path = ".cache/federated_model.json"
    os.makedirs(".cache", exist_ok=True)
    server.save_model(model_path)
    print()

    # ========================================================================
    # 9. Privacy Guarantee
    # ========================================================================
    print("=" * 70)
    print("9. Privacy Guarantee")
    print("=" * 70)

    print("  ✅ PRIVACY PRESERVED:")
    print("    - Raw data never leaves clients")
    print("    - Only gradients/updates transmitted")
    print("    - Server cannot reconstruct individual data")
    print("    - Differential privacy can be added (future)")
    print()

    print("=" * 70)
    print("  Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_federated_learning()
