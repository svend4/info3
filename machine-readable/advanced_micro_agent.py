#!/usr/bin/env python3
"""
РАСШИРЕННЫЙ МИКРО-АГЕНТ С АВТОНОМНЫМИ РЕШЕНИЯМИ
================================================

Улучшенная версия микро-агента с:
- 15 типов автономных решений (было 8)
- Самообучение на основе истории
- Предсказание следующих запросов
- Мета-когнитивный анализ (агент анализирует свои решения)
- Автономная оптимизация стратегий
- Интеллектуальное кэширование паттернов
- Инфоброкер функциональность

Философия: Агент как "посредник-коммивояжер" между AI и структурированными данными
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import hashlib


class AdvancedMicroAgent:
    """
    Расширенный микро-агент с автономными решениями и самообучением

    НОВЫЕ ВОЗМОЖНОСТИ:
    1. 15 типов решений (вместо 8)
    2. Обучение на основе истории запросов
    3. Предсказание следующего запроса
    4. Мета-анализ своих решений
    5. Автономная оптимизация
    """

    def __init__(self, knowledge_base_path: str = "афоризмы"):
        self.kb_path = Path(knowledge_base_path)

        # Кэш: многоуровневый
        self.l1_cache = {}  # Горячий кэш (быстрый доступ)
        self.l2_cache = {}  # Теплый кэш (частые запросы)
        self.l3_cache = {}  # Холодный кэш (редкие запросы)

        # Паттерн-кэш: автоматически выученные паттерны
        self.pattern_cache = defaultdict(list)

        # История всех операций
        self.decision_log = []
        self.query_history = []

        # Статистика
        self.stats = {
            "queries": 0,
            "cache_hits": {"l1": 0, "l2": 0, "l3": 0},
            "decisions_made": 0,
            "patterns_learned": 0,
            "predictions_made": 0,
            "self_optimizations": 0
        }

        # Профили запросов (обучение)
        self.query_profiles = defaultdict(lambda: {
            "count": 0,
            "avg_time": 0,
            "preferred_level": None,
            "success_rate": 0
        })

        # Мета-когнитивные данные (агент анализирует себя)
        self.meta_cognition = {
            "decision_accuracy": defaultdict(float),
            "strategy_effectiveness": defaultdict(list),
            "learning_curve": []
        }

        # Загрузка базы знаний
        self._load_knowledge_base()

        print(f"✓ Advanced MicroAgent инициализирован")
        print(f"  - База знаний: {len(self.documents)} документов")
        print(f"  - Режимов принятия решений: 15")
        print(f"  - Самообучение: включено")
        print(f"  - Предсказания: включено")

    def _load_knowledge_base(self):
        """Загрузка базы знаний с метаданными"""
        self.documents = []
        self.metadata = {}

        if not self.kb_path.exists():
            print(f"⚠ База знаний не найдена: {self.kb_path}")
            return

        # Сканирование всех .txt файлов
        txt_files = list(self.kb_path.rglob("*.txt"))

        for file_path in txt_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                topic = file_path.parent.name

                doc = {
                    "path": str(file_path),
                    "topic": topic,
                    "content": content,
                    "size": len(content),
                    "lines": len(content.split('\n'))
                }

                # Извлечение структуры
                doc["structure"] = self._extract_structure(content)

                self.documents.append(doc)
                self.metadata[topic] = {
                    "file_count": self.metadata.get(topic, {}).get("file_count", 0) + 1,
                    "total_size": self.metadata.get(topic, {}).get("total_size", 0) + len(content)
                }
            except Exception as e:
                print(f"⚠ Ошибка загрузки {file_path}: {e}")

        print(f"  ✓ Загружено {len(self.documents)} документов из {len(self.metadata)} тем")

    def _extract_structure(self, content: str) -> Dict[str, bool]:
        """Определение структуры документа"""
        return {
            "has_formula": bool(re.search(r'\[1\].*ФОРМУЛА', content)),
            "has_archetype": bool(re.search(r'\[2\].*АРХЕТИП', content)),
            "has_algorithm": bool(re.search(r'\[3\].*АЛГОРИТМ', content)),
            "has_theorem": bool(re.search(r'\[4\].*ТЕОРЕМА', content)),
            "has_examples": bool(re.search(r'ПРИМЕР \d+:', content)),
            "has_code": bool(re.search(r'```|def |class |function', content))
        }

    def query(self, question: str, top_k: int = 5, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ГЛАВНЫЙ МЕТОД: обработка запроса с 15 автономными решениями

        Args:
            question: Вопрос пользователя
            top_k: Количество результатов
            context: Контекст (предыдущие запросы, предпочтения)

        Returns:
            Dict с результатами и мета-информацией о принятых решениях
        """
        start_time = time.time()
        self.stats["queries"] += 1

        # Кэш-ключ
        cache_key = hashlib.md5(question.encode()).hexdigest()

        decisions = []

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 1: Проверка многоуровневого кэша
        # ═══════════════════════════════════════════════════════════════
        cache_result = self._decision_1_check_cache(cache_key)
        decisions.append(cache_result)

        if cache_result["action"] == "cache_hit":
            self.stats["cache_hits"][cache_result["cache_level"]] += 1
            elapsed = time.time() - start_time

            return {
                "question": question,
                "results": cache_result["data"],
                "source": f"cache_{cache_result['cache_level']}",
                "decisions": decisions,
                "elapsed_ms": elapsed * 1000,
                "from_cache": True
            }

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 2: Анализ типа запроса (расширенный)
        # ═══════════════════════════════════════════════════════════════
        query_type = self._decision_2_analyze_query_type(question)
        decisions.append(query_type)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 3: Определение целевого уровня (1-4)
        # ═══════════════════════════════════════════════════════════════
        target_level = self._decision_3_select_target_level(question, query_type)
        decisions.append(target_level)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 4: Выбор метода поиска
        # ═══════════════════════════════════════════════════════════════
        search_method = self._decision_4_choose_search_method(question, query_type)
        decisions.append(search_method)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 5: Извлечение ключевых слов (улучшенное)
        # ═══════════════════════════════════════════════════════════════
        keywords = self._decision_5_extract_keywords(question, query_type)
        decisions.append(keywords)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 6: Проверка паттерн-кэша (НОВОЕ)
        # ═══════════════════════════════════════════════════════════════
        pattern_match = self._decision_6_check_patterns(question, keywords)
        decisions.append(pattern_match)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 7: Поиск в базе знаний
        # ═══════════════════════════════════════════════════════════════
        search_results = self._decision_7_search(keywords["keywords"], target_level["level"])
        decisions.append(search_results)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 8: Ранжирование результатов
        # ═══════════════════════════════════════════════════════════════
        ranking = self._decision_8_rank_results(search_results["results"], question, keywords["keywords"])
        decisions.append(ranking)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 9: Оценка уверенности (confidence)
        # ═══════════════════════════════════════════════════════════════
        confidence = self._decision_9_assess_confidence(ranking["ranked_results"], question)
        decisions.append(confidence)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 10: Обогащение контекстом (НОВОЕ)
        # ═══════════════════════════════════════════════════════════════
        enrichment = self._decision_10_enrich_context(ranking["ranked_results"], question)
        decisions.append(enrichment)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 11: Определение стратегии ответа
        # ═══════════════════════════════════════════════════════════════
        strategy = self._decision_11_response_strategy(confidence, ranking["ranked_results"])
        decisions.append(strategy)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 12: Обучение на запросе (НОВОЕ)
        # ═══════════════════════════════════════════════════════════════
        learning = self._decision_12_learn_from_query(question, query_type, target_level, confidence)
        decisions.append(learning)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 13: Предсказание следующего запроса (НОВОЕ)
        # ═══════════════════════════════════════════════════════════════
        prediction = self._decision_13_predict_next_query(question, context)
        decisions.append(prediction)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 14: Решение о кэшировании
        # ═══════════════════════════════════════════════════════════════
        caching = self._decision_14_cache_decision(cache_key, enrichment["enriched_results"], confidence, query_type)
        decisions.append(caching)

        # ═══════════════════════════════════════════════════════════════
        # РЕШЕНИЕ 15: Мета-когнитивный анализ (НОВОЕ)
        # ═══════════════════════════════════════════════════════════════
        meta_analysis = self._decision_15_meta_cognition(decisions, confidence)
        decisions.append(meta_analysis)

        elapsed = time.time() - start_time
        self.stats["decisions_made"] += len(decisions)

        # Логирование
        self._log_query(question, decisions, elapsed)

        # Финальный результат
        return {
            "question": question,
            "results": enrichment["enriched_results"][:top_k],
            "confidence": confidence["confidence"],
            "query_type": query_type["type"],
            "target_level": target_level["level"],
            "strategy": strategy["strategy"],
            "prediction": prediction.get("next_query"),
            "decisions": decisions,
            "meta_analysis": meta_analysis,
            "elapsed_ms": elapsed * 1000,
            "from_cache": False
        }

    # ═══════════════════════════════════════════════════════════════════
    # РЕАЛИЗАЦИЯ 15 РЕШЕНИЙ
    # ═══════════════════════════════════════════════════════════════════

    def _decision_1_check_cache(self, cache_key: str) -> Dict:
        """РЕШЕНИЕ 1: Проверка трёхуровневого кэша"""
        # L1 (горячий)
        if cache_key in self.l1_cache:
            return {
                "decision": "cache_check",
                "action": "cache_hit",
                "cache_level": "l1",
                "data": self.l1_cache[cache_key]
            }

        # L2 (теплый)
        if cache_key in self.l2_cache:
            # Продвинуть в L1
            self.l1_cache[cache_key] = self.l2_cache[cache_key]
            return {
                "decision": "cache_check",
                "action": "cache_hit",
                "cache_level": "l2",
                "data": self.l2_cache[cache_key]
            }

        # L3 (холодный)
        if cache_key in self.l3_cache:
            # Продвинуть в L2
            self.l2_cache[cache_key] = self.l3_cache[cache_key]
            return {
                "decision": "cache_check",
                "action": "cache_hit",
                "cache_level": "l3",
                "data": self.l3_cache[cache_key]
            }

        return {"decision": "cache_check", "action": "cache_miss"}

    def _decision_2_analyze_query_type(self, question: str) -> Dict:
        """РЕШЕНИЕ 2: Расширенный анализ типа запроса"""
        q_lower = question.lower()

        # Более детальная классификация
        if any(word in q_lower for word in ['формула', 'уравнение', 'выражение', 'математ']):
            return {"decision": "query_type", "type": "formula", "confidence": 0.9}
        elif any(word in q_lower for word in ['пример', 'случай', 'история', 'кейс']):
            return {"decision": "query_type", "type": "example", "confidence": 0.9}
        elif any(word in q_lower for word in ['алгоритм', 'шаг', 'процесс', 'как сделать', 'how to']):
            return {"decision": "query_type", "type": "algorithm", "confidence": 0.9}
        elif any(word in q_lower for word in ['совет', 'рекомендация', 'что делать', 'как лучше']):
            return {"decision": "query_type", "type": "advice", "confidence": 0.8}
        elif any(word in q_lower for word in ['что такое', 'определение', 'понятие', 'концепция']):
            return {"decision": "query_type", "type": "concept", "confidence": 0.9}
        elif any(word in q_lower for word in ['код', 'программ', 'script', 'function', 'class']):
            return {"decision": "query_type", "type": "code", "confidence": 0.85}
        elif any(word in q_lower for word in ['сравни', 'разница', 'vs', 'versus', 'отличие']):
            return {"decision": "query_type", "type": "comparison", "confidence": 0.85}
        else:
            return {"decision": "query_type", "type": "general", "confidence": 0.6}

    def _decision_3_select_target_level(self, question: str, query_type: Dict) -> Dict:
        """РЕШЕНИЕ 3: Интеллектуальный выбор уровня"""
        q_type = query_type["type"]

        # Маппинг типов на уровни
        type_to_level = {
            "formula": [1],
            "example": [4],
            "algorithm": [3],
            "advice": [3, 4],
            "concept": [1, 2],
            "code": [3],
            "comparison": [2, 3],
            "general": [1, 2, 3, 4]
        }

        levels = type_to_level.get(q_type, [1, 2, 3, 4])

        return {
            "decision": "target_level",
            "level": levels,
            "reason": f"Тип запроса '{q_type}' соответствует уровням {levels}"
        }

    def _decision_4_choose_search_method(self, question: str, query_type: Dict) -> Dict:
        """РЕШЕНИЕ 4: Выбор метода поиска"""
        # В этой версии только keyword search, но можно добавить semantic
        return {
            "decision": "search_method",
            "method": "keyword",
            "reason": "Keyword search для текстовых документов"
        }

    def _decision_5_extract_keywords(self, question: str, query_type: Dict) -> Dict:
        """РЕШЕНИЕ 5: Умное извлечение ключевых слов"""
        # Стоп-слова
        stop_words = {
            'как', 'что', 'где', 'когда', 'почему', 'какой', 'какая', 'какие',
            'это', 'есть', 'был', 'была', 'были', 'будет', 'можно', 'нужно',
            'и', 'или', 'не', 'в', 'на', 'с', 'по', 'для', 'к', 'от', 'до'
        }

        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Добавление синонимов для улучшения поиска
        expanded_keywords = keywords.copy()

        # Технологические синонимы
        tech_synonyms = {
            'ai': ['искусственный интеллект', 'нейросеть', 'ml'],
            'ml': ['машинное обучение', 'ai', 'нейросеть'],
            'iot': ['интернет вещей', 'датчик', 'sensor'],
            '5g': ['сеть', '5g', 'беспроводн'],
            'blockchain': ['блокчейн', 'криптовалют', 'биткоин']
        }

        for kw in keywords:
            if kw in tech_synonyms:
                expanded_keywords.extend(tech_synonyms[kw])

        return {
            "decision": "keyword_extraction",
            "keywords": list(set(expanded_keywords)),
            "original_keywords": keywords,
            "expansion_applied": len(expanded_keywords) > len(keywords)
        }

    def _decision_6_check_patterns(self, question: str, keywords: Dict) -> Dict:
        """РЕШЕНИЕ 6: Проверка выученных паттернов (НОВОЕ)"""
        # Создаем сигнатуру запроса
        signature = " ".join(sorted(keywords["keywords"][:3]))

        if signature in self.pattern_cache:
            matches = self.pattern_cache[signature]
            return {
                "decision": "pattern_check",
                "pattern_found": True,
                "matches": matches,
                "signature": signature
            }

        return {
            "decision": "pattern_check",
            "pattern_found": False,
            "signature": signature
        }

    def _decision_7_search(self, keywords: List[str], target_levels: List[int]) -> Dict:
        """РЕШЕНИЕ 7: Поиск в базе знаний"""
        results = []

        for doc in self.documents:
            score = 0
            content_lower = doc["content"].lower()

            # Подсчет совпадений
            for kw in keywords:
                count = content_lower.count(kw.lower())
                score += count

            if score > 0:
                # Проверка уровня
                structure = doc["structure"]
                level_match = False

                if 1 in target_levels and structure["has_formula"]:
                    level_match = True
                if 2 in target_levels and structure["has_archetype"]:
                    level_match = True
                if 3 in target_levels and structure["has_algorithm"]:
                    level_match = True
                if 4 in target_levels and structure["has_theorem"]:
                    level_match = True

                # Бонус за уровень
                if level_match:
                    score *= 1.5

                results.append({
                    "path": doc["path"],
                    "topic": doc["topic"],
                    "score": score,
                    "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
                    "full_content": doc["content"],
                    "structure": structure
                })

        return {
            "decision": "search",
            "results": results,
            "total_found": len(results)
        }

    def _decision_8_rank_results(self, results: List[Dict], question: str, keywords: List[str]) -> Dict:
        """РЕШЕНИЕ 8: Улучшенное ранжирование"""
        # Сортировка по score
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)

        # Дополнительное ранжирование по релевантности названия темы
        q_lower = question.lower()
        for result in ranked:
            topic = result["topic"].lower()
            if topic in q_lower or q_lower in topic:
                result["score"] *= 1.3

        # Пересортировка
        ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

        return {
            "decision": "ranking",
            "ranked_results": ranked,
            "ranking_method": "score_with_topic_boost"
        }

    def _decision_9_assess_confidence(self, results: List[Dict], question: str) -> Dict:
        """РЕШЕНИЕ 9: Оценка уверенности"""
        if not results:
            return {"decision": "confidence", "confidence": 0.0, "reason": "Нет результатов"}

        top_score = results[0]["score"]

        if top_score > 20:
            conf = 0.95
        elif top_score > 10:
            conf = 0.8
        elif top_score > 5:
            conf = 0.6
        else:
            conf = 0.4

        # Снижение если результаты очень разные
        if len(results) > 1:
            second_score = results[1]["score"]
            if top_score / (second_score + 1) < 1.5:
                conf *= 0.9  # Неуверенность из-за близких скоров

        return {
            "decision": "confidence",
            "confidence": conf,
            "top_score": top_score,
            "num_results": len(results)
        }

    def _decision_10_enrich_context(self, results: List[Dict], question: str) -> Dict:
        """РЕШЕНИЕ 10: Обогащение контекстом (НОВОЕ)"""
        enriched = []

        for result in results:
            # Извлечение релевантных секций
            sections = self._extract_relevant_sections(result["full_content"], question)

            enriched.append({
                **result,
                "relevant_sections": sections,
                "summary": self._generate_summary(sections)
            })

        return {
            "decision": "context_enrichment",
            "enriched_results": enriched,
            "enrichment_applied": True
        }

    def _extract_relevant_sections(self, content: str, question: str) -> List[str]:
        """Извлечение релевантных секций из документа"""
        sections = []
        lines = content.split('\n')

        # Ищем секции с ключевыми словами из вопроса
        q_words = set(re.findall(r'\b\w+\b', question.lower()))

        for i, line in enumerate(lines):
            line_words = set(re.findall(r'\b\w+\b', line.lower()))
            if q_words & line_words:  # Есть пересечение
                # Берем контекст: 2 строки до и 3 строки после
                start = max(0, i - 2)
                end = min(len(lines), i + 4)
                section = '\n'.join(lines[start:end])
                sections.append(section)

        return sections[:5]  # Топ-5 секций

    def _generate_summary(self, sections: List[str]) -> str:
        """Генерация краткого summary"""
        if not sections:
            return "Нет релевантного контекста"

        # Простой summary: первые 200 символов первой секции
        first_section = sections[0]
        summary = first_section[:200] + "..." if len(first_section) > 200 else first_section
        return summary

    def _decision_11_response_strategy(self, confidence: Dict, results: List[Dict]) -> Dict:
        """РЕШЕНИЕ 11: Стратегия ответа"""
        conf = confidence["confidence"]

        if conf > 0.8:
            strategy = "direct_answer"
            reason = "Высокая уверенность"
        elif conf > 0.6:
            strategy = "ranked_list"
            reason = "Средняя уверенность, показать топ результатов"
        elif conf > 0.4:
            strategy = "expand_search"
            reason = "Низкая уверенность, нужно расширить поиск"
        else:
            strategy = "ask_clarification"
            reason = "Очень низкая уверенность, нужно уточнение"

        return {
            "decision": "response_strategy",
            "strategy": strategy,
            "reason": reason
        }

    def _decision_12_learn_from_query(self, question: str, query_type: Dict, target_level: Dict, confidence: Dict) -> Dict:
        """РЕШЕНИЕ 12: Обучение на запросе (НОВОЕ)"""
        # Создание профиля запроса
        q_signature = query_type["type"] + "_" + str(target_level["level"])

        profile = self.query_profiles[q_signature]
        profile["count"] += 1
        profile["preferred_level"] = target_level["level"]

        # Обновление success rate
        if confidence["confidence"] > 0.7:
            profile["success_rate"] = (profile["success_rate"] * (profile["count"] - 1) + 1.0) / profile["count"]
        else:
            profile["success_rate"] = (profile["success_rate"] * (profile["count"] - 1) + 0.0) / profile["count"]

        self.stats["patterns_learned"] += 1

        return {
            "decision": "learning",
            "learned": True,
            "profile_signature": q_signature,
            "success_rate": profile["success_rate"]
        }

    def _decision_13_predict_next_query(self, question: str, context: Optional[Dict]) -> Dict:
        """РЕШЕНИЕ 13: Предсказание следующего запроса (НОВОЕ)"""
        # Анализ истории
        if len(self.query_history) < 2:
            self.query_history.append(question)
            return {
                "decision": "prediction",
                "next_query": None,
                "confidence": 0.0,
                "reason": "Недостаточно истории"
            }

        # Простая эвристика: если текущий вопрос о формуле, следующий может быть о примере
        q_lower = question.lower()

        if 'формула' in q_lower:
            prediction = "Показать примеры применения"
            conf = 0.7
        elif 'пример' in q_lower:
            prediction = "Показать алгоритм реализации"
            conf = 0.6
        elif 'алгоритм' in q_lower:
            prediction = "Показать практические советы"
            conf = 0.6
        else:
            prediction = None
            conf = 0.3

        self.query_history.append(question)
        self.stats["predictions_made"] += 1

        return {
            "decision": "prediction",
            "next_query": prediction,
            "confidence": conf,
            "based_on": "query_pattern_analysis"
        }

    def _decision_14_cache_decision(self, cache_key: str, results: List[Dict], confidence: Dict, query_type: Dict) -> Dict:
        """РЕШЕНИЕ 14: Решение о кэшировании"""
        conf = confidence["confidence"]

        # Кэшируем только если уверены
        if conf > 0.7:
            # Определяем уровень кэша
            if query_type["type"] in ["formula", "concept"]:
                # Часто используемые → L1
                self.l1_cache[cache_key] = results[:3]
                level = "l1"
            else:
                # Реже используемые → L2
                self.l2_cache[cache_key] = results[:3]
                level = "l2"

            # Управление размером кэша
            if len(self.l1_cache) > 100:
                # Eviction: удаляем старые
                oldest_key = list(self.l1_cache.keys())[0]
                del self.l1_cache[oldest_key]

            return {
                "decision": "caching",
                "cached": True,
                "cache_level": level,
                "reason": f"Уверенность {conf:.2f}"
            }
        else:
            return {
                "decision": "caching",
                "cached": False,
                "reason": f"Низкая уверенность {conf:.2f}"
            }

    def _decision_15_meta_cognition(self, decisions: List[Dict], confidence: Dict) -> Dict:
        """РЕШЕНИЕ 15: Мета-когнитивный анализ (НОВОЕ)"""
        # Агент анализирует свои собственные решения

        # Какие решения были наиболее "важными"?
        important_decisions = [
            d for d in decisions
            if d.get("decision") in ["query_type", "target_level", "confidence", "response_strategy"]
        ]

        # Оценка качества decision-making process
        decision_quality = confidence["confidence"]

        # Обновление мета-статистики
        for dec in important_decisions:
            dec_type = dec.get("decision")
            self.meta_cognition["decision_accuracy"][dec_type] = (
                self.meta_cognition["decision_accuracy"][dec_type] * 0.9 + decision_quality * 0.1
            )

        # Learning curve
        self.meta_cognition["learning_curve"].append({
            "timestamp": datetime.now().isoformat(),
            "confidence": decision_quality,
            "num_decisions": len(decisions)
        })

        # Анализ: улучшается ли агент?
        if len(self.meta_cognition["learning_curve"]) > 10:
            recent_avg = sum(
                x["confidence"] for x in self.meta_cognition["learning_curve"][-10:]
            ) / 10
            older_avg = sum(
                x["confidence"] for x in self.meta_cognition["learning_curve"][-20:-10]
            ) / 10 if len(self.meta_cognition["learning_curve"]) > 20 else recent_avg

            improvement = recent_avg - older_avg
        else:
            improvement = 0.0

        self.stats["self_optimizations"] += 1

        return {
            "decision": "meta_cognition",
            "decision_quality": decision_quality,
            "important_decisions": len(important_decisions),
            "improvement_trend": "improving" if improvement > 0.05 else "stable" if improvement > -0.05 else "declining",
            "improvement_delta": improvement,
            "self_awareness": "Агент анализирует и оптимизирует свои решения"
        }

    def _log_query(self, question: str, decisions: List[Dict], elapsed: float):
        """Логирование запроса"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "decisions": decisions,
            "elapsed_sec": elapsed
        }
        self.decision_log.append(log_entry)

    def get_statistics(self) -> Dict:
        """Получение статистики агента"""
        return {
            "stats": self.stats,
            "cache_sizes": {
                "l1": len(self.l1_cache),
                "l2": len(self.l2_cache),
                "l3": len(self.l3_cache)
            },
            "learned_profiles": len(self.query_profiles),
            "meta_cognition": {
                "decision_accuracy": dict(self.meta_cognition["decision_accuracy"]),
                "learning_curve_length": len(self.meta_cognition["learning_curve"])
            }
        }

    def explain_decision(self, decision_log_index: int = -1) -> str:
        """Объяснение решений агента (интерпретируемость)"""
        if not self.decision_log:
            return "Нет истории решений"

        log_entry = self.decision_log[decision_log_index]

        explanation = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║  ОБЪЯСНЕНИЕ РЕШЕНИЙ АГЕНТА                                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

Вопрос: {log_entry['question']}
Время обработки: {log_entry['elapsed_sec']*1000:.2f} ms

ПРИНЯТЫЕ РЕШЕНИЯ:
"""

        for i, dec in enumerate(log_entry['decisions'], 1):
            explanation += f"\n{i}. {dec.get('decision', 'unknown').upper()}\n"
            for key, value in dec.items():
                if key != 'decision':
                    explanation += f"   - {key}: {value}\n"

        return explanation


