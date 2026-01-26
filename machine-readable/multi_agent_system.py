#!/usr/bin/env python3
"""
МУЛЬТИ-АГЕНТНАЯ СИСТЕМА ДЛЯ 4-УРОВНЕВОЙ БАЗЫ ЗНАНИЙ
==================================================

Концепция: Специализированные агенты для каждого уровня + координатор

АРХИТЕКТУРА:
┌─────────────────────────────────────────────────────────────────┐
│                      COORDINATOR AGENT                          │
│         (Координирует работу всех агентов)                      │
└────────┬────────────────────────────────────────────────────┬───┘
         │                                                    │
    ┌────▼─────┐  ┌──────────┐  ┌──────────┐  ┌─────────────▼─┐
    │ Formula  │  │Archetype │  │Algorithm │  │  Theorem      │
    │  Agent   │  │  Agent   │  │  Agent   │  │   Agent       │
    │ (Уровень1)│  │(Уровень2)│  │(Уровень3)│  │ (Уровень 4)   │
    └──────────┘  └──────────┘  └──────────┘  └───────────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                            │
                   ┌────────▼────────┐
                   │  Knowledge Base │
                   └─────────────────┘

СПЕЦИАЛИЗАЦИЯ АГЕНТОВ:
- FormulaAgent: Эксперт по математическим формулам и абстракциям
- ArchetypeAgent: Эксперт по структурам и компонентам
- AlgorithmAgent: Эксперт по процессам и алгоритмам
- TheoremAgent: Эксперт по практическим примерам и афоризмам
- CoordinatorAgent: Управляет всеми агентами, принимает стратегические решения
"""

import json
import time
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import re


@dataclass
class AgentMessage:
    """Сообщение между агентами"""
    from_agent: str
    to_agent: str
    message_type: str  # request, response, notification
    content: Any
    timestamp: str
    metadata: Dict[str, Any]


@dataclass
class AgentResponse:
    """Ответ агента"""
    agent_name: str
    success: bool
    data: Any
    confidence: float
    processing_time_ms: float
    reasoning: str


class BaseAgent(ABC):
    """Базовый класс для всех агентов"""

    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.processed_requests = 0
        self.avg_confidence = 0.0
        self.knowledge_cache = {}

        print(f"  ✓ {name} инициализирован (специализация: {specialization})")

    @abstractmethod
    def process(self, query: str, context: Dict) -> AgentResponse:
        """Обработка запроса (должна быть реализована в подклассах)"""
        pass

    def _extract_section(self, content: str, section_marker: str) -> Optional[str]:
        """Извлечение секции из документа"""
        pattern = rf'{section_marker}.*?(?=\n\[|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0) if match else None

    def _update_stats(self, confidence: float):
        """Обновление статистики агента"""
        self.processed_requests += 1
        self.avg_confidence = (
            (self.avg_confidence * (self.processed_requests - 1) + confidence)
            / self.processed_requests
        )


class FormulaAgent(BaseAgent):
    """
    АГЕНТ ФОРМУЛ (Уровень 1)

    Специализация:
    - Поиск и извлечение математических формул
    - Объяснение переменных и параметров
    - Валидация формул
    """

    def __init__(self, knowledge_base: List[Dict]):
        super().__init__("FormulaAgent", "Математические формулы и абстракции")
        self.kb = knowledge_base

    def process(self, query: str, context: Dict) -> AgentResponse:
        start_time = time.time()

        results = []
        query_lower = query.lower()

        # Поиск формул в документах
        for doc in self.kb:
            content = doc.get("content", "")

            # Проверка наличия уровня 1 (ФОРМУЛА)
            if not doc.get("structure", {}).get("has_formula", False):
                continue

            # Извлечение секции с формулой
            formula_section = self._extract_section(content, r'\[1\].*?ФОРМУЛА')

            if formula_section:
                # Проверка релевантности
                keywords = re.findall(r'\b\w+\b', query_lower)
                score = sum(1 for kw in keywords if kw in formula_section.lower())

                if score > 0:
                    results.append({
                        "topic": doc["topic"],
                        "formula_section": formula_section[:500],
                        "score": score,
                        "path": doc["path"]
                    })

        # Ранжирование
        results.sort(key=lambda x: x["score"], reverse=True)

        # Оценка уверенности
        if results:
            confidence = min(0.95, 0.5 + (results[0]["score"] / 10))
        else:
            confidence = 0.0

        elapsed = (time.time() - start_time) * 1000

        self._update_stats(confidence)

        return AgentResponse(
            agent_name=self.name,
            success=len(results) > 0,
            data=results[:3],  # Топ-3
            confidence=confidence,
            processing_time_ms=elapsed,
            reasoning=f"Найдено {len(results)} формул с релевантностью > 0"
        )


