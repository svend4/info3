# 🚀 БЫСТРЫЙ СТАРТ: RAG МИКРО-АГЕНТ СИСТЕМА

## 📋 Содержание

1. [Что это?](#что-это)
2. [Быстрый запуск за 5 минут](#быстрый-запуск-за-5-минут)
3. [Детальная установка](#детальная-установка)
4. [Примеры использования](#примеры-использования)
5. [API Reference](#api-reference)
6. [Архитектура](#архитектура)
7. [FAQ](#faq)

---

## 🎯 Что это?

**RAG Микро-Агент** - это автономная система-посредник между AI/LLM и вашей базой знаний.

### Концепция "Информационного Курьера"

```
AI/LLM  →  🤖 МИКРО-АГЕНТ  →  📚 БАЗА ЗНАНИЙ
          (Делает решения)   (4 уровня)

Агент автономно:
✅ Анализирует тип запроса
✅ Выбирает целевые уровни
✅ Ищет релевантную информацию
✅ Оценивает уверенность
✅ Выбирает стратегию ответа
✅ Кэширует результаты
```

### Возможности

- 🔍 **Semantic Search**: понимание смысла запросов
- 🤖 **Автономные решения**: агент сам принимает мини-решения
- ⚡ **Кэширование**: быстрые ответы на повторные запросы
- 🎯 **Умная маршрутизация**: автоматический выбор уровня знаний
- 📊 **Прозрачность**: логирование всех решений
- 🔌 **REST API**: легкая интеграция

---

## ⚡ Быстрый запуск за 5 минут

### Вариант 1: Простой агент (без зависимостей)

```bash
# 1. Убедитесь что вы в директории с базами знаний
cd machine-readable/

# 2. Запустите простой агент
python3 micro_agent_simple.py
```

**Результат**: Демонстрация работы с 5 тестовыми запросами.

---

### Вариант 2: API сервер (с semantic search)

```bash
# 1. Установите зависимости
pip install fastapi uvicorn sentence-transformers faiss-cpu pydantic

# 2. Запустите API сервер
python3 rag_api_server.py
```

**Результат**: API доступен на http://localhost:8000

Откройте в браузере:
- **Документация**: http://localhost:8000/docs
- **Проверка здоровья**: http://localhost:8000/health

---

### Вариант 3: Примеры использования

```bash
# В ДРУГОМ терминале (сервер должен быть запущен):
python3 rag_client_examples.py
```

**Результат**: 7 интерактивных примеров использования API.

---

## 📦 Детальная установка

### Системные требования

- Python 3.8+
- 2GB RAM (минимум), 4GB+ (рекомендуется для semantic search)
- 500MB свободного места (для моделей)

### Шаг 1: Клонирование (если нужно)

```bash
git clone <repository>
cd machine-readable/
```

### Шаг 2: Установка зависимостей

#### Минимальная (keyword search):
```bash
pip install fastapi uvicorn pydantic
```

#### Полная (semantic search):
```bash
pip install fastapi uvicorn pydantic sentence-transformers faiss-cpu requests
```

#### Опциональные (для интеграции):
```bash
# Для интеграции с OpenAI
pip install openai

# Для Redis кэша (production)
pip install redis

# Для продвинутого RAG
pip install langchain
```

### Шаг 3: Проверка установки

```bash
python3 -c "import fastapi, uvicorn; print('✅ Базовые зависимости OK')"
python3 -c "from sentence_transformers import SentenceTransformer; print('✅ Semantic search OK')"
```

---

## 💡 Примеры использования

### Пример 1: Python скрипт

```python
import requests

# Отправить запрос
response = requests.post('http://localhost:8000/query', json={
    "question": "Что такое overfitting?",
    "top_k": 5,
    "use_semantic": True,
    "explain": True
})

data = response.json()
print(f"Уверенность: {data['confidence']:.2%}")
for result in data['results']:
    print(f"• [{result['level']}] {result['topic']}: {result['content'][:100]}...")
```

### Пример 2: cURL

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Как работает блокчейн?",
    "top_k": 3,
    "use_semantic": true
  }'
```

### Пример 3: Интеграция с OpenAI (RAG)

```python
import openai
import requests

# 1. Получить контекст из базы знаний
response = requests.post('http://localhost:8000/query', json={
    "question": "Как защититься от ransomware?",
    "top_k": 3
})

context = "\n".join([r['content'] for r in response.json()['results']])

# 2. Отправить в GPT с контекстом
completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Используй контекст из базы знаний."},
        {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: Как защититься от ransomware?"}
    ]
)

print(completion.choices[0].message.content)
```

### Пример 4: Batch processing

```python
questions = [
    "Что такое Bitcoin?",
    "Как работает квантовый компьютер?",
    "Примеры ransomware атак"
]

for q in questions:
    response = requests.post('http://localhost:8000/query', json={"question": q})
    print(f"{q} → {response.json()['results'][0]['topic']}")
```

---

## 📚 API Reference

### POST /query

Главный endpoint для запросов к агенту.

**Request Body:**
```json
{
  "question": "Что такое overfitting?",
  "top_k": 5,
  "levels": [1, 2, 3, 4],  // null = все уровни
  "use_semantic": true,     // true = semantic, false = keyword
  "explain": false          // true = включить логи решений
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "concept",
  "target_levels": [2, 1, 4],
  "results": [
    {
      "level": 2,
      "topic": "искусственный-интеллект",
      "type": "archetype_component",
      "content": "Переобучение (Overfitting) — враг ИИ...",
      "score": 0.89
    }
  ],
  "confidence": 0.87,
  "strategy": "ranked_list",
  "decisions": [...],
  "stats": {...},
  "elapsed_ms": 45.2,
  "semantic_search_used": true
}
```

### GET /health

Проверка здоровья сервиса.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "semantic_search_available": true,
  "knowledge_bases_loaded": 3,
  "total_embeddings": 1250,
  "cache_size": 15
}
```

### GET /stats

Статистика работы агента.

**Response:**
```json
{
  "stats": {
    "queries": 127,
    "cache_hits": 23,
    "decisions_made": 1143,
    "semantic_searches": 104
  },
  "cache_size": 15,
  "total_documents": 1250,
  "recent_decisions": [...]
}
```

### POST /clear-cache

Очистка кэша.

---

## 🏗️ Архитектура

### Компоненты системы

```
┌─────────────────────────────────────────────────────────┐
│                  CLIENT (Python/JS/cURL)                │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP REST
                        ↓
┌─────────────────────────────────────────────────────────┐
│              FASTAPI SERVER (rag_api_server.py)         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  AUTONOMOUS RAG AGENT                              │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  1. Query Analyzer                           │ │ │
│  │  │     → Определяет тип запроса                 │ │ │
│  │  ├──────────────────────────────────────────────┤ │ │
│  │  │  2. Level Selector                           │ │ │
│  │  │     → Выбирает целевые уровни                │ │ │
│  │  ├──────────────────────────────────────────────┤ │ │
│  │  │  3. Search Engine                            │ │ │
│  │  │     → Semantic (FAISS) или Keyword           │ │ │
│  │  ├──────────────────────────────────────────────┤ │ │
│  │  │  4. Ranker                                   │ │ │
│  │  │     → Ранжирует по relevance                 │ │ │
│  │  ├──────────────────────────────────────────────┤ │ │
│  │  │  5. Confidence Assessor                      │ │ │
│  │  │     → Оценивает уверенность                  │ │ │
│  │  ├──────────────────────────────────────────────┤ │ │
│  │  │  6. Strategy Selector                        │ │ │
│  │  │     → Выбирает стратегию ответа              │ │ │
│  │  ├──────────────────────────────────────────────┤ │ │
│  │  │  7. Cache Manager                            │ │ │
│  │  │     → Кэширует результаты                    │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│          VECTOR DB (FAISS)                              │
│  ┌────────────────────────────────────────────────┐    │
│  │  Embeddings:                                   │    │
│  │  - Формулы (уровень 1)                         │    │
│  │  - Архетипы (уровень 2)                        │    │
│  │  - Алгоритмы (уровень 3)                       │    │
│  │  - Теоремы/Примеры (уровень 4)                 │    │
│  └────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│       KNOWLEDGE BASE (JSON files)                       │
│  - искусственный-интеллект.json                         │
│  - блокчейн-и-криптография.json                         │
│  - квантовые-вычисления.json                            │
│  - ...                                                  │
└─────────────────────────────────────────────────────────┘
```

### Поток данных (Data Flow)

```
1. USER QUERY
   ↓
2. CACHE CHECK
   ├─ HIT  → Return cached result
   └─ MISS → Continue
   ↓
3. QUERY ANALYSIS
   → Type: formula/example/algorithm/advice/concept
   ↓
4. LEVEL SELECTION
   → [1,2,3,4] depending on type
   ↓
5. SEARCH
   ├─ Semantic: query embedding → FAISS → top_k
   └─ Keyword: word matching → scoring
   ↓
6. RANKING
   → Sort by relevance score
   ↓
7. CONFIDENCE ASSESSMENT
   → 0.0 to 1.0 score
   ↓
8. STRATEGY DECISION
   ├─ >0.85: direct (single answer)
   ├─ >0.60: ranked_list (multiple options)
   ├─ >0.30: expand_search (need more)
   └─ <0.30: ask_clarification (unclear)
   ↓
9. CACHE (if confidence > 0.6)
   ↓
10. RETURN RESPONSE
```

---

## 🛠️ Продвинутые настройки

### Кастомизация агента

```python
# rag_api_server.py

# Изменить модель для embeddings
self.model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

# Изменить thresholds для confidence
def _decide_response_strategy(self, confidence: float, results: List[Dict]) -> str:
    if confidence > 0.90:  # Было 0.85
        return "direct"
    # ...
```

### Добавление новых баз знаний

1. Создайте JSON файл в формате:
```json
{
  "metadata": {"topic": "my-topic"},
  "level_1_formula": {...},
  "level_2_archetype": {...},
  "level_3_algorithm": {...},
  "level_4_theorem": {...}
}
```

2. Перезапустите сервер - автоматически индексируется

### Production deployment

#### С Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "rag_api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t rag-agent .
docker run -p 8000:8000 rag-agent
```

#### С nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name rag-api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## ❓ FAQ

### Q: Нужен ли GPU для работы?

**A:** Нет, CPU достаточно. Semantic search работает на CPU (FAISS). Первая загрузка модели ~30 секунд, дальше быстро.

### Q: Можно ли использовать без интернета?

**A:** Да, после первой загрузки модели (sentence-transformers) всё работает offline.

### Q: Как добавить свои данные?

**A:**
1. Создайте JSON файл в формате базы знаний
2. Положите в `machine-readable/`
3. Перезапустите сервер

### Q: Можно ли использовать с другими языками (не русский)?

**A:** Да, модель `paraphrase-multilingual-MiniLM-L12-v2` поддерживает 50+ языков. Просто создайте базы знаний на нужном языке.

### Q: Как масштабировать на production?

**A:**
- Используйте Redis для distributed cache
- Запустите несколько инстансов за load balancer
- Используйте persistent vector DB (Pinecone, Weaviate)
- Мониторинг: Prometheus + Grafana

### Q: Можно ли fine-tune модель?

**A:** Да, можно дообучить sentence-transformer на ваших данных:
```python
from sentence_transformers import SentenceTransformer, InputExample, losses
# Fine-tuning code...
```

### Q: Как интегрировать с ChatGPT/Claude?

**A:** См. "Пример 3: Интеграция с OpenAI" выше. Паттерн:
1. Query RAG API → получить контекст
2. Отправить контекст + вопрос в LLM
3. LLM генерирует ответ на основе контекста

---

## 📈 Roadmap

### v2.1 (планируется)
- [ ] GraphQL API
- [ ] WebSocket для streaming
- [ ] Multi-language UI

### v3.0 (будущее)
- [ ] Мульти-агентная система
- [ ] Self-learning (continuous fine-tuning)
- [ ] Knowledge graph интеграция

---

## 🤝 Вклад

Открыт для контрибуций! Идеи:
- Новые агенты (Formula Agent, Example Agent...)
- Интеграции (Langchain, LlamaIndex)
- Оптимизации (faster search, better ranking)
- Документация

---

## 📄 Лицензия

MIT License - используйте свободно!

---

## 🎓 Обучающие материалы

- [RAG-ARCHITECTURE-ANALYSIS.md](RAG-ARCHITECTURE-ANALYSIS.md) - Подробный анализ архитектур
- [knowledge_system.py](knowledge_system.py) - Python модуль для работы с базой знаний
- [demo.py](demo.py) - 9 демонстраций возможностей

---

## 📞 Поддержка

Вопросы? Проблемы?
1. Проверьте FAQ выше
2. Проверьте Issues на GitHub
3. Создайте новый Issue

---

**Готово к использованию! 🚀**

Запустите `python3 rag_api_server.py` и начинайте экспериментировать!
