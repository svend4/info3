# РАСШИРЕННАЯ АРХИТЕКТУРА: МИКРО-АГЕНТЫ И ИНФОБРОКЕРЫ

## 📚 Оглавление

- [Обзор](#обзор)
- [Философия](#философия)
- [Компоненты системы](#компоненты-системы)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Примеры использования](#примеры-использования)
- [API Reference](#api-reference)

---

## 🎯 Обзор

Это **расширенная версия** RAG системы для 4-уровневой базы знаний.

**Что нового:**
- ✨ **15 типов автономных решений** (было 8)
- 🧠 **Мета-когнитивный анализ** (агент анализирует свои решения)
- 🤖 **Мульти-агентная система** (специализированные агенты для каждого уровня)
- 📮 **Инфоброкер** (посредник между AI и данными)
- 🎓 **Самообучение** на основе истории запросов
- 🔮 **Предсказание** следующих запросов
- 🎯 **Интеграция с GPT/Claude** (готовые сценарии)

**Базовая версия** (simple):
```
micro_agent_simple.py      - 8 решений, нет зависимостей
rag_api_server.py          - FastAPI сервер с semantic search
```

**Расширенная версия** (advanced):
```
advanced_micro_agent.py    - 15 решений + самообучение + мета-анализ
info_broker.py             - Инфоброкер с маршрутизацией
multi_agent_system.py      - Мульти-агентная архитектура
integration_examples.py    - Интеграция с GPT/Claude
```

---

## 🧠 Философия

### Концепция "Информационного Redis"

Традиционный Redis кэширует **данные**. Наша система кэширует **знания** и **паттерны**.

```
┌─────────────┐           ┌──────────────────┐           ┌──────────────┐
│   AI/LLM    │ ◄────────►│   InfoBroker     │◄─────────►│  Knowledge   │
│  (GPT/      │           │  (Посредник)     │           │     Base     │
│   Claude)   │           │                  │           │  (4 уровня)  │
└─────────────┘           └──────────────────┘           └──────────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                     ┌────▼─────┐    ┌─────▼────┐
                     │  Agents  │    │  Cache   │
                     │ (Специа- │    │(Паттерны)│
                     │ листы)   │    │          │
                     └──────────┘    └──────────┘
```

**Роли инфоброкера:**
- 🚚 **Коммивояжёр**: доставляет нужную информацию в нужное место
- 🎯 **Курьер**: быстрая доставка срочных знаний
- 📮 **Почтальон**: регулярная доставка паттернов
- 🔀 **Маршрутизатор**: выбирает оптимальный путь к данным

---

## 🏗️ Компоненты системы

### 1. Advanced Micro Agent

**Файл:** `advanced_micro_agent.py`

**Возможности:**
- 15 типов автономных решений:
  1. Проверка 3-уровневого кэша (L1/L2/L3)
  2. Расширенный анализ типа запроса
  3. Интеллектуальный выбор целевого уровня
  4. Выбор метода поиска
  5. Умное извлечение ключевых слов с синонимами
  6. **НОВОЕ:** Проверка паттерн-кэша
  7. Поиск в базе знаний
  8. Улучшенное ранжирование
  9. Оценка уверенности
  10. **НОВОЕ:** Обогащение контекстом
  11. Определение стратегии ответа
  12. **НОВОЕ:** Обучение на запросе
  13. **НОВОЕ:** Предсказание следующего запроса
  14. Решение о кэшировании
  15. **НОВОЕ:** Мета-когнитивный анализ

**Пример использования:**
```python
from advanced_micro_agent import AdvancedMicroAgent

agent = AdvancedMicroAgent(knowledge_base_path="афоризмы")

result = agent.query("Как защититься от DDoS?", top_k=5)

print(f"Уверенность: {result['confidence']}")
print(f"Предсказание: {result['prediction']}")
print(f"Решений принято: {len(result['decisions'])}")
print(f"Мета-анализ: {result['meta_analysis']}")
```

**Статистика:**
```python
stats = agent.get_statistics()
# {
#   "queries": 42,
#   "cache_hits": {"l1": 10, "l2": 5, "l3": 2},
#   "patterns_learned": 15,
#   "predictions_made": 42,
#   "self_optimizations": 42
# }
```

---

### 2. Info Broker

**Файл:** `info_broker.py`

**Концепция:** Посредник между AI-системой и структурированными данными.

**Намерения запросов** (автоопределение):
- `SOLVE_PROBLEM` - Решить конкретную проблему
- `LEARN_CONCEPT` - Изучить концепцию
- `FIND_ANALOGY` - Найти аналогию
- `GET_FORMULA` - Получить формулу
- `SEE_EXAMPLES` - Увидеть примеры
- `VALIDATE_APPROACH` - Валидировать подход
- `EXPLORE_DOMAIN` - Исследовать область
- `COMPARE_OPTIONS` - Сравнить опции

**Маршруты доставки:**
- `EXPRESS` - Самый быстрый (кэш)
- `STANDARD` - Обычный поиск
- `DEEP_SEARCH` - Глубокий поиск
- `MULTI_SOURCE` - Из нескольких источников
- `SYNTHESIZE` - Синтезировать из частей

**Пример использования:**
```python
from info_broker import InfoBroker, QueryIntent

broker = InfoBroker(knowledge_base_path="афоризмы")

package = broker.serve(
    query="Какая формула для 5G?",
    intent=QueryIntent.GET_FORMULA,  # Опционально
    urgency="critical"  # или "high", "normal", "low"
)

print(f"Маршрут: {package.route_taken}")
print(f"Время доставки: {package.delivery_time_ms:.2f} ms")
print(f"Уверенность: {package.confidence}")
print(f"Источники: {', '.join(package.sources)}")

for rec in package.recommendations:
    print(f"  💡 {rec}")
```

**Статистика:**
```python
stats = broker.get_statistics()
# {
#   "requests_served": 100,
#   "avg_delivery_time_ms": 45.2,
#   "routes_used": {"express": 30, "standard": 50, ...},
#   "customer_satisfaction": 0.85
# }
```

---

### 3. Multi-Agent System

**Файл:** `multi_agent_system.py`

**Концепция:** Специализированные агенты для каждого уровня 4-уровневой системы.

**Агенты:**
```
┌────────────────────────────────────────────────┐
│         CoordinatorAgent                       │
│    (Координирует всех агентов)                 │
└──────┬──────────┬──────────┬──────────┬────────┘
       │          │          │          │
   ┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌──▼────┐
   │Formula│  │Arche-│  │Algo-  │  │Theorem│
   │ Agent │  │ type │  │ rithm │  │ Agent │
   │       │  │Agent │  │ Agent │  │       │
   │(Ур.1) │  │(Ур.2)│  │(Ур.3) │  │(Ур.4) │
   └───────┘  └──────┘  └───────┘  └───────┘
```

**Специализация:**
- **FormulaAgent** (Уровень 1): Эксперт по математическим формулам
- **ArchetypeAgent** (Уровень 2): Эксперт по структурам и компонентам
- **AlgorithmAgent** (Уровень 3): Эксперт по процессам и алгоритмам
- **TheoremAgent** (Уровень 4): Эксперт по практическим примерам

**Пример использования:**
```python
from multi_agent_system import MultiAgentSystem

system = MultiAgentSystem(knowledge_base_path="афоризмы")

result = system.query("Расскажи про blockchain")

print(f"Агентов использовано: {len(result['agents_used'])}")
print(f"Уверенность: {result['confidence']}")

# Результаты по уровням
for agent, items in result['results_by_level'].items():
    print(f"\n{agent}:")
    for item in items:
        print(f"  • {item['topic']}")

# Производительность агентов
for agent, perf in result['meta']['agent_performance'].items():
    print(f"{agent}: {perf['confidence']:.2f}, {perf['time_ms']:.1f}ms")
```

**Когда какой агент используется:**
- `"формула"` в запросе → FormulaAgent
- `"как", "шаг"` → AlgorithmAgent
- `"пример", "случай"` → TheoremAgent
- `"структура", "компонент"` → ArchetypeAgent
- Без явных сигналов → все агенты (комплексный запрос)

---

### 4. Integration Examples

**Файл:** `integration_examples.py`

**Готовые сценарии интеграции с GPT/Claude:**

#### 4.1. AI Learning Assistant

Концепция: AI учится из базы знаний перед решением задачи.

```python
from integration_examples import AILearningAssistant

learner = AILearningAssistant(knowledge_system)

result = learner.learn_before_solve(
    "Как оптимизировать производительность 5G сети?"
)

# Отправь prompt в GPT/Claude
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": result['prompt_for_ai']}]
)
```

#### 4.2. Autonomous Advisor

Концепция: AI даёт советы на основе похожих примеров из базы.

```python
from integration_examples import AutonomousAdvisor

advisor = AutonomousAdvisor(knowledge_system)

result = advisor.give_advice(
    "Моя компания хочет внедрить IoT, но переживаем за безопасность"
)

print(result['advice'])
print(f"Источники: {result['sources']}")
```

#### 4.3. Analogy Generator

Концепция: Поиск аналогий между концепциями в разных доменах.

```python
from integration_examples import AnalogyGenerator

analogy_gen = AnalogyGenerator(knowledge_system)

result = analogy_gen.find_analogies("5G сети", target_domain="биология")

# Отправь prompt в Claude
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": result['prompt_for_ai']}]
)
```

#### 4.4. Solution Validator

Концепция: Валидация решений по формулам из базы знаний.

```python
from integration_examples import SolutionValidator

validator = SolutionValidator(knowledge_system)

result = validator.validate(
    problem="Нужно улучшить покрытие 5G",
    proposed_solution="Установить больше mmWave станций"
)

# Валидация через AI
validation_response = call_ai(result['prompt_for_ai'])
```

---

## 🚀 Быстрый старт

### Установка

```bash
# Базовые зависимости (если используете advanced_micro_agent.py)
pip install -r requirements.txt

# Минимальные зависимости (если используете integration_examples.py)
# Нет дополнительных зависимостей!
```

### Пример 1: Простой запрос

```python
from advanced_micro_agent import AdvancedMicroAgent

agent = AdvancedMicroAgent("афоризмы")
result = agent.query("Какая формула для IoT?")

print(f"Результаты: {len(result['results'])}")
print(f"Уверенность: {result['confidence']:.0%}")
```

### Пример 2: Через инфоброкера

```python
from info_broker import InfoBroker

broker = InfoBroker("афоризмы")
package = broker.serve(
    "Покажи примеры blockchain атак",
    urgency="high"
)

print(f"Маршрут: {package.route_taken}")
print(f"Время: {package.delivery_time_ms:.1f}ms")
```

### Пример 3: Мульти-агентная система

```python
from multi_agent_system import MultiAgentSystem

system = MultiAgentSystem("афоризмы")
result = system.query("Расскажи про квантовые вычисления")

print(f"Агентов: {len(result['agents_used'])}")
for agent in result['agents_used']:
    print(f"  • {agent}")
```

---

## 📊 Сравнение версий

| Функция | Simple | Advanced | Multi-Agent | InfoBroker |
|---------|--------|----------|-------------|------------|
| Автономные решения | 8 | 15 | - | 5 |
| Самообучение | ❌ | ✅ | ✅ | ❌ |
| Предсказания | ❌ | ✅ | ❌ | ❌ |
| Мета-анализ | ❌ | ✅ | ❌ | ❌ |
| Специализация | ❌ | ❌ | ✅ | ✅ |
| Маршрутизация | ❌ | ❌ | ✅ | ✅ |
| Зависимости | 0 | 0 | 0 | 0 |
| Semantic search | ❌ | ❌ | ❌ | ❌ |

**Примечание:** Для semantic search используйте `rag_api_server.py` (FastAPI + Sentence Transformers + FAISS).

---

## 🎯 Когда что использовать

### Используй `advanced_micro_agent.py` если:
- Нужно самообучение на основе истории
- Важна мета-когнитивность (агент анализирует себя)
- Хочешь предсказания следующих запросов
- Нужен многоуровневый кэш (L1/L2/L3)

### Используй `multi_agent_system.py` если:
- Нужна специализация по уровням (формулы/архетипы/алгоритмы/теоремы)
- Хочешь параллельную обработку (каждый агент независим)
- Важна прозрачность (видно какой агент что нашёл)

### Используй `info_broker.py` если:
- Нужна маршрутизация запросов (EXPRESS/STANDARD/DEEP)
- Важно понимание намерений (SOLVE_PROBLEM/LEARN_CONCEPT/etc)
- Хочешь разную срочность обработки (critical/high/normal/low)

### Используй `integration_examples.py` если:
- Интегрируешь с GPT/Claude
- Нужны готовые промпты для AI
- Хочешь RAG паттерн из коробки

---

## 🔬 Продвинутые возможности

### 1. Мета-когнитивный анализ

Агент анализирует свои собственные решения:

```python
result = agent.query("вопрос")

meta = result['meta_analysis']
print(f"Качество решений: {meta['decision_quality']}")
print(f"Тренд: {meta['improvement_trend']}")  # improving/stable/declining
print(f"Улучшение: {meta['improvement_delta']:+.2f}")
```

### 2. Объяснение решений (Explainability)

```python
explanation = agent.explain_decision(-1)  # Последнее решение
print(explanation)

# Вывод:
# ╔════════════════════════════════════════╗
# ║  ОБЪЯСНЕНИЕ РЕШЕНИЙ АГЕНТА             ║
# ╚════════════════════════════════════════╝
#
# Вопрос: Как защититься от DDoS?
# Время обработки: 45.2 ms
#
# ПРИНЯТЫЕ РЕШЕНИЯ:
# 1. CACHE_CHECK
#    - action: cache_miss
#    - reason: Данных в кэше нет
# ...
```

### 3. Обучение из истории

Агент автоматически обучается:

```python
# После 100 запросов
stats = agent.get_statistics()

print(stats['learned_profiles'])
# 15  (выучено 15 профилей запросов)

print(agent.query_profiles)
# {
#   "formula_[1]": {
#     "count": 25,
#     "success_rate": 0.92,
#     "preferred_level": [1]
#   },
#   ...
# }
```

### 4. Предсказание следующего запроса

```python
result = agent.query("Какая формула для 5G?")

prediction = result['prediction']
print(prediction)
# "Показать примеры применения"  (с confidence 0.7)
```

---

## 🏭 Production Deployment

### Docker Compose (рекомендуется)

```yaml
version: '3.8'

services:
  advanced-rag:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./афоризмы:/app/афоризмы:ro
    environment:
      - KNOWLEDGE_BASE_PATH=/app/афоризмы
    command: python3 advanced_micro_agent.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Масштабирование

```bash
# Несколько воркеров
docker-compose up --scale advanced-rag=4

# Или с nginx load balancer
docker-compose -f docker-compose.prod.yml up
```

### Мониторинг

```python
# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    stats = agent.get_statistics()

    return f"""
# HELP queries_total Total number of queries processed
# TYPE queries_total counter
queries_total {stats['stats']['queries']}

# HELP cache_hits_total Total cache hits by level
# TYPE cache_hits_total counter
cache_hits_l1_total {stats['stats']['cache_hits']['l1']}
cache_hits_l2_total {stats['stats']['cache_hits']['l2']}
cache_hits_l3_total {stats['stats']['cache_hits']['l3']}

# HELP patterns_learned_total Total patterns learned
# TYPE patterns_learned_total counter
patterns_learned_total {stats['stats']['patterns_learned']}
    """
```

---

## 🧪 Тестирование

### Unit Tests

```python
# test_advanced_agent.py
import unittest
from advanced_micro_agent import AdvancedMicroAgent

class TestAdvancedAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AdvancedMicroAgent("афоризмы")

    def test_query_returns_results(self):
        result = self.agent.query("тест")
        self.assertIn('results', result)
        self.assertIn('confidence', result)

    def test_meta_cognition(self):
        result = self.agent.query("тест")
        self.assertIn('meta_analysis', result)
        self.assertIn('improvement_trend', result['meta_analysis'])

if __name__ == '__main__':
    unittest.main()
```

### Performance Tests

```python
# benchmark.py
import time
from advanced_micro_agent import AdvancedMicroAgent

agent = AdvancedMicroAgent("афоризмы")

# Warm-up
for _ in range(10):
    agent.query("тест")

# Benchmark
times = []
for _ in range(100):
    start = time.time()
    agent.query("формула 5G")
    times.append(time.time() - start)

print(f"Среднее время: {sum(times)/len(times)*1000:.2f} ms")
print(f"p95: {sorted(times)[95]*1000:.2f} ms")
print(f"p99: {sorted(times)[99]*1000:.2f} ms")
```

---

## 🤝 Contributing

Вклад приветствуется! Области для улучшения:

1. **Semantic Search**: Интеграция с vector databases (Pinecone, Weaviate)
2. **Multilingual**: Поддержка нескольких языков
3. **Graph Knowledge**: Графовое представление связей между концепциями
4. **Active Learning**: Агент запрашивает недостающие знания
5. **Federated Learning**: Обучение на данных от нескольких пользователей

---

## 📄 Лицензия

MIT License

---

## 🙏 Благодарности

Система построена на идеях:
- RAG (Retrieval-Augmented Generation)
- Multi-Agent Systems
- Meta-Learning
- Cognitive Architectures

---

## 📞 Поддержка

Если есть вопросы:
1. Прочитай `RAG-QUICKSTART.md` (базовое использование)
2. Прочитай `VISUAL-GUIDE.md` (визуальные схемы)
3. Посмотри примеры в `integration_examples.py`

---

Создано с ❤️ для интеграции AI с структурированными знаниями