class ArchetypeAgent(BaseAgent):
    """
    АГЕНТ АРХЕТИПОВ (Уровень 2)

    Специализация:
    - Поиск структурных компонентов
    - Анализ архитектур и паттернов
    - Детализация систем
    """

    def __init__(self, knowledge_base: List[Dict]):
        super().__init__("ArchetypeAgent", "Структуры и архетипы")
        self.kb = knowledge_base

    def process(self, query: str, context: Dict) -> AgentResponse:
        start_time = time.time()

        results = []

        for doc in self.kb:
            if not doc.get("structure", {}).get("has_archetype", False):
                continue

            content = doc.get("content", "")
            archetype_section = self._extract_section(content, r'\[2\].*?АРХЕТИП')

            if archetype_section:
                keywords = re.findall(r'\b\w+\b', query.lower())
                score = sum(1 for kw in keywords if kw in archetype_section.lower())

                if score > 0:
                    results.append({
                        "topic": doc["topic"],
                        "archetype_section": archetype_section[:500],
                        "score": score,
                        "path": doc["path"]
                    })

        results.sort(key=lambda x: x["score"], reverse=True)

        confidence = min(0.9, 0.4 + (results[0]["score"] / 10)) if results else 0.0
        elapsed = (time.time() - start_time) * 1000

        self._update_stats(confidence)

        return AgentResponse(
            agent_name=self.name,
            success=len(results) > 0,
            data=results[:3],
            confidence=confidence,
            processing_time_ms=elapsed,
            reasoning=f"Найдено {len(results)} архетипов"
        )


class AlgorithmAgent(BaseAgent):
    """
    АГЕНТ АЛГОРИТМОВ (Уровень 3)

    Специализация:
    - Поиск пошаговых процессов
    - Извлечение алгоритмов и инструкций
    - Анализ последовательностей действий
    """

    def __init__(self, knowledge_base: List[Dict]):
        super().__init__("AlgorithmAgent", "Алгоритмы и процессы")
        self.kb = knowledge_base

    def process(self, query: str, context: Dict) -> AgentResponse:
        start_time = time.time()

        results = []

        for doc in self.kb:
            if not doc.get("structure", {}).get("has_algorithm", False):
                continue

            content = doc.get("content", "")
            algo_section = self._extract_section(content, r'\[3\].*?АЛГОРИТМ')

            if algo_section:
                keywords = re.findall(r'\b\w+\b', query.lower())
                score = sum(1 for kw in keywords if kw in algo_section.lower())

                # Бонус за "как" вопросы (алгоритмы отвечают на "как")
                if 'как' in query.lower() or 'how' in query.lower():
                    score *= 1.5

                if score > 0:
                    # Извлечение шагов
                    steps = self._extract_steps(algo_section)

                    results.append({
                        "topic": doc["topic"],
                        "algorithm_section": algo_section[:500],
                        "steps": steps,
                        "score": score,
                        "path": doc["path"]
                    })

        results.sort(key=lambda x: x["score"], reverse=True)

        confidence = min(0.9, 0.4 + (results[0]["score"] / 10)) if results else 0.0
        elapsed = (time.time() - start_time) * 1000

        self._update_stats(confidence)

        return AgentResponse(
            agent_name=self.name,
            success=len(results) > 0,
            data=results[:3],
            confidence=confidence,
            processing_time_ms=elapsed,
            reasoning=f"Найдено {len(results)} алгоритмов"
        )

    def _extract_steps(self, content: str) -> List[str]:
        """Извлечение шагов из алгоритма"""
        # Ищем строки начинающиеся с "Шаг N:"
        pattern = r'Шаг \d+:.*?(?=Шаг \d+:|\n\[|\Z)'
        steps = re.findall(pattern, content, re.DOTALL)
        return [step.strip()[:100] for step in steps[:5]]  # Первые 5 шагов