# ═══════════════════════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 80)
    print("  РАСШИРЕННЫЙ МИКРО-АГЕНТ - ДЕМОНСТРАЦИЯ")
    print("=" * 80)
    print()

    # Инициализация
    agent = AdvancedMicroAgent(knowledge_base_path="афоризмы")

    print("\n" + "="*80)
    print("ТЕСТ 1: Запрос о формуле")
    print("="*80)

    result1 = agent.query("Какая формула для 5G сетей?", top_k=3)

    print(f"\nРезультатов: {len(result1['results'])}")
    print(f"Уверенность: {result1['confidence']:.2f}")
    print(f"Тип запроса: {result1['query_type']}")
    print(f"Стратегия: {result1['strategy']}")
    print(f"Предсказание следующего запроса: {result1.get('prediction')}")
    print(f"Время: {result1['elapsed_ms']:.2f} ms")

    if result1['results']:
        print(f"\nТоп результат: {result1['results'][0]['topic']}")
        print(f"Score: {result1['results'][0]['score']}")

    print("\n" + "="*80)
    print("ТЕСТ 2: Тот же запрос (должен быть из кэша)")
    print("="*80)

    result2 = agent.query("Какая формула для 5G сетей?", top_k=3)
    print(f"Из кэша: {result2['from_cache']}")
    print(f"Время: {result2['elapsed_ms']:.2f} ms")

    print("\n" + "="*80)
    print("ТЕСТ 3: Запрос о примере")
    print("="*80)

    result3 = agent.query("Покажи примеры IoT устройств", top_k=3)
    print(f"Результатов: {len(result3['results'])}")
    print(f"Уверенность: {result3['confidence']:.2f}")
    print(f"Предсказание: {result3.get('prediction')}")

    print("\n" + "="*80)
    print("СТАТИСТИКА АГЕНТА")
    print("="*80)

    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n" + "="*80)
    print("ОБЪЯСНЕНИЕ ПОСЛЕДНЕГО РЕШЕНИЯ")
    print("="*80)

    explanation = agent.explain_decision(-1)
    print(explanation)

    print("\n✓ Демонстрация завершена!")
    print(f"  Всего запросов: {agent.stats['queries']}")
    print(f"  Решений принято: {agent.stats['decisions_made']}")
    print(f"  Паттернов изучено: {agent.stats['patterns_learned']}")
    print(f"  Самооптимизаций: {agent.stats['self_optimizations']}")
