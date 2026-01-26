#!/usr/bin/env python3
"""
Neural-Symbolic Integration (Level 3.2)

Комбинация нейронных сетей и символьного вывода:
- Neural: паттерн-матчинг, обобщение, feature extraction
- Symbolic: логический вывод, объяснения, reasoning
- Integration: двунаправленная конвертация между представлениями

Преимущества:
- Neural хорош в распознавании паттернов из данных
- Symbolic хорош в логическом выводе и объяснениях
- Вместе: сила обоих подходов

Пример использования:
    agent = NeuralSymbolicAgent()
    agent.add_rule("is_high_frequency(X) :- frequency(X, F), F > 20")
    agent.add_rule("poor_penetration(X) :- is_high_frequency(X)")

    result = agent.query("Can 5G mmWave penetrate walls?")
    print(result['answer'])  # Neural + Symbolic reasoning
"""

import json
import time
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import re

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("Warning: sentence-transformers not available, using mock neural model")


@dataclass
class Predicate:
    """Логический предикат"""
    functor: str  # Имя предиката (e.g., "is_high_frequency")
    args: List[str]  # Аргументы (e.g., ["mmWave"])
    confidence: float = 1.0

    def __str__(self):
        args_str = ", ".join(self.args)
        return f"{self.functor}({args_str})"

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.functor == other.functor and self.args == other.args

    def __hash__(self):
        return hash((self.functor, tuple(self.args)))


@dataclass
class Rule:
    """Логическое правило (Horn clause): head :- body"""
    head: Predicate
    body: List[Predicate]
    confidence: float = 1.0

    def __str__(self):
        if not self.body:
            return f"{self.head}."
        body_str = ", ".join(str(p) for p in self.body)
        return f"{self.head} :- {body_str}."


@dataclass
class InferenceResult:
    """Результат логического вывода"""
    predicates: List[Predicate]
    explanation: List[str]
    confidence: float
    inference_chain: List[Rule] = field(default_factory=list)