class TheoremAgent(BaseAgent):
    """
    АГЕНТ ТЕОРЕМ (Уровень 4)

    Специализация:
    - Поиск конкретных примеров и кейсов
    - Извлечение афоризмов и практических советов
    - Анализ реальных историй
    """

    def __init__(self, knowledge_base: List[Dict]):
        super().__init__("TheoremAgent", "Примеры и теоремы")
        self.kb = knowledge_base

    def process(self, query: str, context: Dict) -> AgentResponse:
        start_time = time.time()

        results = []

        for doc in self.kb:
            if not doc.get("structure", {}).get("has_theorem", False):
                continue

            content = doc.get("content", "")
            theorem_section = self._extract_section(content, r'\[4\].*?ТЕОРЕМА')

            if theorem_section:
                keywords = re.findall(r'\b\w+\b', query.lower())
                score = sum(1 for kw in keywords if kw in theorem_section.lower())

                # Бонус за запросы примеров
                if 'пример' in query.lower() or 'example' in query.lower():
                    score *= 1.5

                if score > 0:
                    # Извлечение примеров
                    examples = self._extract_examples(theorem_section)

                    results.append({
                        "topic": doc["topic"],
                        "theorem_section": theorem_section[:500],
                        "examples": examples,
                        "score": score,
                        "path": doc["path"]
                    })

        results.sort(key=lambda x: x["score"], reverse=True)

        confidence = min(0.95, 0.5 + (results[0]["score"] / 10)) if results else 0.0
        elapsed = (time.time() - start_time) * 1000

        self._update_stats(confidence)

        return AgentResponse(
            agent_name=self.name,
            success=len(results) > 0,
            data=results[:3],
            confidence=confidence,
            processing_time_ms=elapsed,
            reasoning=f"Найдено {len(results)} теорем с примерами"
        )

    def _extract_examples(self, content: str) -> List[str]:
        """Извлечение примеров из теоремы"""
        pattern = r'ПРИМЕР \d+:.*?(?=ПРИМЕР \d+:|\n\[|\Z)'
        examples = re.findall(pattern, content, re.DOTALL)
        return [ex.strip()[:150] for ex in examples[:3]]  # Первые 3 примера


class CoordinatorAgent(BaseAgent):
    """
    АГЕНТ-КООРДИНАТОР

    Роль:
    - Анализирует запрос и определяет какие агенты нужны
    - Координирует работу специализированных агентов
    - Агрегирует результаты
    - Принимает стратегические решения
    """

    def __init__(self, agents: Dict[str, BaseAgent]):
        super().__init__("CoordinatorAgent", "Координация и стратегия")
        self.agents = agents
        self.coordination_log = []

    def process(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Координированная обработка запроса

        Стратегия:
        1. Анализ запроса
        2. Выбор релевантных агентов
        3. Параллельная обработка (эмуляция)
        4. Агрегация результатов
        5. Формирование финального ответа
        """
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"  КООРДИНАТОР: Обработка запроса")
        print(f"{'='*70}")
        print(f"  Запрос: {query}")

        # ═══════════════════════════════════════════════════════════════
        # ШАГ 1: Анализ запроса и выбор агентов
        # ═══════════════════════════════════════════════════════════════
        selected_agents = self._select_agents(query)

        print(f"  Выбрано агентов: {len(selected_agents)}")
        for agent_name in selected_agents:
            print(f"    • {agent_name}")

        # ═══════════════════════════════════════════════════════════════
        # ШАГ 2: Отправка запросов агентам (параллельно в реальности)
        # ═══════════════════════════════════════════════════════════════
        agent_responses = {}

        for agent_name in selected_agents:
            agent = self.agents[agent_name]
            print(f"\n  → Запрос к {agent_name}...")

            response = agent.process(query, context or {})
            agent_responses[agent_name] = response

            print(f"    ✓ Ответ получен: {response.success}, "
                  f"confidence={response.confidence:.2f}, "
                  f"время={response.processing_time_ms:.1f}ms")

        # ═══════════════════════════════════════════════════════════════
        # ШАГ 3: Агрегация результатов
        # ═══════════════════════════════════════════════════════════════
        aggregated = self._aggregate_results(agent_responses, query)

        # ═══════════════════════════════════════════════════════════════
        # ШАГ 4: Формирование финального ответа
        # ═══════════════════════════════════════════════════════════════
        final_response = self._formulate_response(aggregated, query, agent_responses)

        elapsed = (time.time() - start_time) * 1000

        print(f"\n  Общее время: {elapsed:.2f} ms")
        print(f"  Итоговая уверенность: {final_response['confidence']:.2f}")
        print(f"{'='*70}\n")

        # Логирование
        self._log_coordination(query, selected_agents, agent_responses, final_response)

        return final_response

    def _select_agents(self, query: str) -> List[str]:
        """Выбор релевантных агентов для запроса"""
        q = query.lower()

        selected = []

        # Эвристики выбора
        if any(word in q for word in ['формула', 'уравнение', 'выражение', 'formula']):
            selected.append("FormulaAgent")

        if any(word in q for word in ['структура', 'компонент', 'архитектура', 'archetype']):
            selected.append("ArchetypeAgent")

        if any(word in q for word in ['как', 'шаг', 'процесс', 'алгоритм', 'how', 'step']):
            selected.append("AlgorithmAgent")

        if any(word in q for word in ['пример', 'случай', 'история', 'example', 'case']):
            selected.append("TheoremAgent")

        # Если ничего не выбрано - используем всех (комплексный запрос)
        if not selected:
            selected = list(self.agents.keys())

        return selected

    def _aggregate_results(self, responses: Dict[str, AgentResponse], query: str) -> Dict:
        """Агрегация результатов от разных агентов"""

        all_results = []
        total_confidence = 0.0
        successful_agents = 0

        for agent_name, response in responses.items():
            if response.success and response.data:
                all_results.extend([
                    {**item, "source_agent": agent_name}
                    for item in response.data
                ])
                total_confidence += response.confidence
                successful_agents += 1

        # Средняя уверенность
        avg_confidence = total_confidence / successful_agents if successful_agents > 0 else 0.0

        # Ранжирование по score (если есть)
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return {
            "results": all_results[:10],  # Топ-10
            "avg_confidence": avg_confidence,
            "agents_responded": successful_agents,
            "total_results": len(all_results)
        }

    def _formulate_response(self, aggregated: Dict, query: str, agent_responses: Dict) -> Dict:
        """Формирование финального ответа"""

        # Структурирование по агентам
        by_level = {}
        for result in aggregated["results"]:
            agent = result.get("source_agent", "unknown")
            if agent not in by_level:
                by_level[agent] = []
            by_level[agent].append(result)

        # Рекомендации
        recommendations = self._generate_coordinator_recommendations(
            query, aggregated, agent_responses
        )

        return {
            "query": query,
            "results": aggregated["results"],
            "confidence": aggregated["avg_confidence"],
            "agents_used": list(agent_responses.keys()),
            "results_by_level": by_level,
            "recommendations": recommendations,
            "meta": {
                "total_results": aggregated["total_results"],
                "agents_responded": aggregated["agents_responded"],
                "agent_performance": {
                    name: {
                        "confidence": resp.confidence,
                        "time_ms": resp.processing_time_ms
                    }
                    for name, resp in agent_responses.items()
                }
            }
        }

    def _generate_coordinator_recommendations(self, query: str, aggregated: Dict,
                                             agent_responses: Dict) -> List[str]:
        """Генерация рекомендаций от координатора"""
        recs = []

        # Рекомендации на основе уверенности
        if aggregated["avg_confidence"] > 0.8:
            recs.append("✓ Высокая уверенность: результаты высоко релевантны")
        elif aggregated["avg_confidence"] < 0.5:
            recs.append("⚠️ Низкая уверенность: рекомендуется уточнить запрос")

        # Рекомендации на основе охвата
        all_agent_names = set(self.agents.keys())
        used_agents = set(agent_responses.keys())
        unused = all_agent_names - used_agents

        if unused:
            unused_str = ", ".join(unused)
            recs.append(f"💡 Не использованы: {unused_str} (могут содержать дополнительную информацию)")

        # Рекомендации на основе результатов
        if "FormulaAgent" in agent_responses and agent_responses["FormulaAgent"].success:
            recs.append("📐 Найдены формулы → рекомендуется изучить примеры применения")

        if "TheoremAgent" in agent_responses and agent_responses["TheoremAgent"].success:
            recs.append("📚 Найдены примеры → рекомендуется изучить лежащие в основе принципы")

        return recs

    def _log_coordination(self, query: str, agents: List[str], responses: Dict, final: Dict):
        """Логирование координации"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "agents_selected": agents,
            "responses": {
                name: {
                    "success": resp.success,
                    "confidence": resp.confidence,
                    "time_ms": resp.processing_time_ms
                }
                for name, resp in responses.items()
            },
            "final_confidence": final["confidence"]
        }
        self.coordination_log.append(log_entry)

    def get_statistics(self) -> Dict:
        """Статистика координатора"""
        return {
            "coordinations": len(self.coordination_log),
            "agent_stats": {
                name: {
                    "processed": agent.processed_requests,
                    "avg_confidence": agent.avg_confidence
                }
                for name, agent in self.agents.items()
            }
        }