class SymbolicReasoner:
    """
    Символьный reasoner (упрощенный Prolog)

    Поддерживает:
    - Факты (атомарные предикаты)
    - Правила (Horn clauses)
    - Forward chaining inference
    - Backward chaining (goal-driven)
    - Unification (простая)
    """

    def __init__(self):
        self.facts: Set[Predicate] = set()
        self.rules: List[Rule] = []

    def add_fact(self, predicate: Predicate):
        """Добавление факта"""
        self.facts.add(predicate)

    def add_rule(self, rule: Rule):
        """Добавление правила"""
        self.rules.append(rule)

    def parse_rule(self, rule_str: str) -> Rule:
        """
        Парсинг правила из строки

        Формат:
        - Факт: "frequency(mmWave, 30)"
        - Правило: "is_high_frequency(X) :- frequency(X, F), F > 20"
        """
        rule_str = rule_str.strip()

        # Проверка на правило vs факт
        if ":-" in rule_str:
            head_str, body_str = rule_str.split(":-", 1)
            head = self._parse_predicate(head_str.strip())

            # Парсинг body (может содержать несколько предикатов)
            # Нужно правильно разделить по запятым, учитывая скобки
            body_parts = self._split_by_comma(body_str)
            body = [self._parse_predicate(p.strip()) for p in body_parts if self._is_predicate(p.strip())]

            return Rule(head=head, body=body)
        else:
            # Факт
            predicate = self._parse_predicate(rule_str.rstrip("."))
            return Rule(head=predicate, body=[])

    def _split_by_comma(self, text: str) -> List[str]:
        """
        Разделение текста по запятым, учитывая вложенные скобки

        "frequency(X, F), F > 20" → ["frequency(X, F)", "F > 20"]
        """
        parts = []
        current = []
        depth = 0

        for char in text:
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                # Запятая вне скобок - это разделитель
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)

        # Добавляем последнюю часть
        if current:
            parts.append(''.join(current))

        return parts

    def _is_predicate(self, text: str) -> bool:
        """Проверка, является ли текст предикатом"""
        # Предикат: functor(args) или сравнение
        return "(" in text or any(op in text for op in [">", "<", "=", ">=", "<="])

    def _parse_predicate(self, pred_str: str) -> Predicate:
        """Парсинг предиката из строки"""
        pred_str = pred_str.strip()

        # Проверка на сравнение (X > 20)
        for op in [" >= ", " <= ", " > ", " < ", " = "]:
            if op in pred_str:
                left, right = pred_str.split(op, 1)
                return Predicate(
                    functor=f"compare_{op.strip()}",
                    args=[left.strip(), right.strip()]
                )

        # Обычный предикат: functor(arg1, arg2, ...)
        match = re.match(r"(\w+)\((.*)\)", pred_str)
        if match:
            functor = match.group(1)
            args_str = match.group(2)
            args = [a.strip() for a in args_str.split(",")] if args_str else []
            return Predicate(functor=functor, args=args)

        # Атомарный предикат без аргументов
        return Predicate(functor=pred_str, args=[])

    def forward_chain(self, max_iterations: int = 10) -> Set[Predicate]:
        """
        Forward chaining: вывод всех возможных фактов из правил

        Алгоритм:
        1. Начинаем с известных фактов
        2. Применяем правила, которые могут сработать
        3. Добавляем новые выведенные факты
        4. Повторяем до достижения фиксированной точки
        """
        inferred = set(self.facts)

        for iteration in range(max_iterations):
            new_facts = set()

            for rule in self.rules:
                # Проверяем, можем ли применить правило
                if self._can_apply_rule(rule, inferred):
                    # Применяем правило и добавляем head как новый факт
                    instantiated_head = self._instantiate_predicate(rule.head, inferred)
                    if instantiated_head:
                        new_facts.add(instantiated_head)

            if not new_facts:
                break  # Фиксированная точка достигнута

            inferred.update(new_facts)

        return inferred

    def _can_apply_rule(self, rule: Rule, facts: Set[Predicate]) -> bool:
        """Проверка, можем ли применить правило"""
        if not rule.body:
            return True  # Правило без body (факт)

        # Проверяем, все ли предикаты в body удовлетворены
        for body_pred in rule.body:
            if not self._is_satisfied(body_pred, facts):
                return False

        return True

    def _is_satisfied(self, predicate: Predicate, facts: Set[Predicate], bindings: Dict[str, str] = None) -> bool:
        """Проверка, удовлетворен ли предикат фактами"""
        if bindings is None:
            bindings = {}

        # Проверка на сравнения (X > 20)
        if predicate.functor.startswith("compare_"):
            # Извлекаем оператор и операнды
            operator = predicate.functor.replace("compare_", "")
            left, right = predicate.args

            # Подстав ляем привязки
            if left in bindings:
                left = bindings[left]
            if right in bindings:
                right = bindings[right]

            # Пытаемся преобразовать в числа и сравнить
            try:
                left_val = float(left)
                right_val = float(right)

                if operator == ">":
                    return left_val > right_val
                elif operator == "<":
                    return left_val < right_val
                elif operator == ">=":
                    return left_val >= right_val
                elif operator == "<=":
                    return left_val <= right_val
                elif operator == "=":
                    return left_val == right_val
            except ValueError:
                return False

        # Проверка на совпадение с фактами
        for fact in facts:
            if self._unify(predicate, fact):
                return True

        return False

    def _unify(self, pred1: Predicate, pred2: Predicate) -> bool:
        """Унификация предикатов (упрощенная)"""
        if pred1.functor != pred2.functor:
            return False

        if len(pred1.args) != len(pred2.args):
            return False

        for arg1, arg2 in zip(pred1.args, pred2.args):
            # Переменные (начинаются с заглавной буквы) унифицируются с чем угодно
            if arg1 and arg2 and (arg1[0].isupper() or arg2[0].isupper()):
                continue

            # Константы должны совпадать (case-insensitive)
            if arg1.lower() != arg2.lower():
                return False

        return True

    def _instantiate_predicate(self, predicate: Predicate, facts: Set[Predicate]) -> Optional[Predicate]:
        """Инстанциация предиката с подстановкой значений переменных"""
        # Упрощение: возвращаем предикат как есть
        return predicate

    def backward_chain(self, goal: Predicate, max_depth: int = 5, bindings: Dict[str, str] = None, debug: bool = False) -> InferenceResult:
        """
        Backward chaining: поиск доказательства для goal

        Алгоритм:
        1. Цель - goal predicate
        2. Ищем правило, которое может вывести goal
        3. Рекурсивно доказываем body этого правила с привязками переменных
        4. Если все body доказаны, goal доказан
        """
        if bindings is None:
            bindings = {}

        explanation = []
        inference_chain = []

        # Применяем существующие привязки к goal
        goal = self._apply_bindings(goal, bindings)

        if debug:
            print(f"[DEBUG] backward_chain: goal={goal}, bindings={bindings}")

        # Проверка, является ли goal фактом
        for fact in self.facts:
            new_bindings_from_fact = self._unify_with_bindings(goal, fact, bindings)
            if new_bindings_from_fact is not None:
                explanation.append(f"✓ {goal} - matches fact: {fact}")
                # Возвращаем факт (с конкретными значениями), а не goal
                return InferenceResult(
                    predicates=[fact],
                    explanation=explanation,
                    confidence=1.0
                )

        # Поиск правил, которые могут вывести goal
        for rule in self.rules:
            # Пытаемся унифицировать goal с head правила
            new_bindings = self._unify_with_bindings(rule.head, goal, bindings.copy())

            if new_bindings is not None:
                # Пытаемся доказать body
                if not rule.body:
                    # Правило без body - это факт
                    explanation.append(f"✓ {goal} - derived from rule: {rule}")
                    inference_chain.append(rule)
                    return InferenceResult(
                        predicates=[goal],
                        explanation=explanation,
                        confidence=rule.confidence,
                        inference_chain=inference_chain
                    )

                # Пытаемся доказать все предикаты в body
                all_proven = True
                body_confidence = 1.0

                for body_pred in rule.body:
                    if max_depth <= 0:
                        all_proven = False
                        break

                    # Применяем привязки к body predicate
                    instantiated_pred = self._apply_bindings(body_pred, new_bindings)

                    # Проверяем сравнения напрямую
                    if instantiated_pred.functor.startswith("compare_"):
                        if self._is_satisfied(instantiated_pred, self.facts, new_bindings):
                            explanation.append(f"✓ {instantiated_pred} - comparison satisfied")
                            continue
                        else:
                            explanation.append(f"✗ {instantiated_pred} - comparison failed")
                            all_proven = False
                            break

                    result = self.backward_chain(instantiated_pred, max_depth - 1, new_bindings)
                    if not result.predicates:
                        all_proven = False
                        break

                    explanation.extend(result.explanation)
                    body_confidence *= result.confidence
                    # Обновляем привязки из результатов подцели
                    new_bindings.update(self._extract_bindings(instantiated_pred, result.predicates[0]))

                if all_proven:
                    explanation.append(f"✓ {goal} - derived from rule: {rule}")
                    inference_chain.append(rule)
                    return InferenceResult(
                        predicates=[goal],
                        explanation=explanation,
                        confidence=rule.confidence * body_confidence,
                        inference_chain=inference_chain
                    )

        # Goal не может быть доказан
        explanation.append(f"✗ {goal} - cannot be proven")
        return InferenceResult(
            predicates=[],
            explanation=explanation,
            confidence=0.0
        )

    def _unify_with_bindings(self, pattern: Predicate, instance: Predicate, bindings: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Унификация с отслеживанием привязок переменных"""
        if pattern.functor != instance.functor:
            return None

        if len(pattern.args) != len(instance.args):
            return None

        new_bindings = bindings.copy()

        for pat_arg, inst_arg in zip(pattern.args, instance.args):
            # Если аргумент паттерна - переменная
            if pat_arg and pat_arg[0].isupper():
                if pat_arg in new_bindings:
                    # Переменная уже привязана, проверяем совпадение
                    if new_bindings[pat_arg].lower() != inst_arg.lower():
                        return None
                else:
                    # Новая привязка
                    new_bindings[pat_arg] = inst_arg
            # Если аргумент instance - переменная
            elif inst_arg and inst_arg[0].isupper():
                if inst_arg in new_bindings:
                    if new_bindings[inst_arg].lower() != pat_arg.lower():
                        return None
                else:
                    new_bindings[inst_arg] = pat_arg
            # Оба константы - должны совпадать
            else:
                if pat_arg.lower() != inst_arg.lower():
                    return None

        return new_bindings

    def _apply_bindings(self, predicate: Predicate, bindings: Dict[str, str]) -> Predicate:
        """Применение привязок переменных к предикату"""
        new_args = []
        for arg in predicate.args:
            if arg in bindings:
                new_args.append(bindings[arg])
            else:
                new_args.append(arg)

        return Predicate(
            functor=predicate.functor,
            args=new_args,
            confidence=predicate.confidence
        )

    def _extract_bindings(self, pattern: Predicate, instance: Predicate) -> Dict[str, str]:
        """Извлечение привязок из унифицированных предикатов"""
        bindings = {}

        if pattern.functor != instance.functor:
            return bindings

        for pat_arg, inst_arg in zip(pattern.args, instance.args):
            if pat_arg and pat_arg[0].isupper():
                bindings[pat_arg] = inst_arg

        return bindings


class NeuralModel:
    """
    Нейронная модель для feature extraction и pattern matching

    Использует:
    - Sentence Transformers для embeddings
    - Cosine similarity для сравнения
    - Feature extraction из текста
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name

        if HAS_SENTENCE_TRANSFORMERS:
            print(f"Loading neural model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            print("Neural model loaded successfully")
        else:
            print("Using mock neural model (sentence-transformers not available)")
            self.model = None

    def extract_features(self, text: str) -> Dict[str, float]:
        """
        Извлечение признаков из текста

        Returns:
            Dict с именованными признаками и их значениями (0-1)
        """
        features = {}

        # Базовые признаки (правила)
        text_lower = text.lower()

        # Технические термины
        technical_terms = ['5g', 'mmwave', 'frequency', 'network', 'latency', 'bandwidth', 'ai', 'ml', 'algorithm']
        features['is_technical'] = sum(1 for term in technical_terms if term in text_lower) / len(technical_terms)

        # Вопросы
        question_words = ['can', 'how', 'what', 'why', 'when', 'where', 'is', 'does', 'может', 'как', 'что']
        features['is_question'] = 1.0 if any(word in text_lower for word in question_words) else 0.0

        # Ограничения/проблемы
        limitation_words = ['cannot', 'limitation', 'problem', 'issue', 'challenge', 'не может', 'ограничение', 'проблема']
        features['about_limitations'] = sum(1 for word in limitation_words if word in text_lower) / len(limitation_words)

        # Покрытие/проникновение
        penetration_words = ['penetrate', 'through', 'wall', 'obstacle', 'проникать', 'через', 'стена', 'препятствие']
        features['about_penetration'] = sum(1 for word in penetration_words if word in text_lower) / len(penetration_words)

        # Скорость/производительность
        performance_words = ['speed', 'fast', 'slow', 'performance', 'throughput', 'скорость', 'быстро', 'медленно']
        features['about_performance'] = sum(1 for word in performance_words if word in text_lower) / len(performance_words)

        # Semantic embedding (if available)
        if self.model:
            embedding = self.model.encode([text])[0]
            # Добавляем топ-5 компонентов embedding как features
            for i, val in enumerate(embedding[:5]):
                features[f'embedding_{i}'] = float(val)

        return features

    def classify_query_type(self, text: str) -> str:
        """Классификация типа запроса"""
        features = self.extract_features(text)

        if features['is_question'] > 0.5:
            if features['about_limitations'] > 0.3:
                return 'limitation_question'
            elif features['about_penetration'] > 0.3:
                return 'penetration_question'
            elif features['about_performance'] > 0.3:
                return 'performance_question'
            else:
                return 'general_question'
        elif features['is_technical'] > 0.5:
            return 'technical_statement'
        else:
            return 'general_statement'

    def generate_answer(self, query: str, symbolic_results: InferenceResult) -> str:
        """
        Генерация ответа на основе символьных результатов

        Neural model использует symbolic reasoning для формирования ответа
        """
        if not symbolic_results.predicates:
            return "I cannot determine the answer based on available knowledge."

        # Извлекаем информацию из symbolic results
        predicates = symbolic_results.predicates
        explanation = symbolic_results.explanation

        # Формируем answer
        answer_parts = []

        # Главный predicate
        main_pred = predicates[0]

        # Проверяем тип ответа на основе predicate
        if main_pred.functor in ['cannot_penetrate', 'poor_penetration']:
            answer_parts.append(f"No, {main_pred.args[0]} cannot penetrate obstacles effectively.")
        elif main_pred.functor in ['can_penetrate', 'good_penetration']:
            answer_parts.append(f"Yes, {main_pred.args[0]} can penetrate obstacles.")
        elif main_pred.functor == 'is_high_frequency':
            answer_parts.append(f"{main_pred.args[0]} operates at high frequencies.")
        else:
            answer_parts.append(f"Conclusion: {main_pred}")

        # Добавляем reasoning
        if len(explanation) > 1:
            answer_parts.append("\n\nReasoning:")
            for exp in explanation[:3]:  # Топ-3 reasoning steps
                if exp.startswith("✓"):
                    answer_parts.append(f"  - {exp[2:]}")

        # Confidence
        answer_parts.append(f"\n\nConfidence: {symbolic_results.confidence:.2%}")

        return "\n".join(answer_parts)


class NeuralSymbolicIntegrator:
    """
    Интегратор между neural и symbolic представлениями

    Функции:
    - neural_to_symbolic: конвертация neural features → logical predicates
    - symbolic_to_neural: конвертация symbolic results → neural representation
    """

    def __init__(self):
        # Маппинг между feature names и predicates
        self.feature_to_predicate_map = {
            'is_technical': 'is_technical_query',
            'is_question': 'is_question',
            'about_limitations': 'asks_about_limitations',
            'about_penetration': 'asks_about_penetration',
            'about_performance': 'asks_about_performance',
        }

    def neural_to_symbolic(self, features: Dict[str, float], threshold: float = 0.5) -> List[Predicate]:
        """
        Конвертация neural features в symbolic predicates

        Args:
            features: Dict с feature names и значениями (0-1)
            threshold: Порог для создания predicate

        Returns:
            List of Predicate objects
        """
        predicates = []

        for feature_name, value in features.items():
            if value > threshold:
                # Игнорируем embedding features (слишком низкоуровневые)
                if feature_name.startswith('embedding_'):
                    continue

                # Получаем predicate name из маппинга
                predicate_name = self.feature_to_predicate_map.get(feature_name, feature_name)

                # Создаем predicate с confidence = feature value
                pred = Predicate(
                    functor=predicate_name,
                    args=['query'],
                    confidence=value
                )
                predicates.append(pred)

        return predicates

    def symbolic_to_neural(self, inference_result: InferenceResult) -> Dict[str, Any]:
        """
        Конвертация symbolic inference results в neural-friendly representation

        Returns:
            Dict с информацией для neural model
        """
        return {
            'predicates': [str(p) for p in inference_result.predicates],
            'confidence': inference_result.confidence,
            'explanation': inference_result.explanation,
            'inference_steps': len(inference_result.inference_chain),
            'success': len(inference_result.predicates) > 0
        }


class NeuralSymbolicAgent:
    """
    Главный агент, объединяющий neural и symbolic подходы

    Архитектура:
    1. Neural Model: feature extraction, pattern matching
    2. Symbolic Reasoner: logical inference, rule-based reasoning
    3. Integrator: двунаправленная конвертация

    Pipeline:
    Query → Neural (features) → Symbolic (predicates) → Reasoning →
    Symbolic (results) → Neural (answer generation) → Answer
    """

    def __init__(self, neural_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        print("=" * 80)
        print("Initializing Neural-Symbolic Agent")
        print("=" * 80)

        self.neural_model = NeuralModel(neural_model_name)
        self.symbolic_reasoner = SymbolicReasoner()
        self.integrator = NeuralSymbolicIntegrator()

        print("✓ Neural model initialized")
        print("✓ Symbolic reasoner initialized")
        print("✓ Integrator initialized")
        print("=" * 80)

    def add_fact(self, fact_str: str):
        """Добавление факта в knowledge base"""
        rule = self.symbolic_reasoner.parse_rule(fact_str)
        if not rule.body:
            self.symbolic_reasoner.add_fact(rule.head)
        else:
            self.symbolic_reasoner.add_rule(rule)

    def add_rule(self, rule_str: str):
        """Добавление правила в knowledge base"""
        rule = self.symbolic_reasoner.parse_rule(rule_str)
        self.symbolic_reasoner.add_rule(rule)

    def query(self, question: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Обработка запроса с использованием neural + symbolic reasoning

        Pipeline:
        1. Neural: Extract features
        2. Neural → Symbolic: Convert to predicates
        3. Symbolic: Logical inference
        4. Symbolic → Neural: Convert results
        5. Neural: Generate answer

        Returns:
            Dict с answer, confidence, explanation, reasoning steps
        """
        if verbose:
            print(f"\n{'='*80}")
            print(f"QUERY: {question}")
            print(f"{'='*80}")

        start_time = time.time()

        # 1. Neural: Extract features
        if verbose:
            print("\n1️⃣  NEURAL: Extracting features...")
        features = self.neural_model.extract_features(question)
        query_type = self.neural_model.classify_query_type(question)

        if verbose:
            print(f"   Query type: {query_type}")
            print(f"   Top features:")
            for name, value in sorted(features.items(), key=lambda x: x[1], reverse=True)[:5]:
                if not name.startswith('embedding_'):
                    print(f"     - {name}: {value:.2f}")

        # 2. Neural → Symbolic: Convert to predicates
        if verbose:
            print("\n2️⃣  NEURAL → SYMBOLIC: Converting to predicates...")
        neural_predicates = self.integrator.neural_to_symbolic(features, threshold=0.3)

        if verbose:
            print(f"   Generated predicates:")
            for pred in neural_predicates:
                print(f"     - {pred} (confidence: {pred.confidence:.2f})")

        # 3. Symbolic: Logical inference
        if verbose:
            print("\n3️⃣  SYMBOLIC: Performing logical inference...")

        # Определяем goal на основе query type и predicates
        goal = self._determine_goal(question, query_type, neural_predicates)

        if verbose:
            print(f"   Goal: {goal}")

        symbolic_results = self.symbolic_reasoner.backward_chain(goal)

        if verbose:
            print(f"   Inference result: {len(symbolic_results.predicates)} predicates derived")
            print(f"   Confidence: {symbolic_results.confidence:.2f}")

        # 4. Symbolic → Neural: Convert results
        if verbose:
            print("\n4️⃣  SYMBOLIC → NEURAL: Converting results...")
        neural_representation = self.integrator.symbolic_to_neural(symbolic_results)

        if verbose:
            print(f"   Success: {neural_representation['success']}")
            print(f"   Inference steps: {neural_representation['inference_steps']}")

        # 5. Neural: Generate answer
        if verbose:
            print("\n5️⃣  NEURAL: Generating answer...")
        answer = self.neural_model.generate_answer(question, symbolic_results)

        elapsed_time = time.time() - start_time

        result = {
            'question': question,
            'answer': answer,
            'query_type': query_type,
            'neural_features': features,
            'neural_predicates': [str(p) for p in neural_predicates],
            'symbolic_goal': str(goal),
            'symbolic_results': [str(p) for p in symbolic_results.predicates],
            'explanation': symbolic_results.explanation,
            'confidence': symbolic_results.confidence,
            'inference_chain': [str(r) for r in symbolic_results.inference_chain],
            'elapsed_ms': elapsed_time * 1000
        }

        if verbose:
            print(f"\n{'='*80}")
            print("ANSWER:")
            print(answer)
            print(f"{'='*80}")
            print(f"Processing time: {elapsed_time*1000:.2f}ms")

        return result

    def _determine_goal(self, question: str, query_type: str, predicates: List[Predicate]) -> Predicate:
        """Определение goal для symbolic reasoning на основе вопроса"""
        question_lower = question.lower()

        # Извлекаем ключевые термины из вопроса
        terms = ['mmwave', '5g', 'wall', 'penetrate', 'frequency']
        found_terms = [term for term in terms if term in question_lower]

        # Определяем goal на основе query type и терминов
        if 'penetrate' in question_lower or 'through' in question_lower:
            # Вопрос о проникновении
            if found_terms:
                return Predicate('cannot_penetrate', [found_terms[0]])
            else:
                return Predicate('cannot_penetrate', ['signal'])
        elif 'limitation' in question_lower or 'cannot' in question_lower:
            # Вопрос об ограничениях
            if found_terms:
                return Predicate('has_limitation', [found_terms[0]])
            else:
                return Predicate('has_limitation', ['technology'])
        elif 'frequency' in question_lower:
            # Вопрос о частоте
            if found_terms:
                return Predicate('is_high_frequency', [found_terms[0]])
            else:
                return Predicate('is_high_frequency', ['signal'])
        else:
            # Общий вопрос
            if found_terms:
                return Predicate('property_of', [found_terms[0]])
            else:
                return Predicate('answer', ['query'])

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Статистика knowledge base"""
        return {
            'total_facts': len(self.symbolic_reasoner.facts),
            'total_rules': len(self.symbolic_reasoner.rules),
            'facts': [str(f) for f in self.symbolic_reasoner.facts],
            'rules': [str(r) for r in self.symbolic_reasoner.rules]
        }


def demo():
    """Демонстрация Neural-Symbolic Integration"""
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ: Neural-Symbolic Integration (Level 3.2)")
    print("=" * 80)

    # Создание агента
    agent = NeuralSymbolicAgent()

    print("\n📚 Добавление знаний в symbolic knowledge base...")

    # Факты о 5G mmWave
    agent.add_fact("frequency(mmWave, 30)")
    agent.add_fact("frequency(sub6, 5)")
    agent.add_fact("technology(mmWave, 5G)")
    agent.add_fact("technology(sub6, 5G)")

    # Правила логического вывода
    agent.add_rule("is_high_frequency(X) :- frequency(X, F), F > 20")
    agent.add_rule("is_low_frequency(X) :- frequency(X, F), F < 10")
    agent.add_rule("poor_penetration(X) :- is_high_frequency(X)")
    agent.add_rule("good_penetration(X) :- is_low_frequency(X)")
    agent.add_rule("cannot_penetrate(X) :- poor_penetration(X)")
    agent.add_rule("can_penetrate(X) :- good_penetration(X)")

    # Статистика knowledge base
    stats = agent.get_knowledge_base_stats()
    print(f"   ✓ Facts: {stats['total_facts']}")
    for fact in stats['facts']:
        print(f"      - {fact}")
    print(f"   ✓ Rules: {stats['total_rules']}")
    for rule in stats['rules']:
        print(f"      - {rule}")

    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ: Neural + Symbolic Reasoning")
    print("=" * 80)

    # Тестовые запросы
    queries = [
        "Can 5G mmWave penetrate through walls?",
        "What are the limitations of mmWave?",
        "Is mmWave a high frequency signal?",
        "Can sub-6 GHz 5G penetrate walls better than mmWave?",
    ]

    results = []

    for i, query in enumerate(queries, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}/{len(queries)}")
        result = agent.query(query, verbose=True)
        results.append(result)
        print(f"{'─'*80}")

    # Итоговая статистика
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)

    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    avg_time = sum(r['elapsed_ms'] for r in results) / len(results)

    print(f"\nОбработано запросов: {len(results)}")
    print(f"Средняя уверенность: {avg_confidence:.2%}")
    print(f"Среднее время обработки: {avg_time:.2f}ms")

    print(f"\nРезультаты по запросам:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['question']}")
        print(f"   Query type: {result['query_type']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Neural predicates: {len(result['neural_predicates'])}")
        print(f"   Symbolic results: {len(result['symbolic_results'])}")
        print(f"   Inference steps: {len(result['inference_chain'])}")
        print(f"   Time: {result['elapsed_ms']:.2f}ms")

    print("\n" + "=" * 80)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)
    print("\n💡 Система успешно объединила:")
    print("   • Neural: pattern matching, feature extraction, answer generation")
    print("   • Symbolic: logical inference, rule-based reasoning, explanations")
    print("   • Integration: bidirectional conversion between representations")
    print("\n🎯 Преимущества:")
    print("   • Neural: обобщение, распознавание паттернов")
    print("   • Symbolic: логический вывод, объяснения, прозрачность")
    print("   • Вместе: сила обоих подходов")


if __name__ == "__main__":
    demo()