class MultiAgentSystem:
    """
    МУЛЬТИ-АГЕНТНАЯ СИСТЕМА - главный интерфейс

    Управляет всей системой агентов
    """

    def __init__(self, knowledge_base_path: str = "афоризмы"):
        print("\n" + "="*70)
        print("  ИНИЦИАЛИЗАЦИЯ МУЛЬТИ-АГЕНТНОЙ СИСТЕМЫ")
        print("="*70)

        # Загрузка базы знаний
        self.kb = self._load_knowledge_base(knowledge_base_path)

        # Создание специализированных агентов
        self.formula_agent = FormulaAgent(self.kb)
        self.archetype_agent = ArchetypeAgent(self.kb)
        self.algorithm_agent = AlgorithmAgent(self.kb)
        self.theorem_agent = TheoremAgent(self.kb)

        # Словарь агентов
        self.agents = {
            "FormulaAgent": self.formula_agent,
            "ArchetypeAgent": self.archetype_agent,
            "AlgorithmAgent": self.algorithm_agent,
            "TheoremAgent": self.theorem_agent
        }

        # Создание координатора
        self.coordinator = CoordinatorAgent(self.agents)

        print(f"\n✓ Система готова к работе")
        print(f"  Агентов: {len(self.agents)}")
        print(f"  Документов в базе: {len(self.kb)}")
        print("="*70 + "\n")

    def _load_knowledge_base(self, path: str) -> List[Dict]:
        """Загрузка базы знаний"""
        kb_path = Path(path)
        documents = []

        if not kb_path.exists():
            print(f"  ⚠ База знаний не найдена: {kb_path}")
            return documents

        txt_files = list(kb_path.rglob("*.txt"))
        print(f"  Загрузка {len(txt_files)} файлов...")

        for file_path in txt_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                topic = file_path.parent.name

                doc = {
                    "path": str(file_path),
                    "topic": topic,
                    "content": content,
                    "structure": {
                        "has_formula": bool(re.search(r'\[1\].*?ФОРМУЛА', content)),
                        "has_archetype": bool(re.search(r'\[2\].*?АРХЕТИП', content)),
                        "has_algorithm": bool(re.search(r'\[3\].*?АЛГОРИТМ', content)),
                        "has_theorem": bool(re.search(r'\[4\].*?ТЕОРЕМА', content)),
                    }
                }

                documents.append(doc)
            except Exception as e:
                print(f"  ⚠ Ошибка: {file_path}: {e}")

        print(f"  ✓ Загружено документов: {len(documents)}")
        return documents

    def query(self, question: str, context: Optional[Dict] = None) -> Dict:
        """
        Обработка запроса через мульти-агентную систему

        Args:
            question: Вопрос
            context: Контекст (опционально)

        Returns:
            Dict с результатами от всех релевантных агентов
        """
        return self.coordinator.process(question, context or {})

    def get_statistics(self) -> Dict:
        """Получение статистики системы"""
        return self.coordinator.get_statistics()


# ═══════════════════════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ДЕМОНСТРАЦИЯ МУЛЬТИ-АГЕНТНОЙ СИСТЕМЫ")
    print("="*80 + "\n")

    # Инициализация
    system = MultiAgentSystem(knowledge_base_path="афоризмы")

    # Тест 1: Запрос формулы
    print("\n" + "─"*80)
    print("  ТЕСТ 1: Запрос формулы")
    print("─"*80)

    result1 = system.query("Какая формула для 5G сетей?")

    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"  Уверенность: {result1['confidence']:.2f}")
    print(f"  Агентов использовано: {len(result1['agents_used'])}")
    print(f"  Результатов: {len(result1['results'])}")

    if result1['results']:
        print(f"\n  Топ результат:")
        print(f"    Тема: {result1['results'][0]['topic']}")
        print(f"    Агент: {result1['results'][0]['source_agent']}")

    print(f"\n  Рекомендации:")
    for rec in result1['recommendations']:
        print(f"    • {rec}")

    # Тест 2: Запрос примеров
    print("\n" + "─"*80)
    print("  ТЕСТ 2: Запрос примеров")
    print("─"*80)

    result2 = system.query("Покажи примеры IoT устройств")

    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"  Уверенность: {result2['confidence']:.2f}")
    print(f"  Результатов: {len(result2['results'])}")

    # Тест 3: Комплексный запрос
    print("\n" + "─"*80)
    print("  ТЕСТ 3: Комплексный запрос (все уровни)")
    print("─"*80)

    result3 = system.query("Расскажи про blockchain")

    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"  Уверенность: {result3['confidence']:.2f}")
    print(f"  Агентов: {len(result3['agents_used'])}")

    print(f"\n  Производительность агентов:")
    for agent, perf in result3['meta']['agent_performance'].items():
        print(f"    {agent}: confidence={perf['confidence']:.2f}, "
              f"time={perf['time_ms']:.1f}ms")

    # Статистика
    print("\n" + "="*80)
    print("  СТАТИСТИКА СИСТЕМЫ")
    print("="*80)

    stats = system.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n✓ Демонстрация завершена!")
