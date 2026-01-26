# Machine-Readable форматы для 4-уровневой системы познания

Этот каталог содержит машиночитаемые представления 4-уровневой системы знаний, оптимизированные для обработки нейросетями, AI-системами и программного кода.

## 📁 Структура файлов

```
machine-readable/
├── README.md                          # Этот файл
├── искусственный-интеллект.json      # JSON формат (строгая структура)
├── искусственный-интеллект.yaml      # YAML формат (читаемый)
├── knowledge_system.py                # Python модуль для работы с данными
├── demo.py                            # Демонстрация использования
├── ai_integration.py                  # Интеграция с AI/ML библиотеками
└── training_data_ai.json              # Сгенерированные тренировочные данные
```

## 🎯 Назначение

Эти форматы предназначены для:

1. **AI/ML обработки** - обучение нейросетей, fine-tuning LLM
2. **Программной реализации** - использование в коде, API
3. **Автоматизации** - скрипты, пайплайны обработки данных
4. **Интеграция** - встраивание в существующие системы

## 📊 Форматы данных

### JSON (.json)
- **Для**: API, JavaScript, строгая типизация
- **Плюсы**: Универсальная поддержка, строгая структура
- **Минусы**: Многословный, хуже читается человеком

### YAML (.yaml)
- **Для**: Конфигурация, человеческое чтение
- **Плюсы**: Компактный, читаемый, меньше символов
- **Минусы**: Чувствителен к отступам

### Python Module (.py)
- **Для**: Программная обработка на Python
- **Плюсы**: Объектно-ориентированный API, типизация
- **Минусы**: Только для Python

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install pyyaml  # Для работы с YAML
```

### 2. Базовое использование

```python
from knowledge_system import KnowledgeSystem

# Загрузка из JSON
ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

# Получение формулы
formula = ks.get_formula()
print(formula.explain())

# Поиск информации
results = ks.search('ChatGPT')

# Получение примеров
examples = ks.find_examples('автопилот')
```

### 3. Запуск демонстрации

```bash
python demo.py
```

Это запустит 9 интерактивных демонстраций, показывающих:
- Базовую загрузку и просмотр данных
- Поиск и запросы
- Обработку алгоритмов
- Генерацию тренировочных данных для AI
- Извлечение ключевых слов
- И многое другое

## 💡 Примеры использования

### Пример 1: Поиск информации

```python
from knowledge_system import KnowledgeSystem

ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

# Поиск по всей системе
results = ks.search('overfitting')
print(results)

# Поиск конкретных примеров
examples = ks.find_examples('Tesla')
for ex in examples:
    print(ex['name'], ':', ex.get('lesson'))
```

### Пример 2: Генерация данных для обучения LLM

```python
from knowledge_system import generate_training_data
import json

ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

# Генерация пар вопрос-ответ
training_data = generate_training_data(ks)

# Сохранение для fine-tuning
with open('training_data.jsonl', 'w', encoding='utf-8') as f:
    for item in training_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

### Пример 3: Извлечение ключевых слов

```python
from knowledge_system import extract_keywords

ks = KnowledgeSystem.from_json('искусственный-интеллект.json')

# Топ-20 ключевых слов
keywords = extract_keywords(ks, top_n=20)
print(keywords)
```

### Пример 4: Работа с алгоритмом

```python
ks = KnowledgeSystem.from_json('искусственный-интеллект.json')
algorithm = ks.get_algorithm()

# Список всех шагов
for i, step_name in enumerate(algorithm.step_names(), 1):
    print(f"{i}. {step_name}")

# Детали конкретного шага
step = algorithm.get_step(4)
print(f"Шаг 4: {step['name']}")
```

## 🤖 Интеграция с AI/ML

### Для обучения нейросетей

```python
# 1. Генерация тренировочных данных
training_data = generate_training_data(ks)

# 2. Формат для OpenAI fine-tuning
openai_format = [
    {
        "messages": [
            {"role": "user", "content": item['question']},
            {"role": "assistant", "content": item['answer']}
        ]
    }
    for item in training_data
]

# 3. Сохранение
with open('openai_training.jsonl', 'w') as f:
    for item in openai_format:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

### Для semantic search (векторный поиск)

```python
# Использование с популярными библиотеками:
# - sentence-transformers для создания эмбеддингов
# - FAISS для векторного поиска
# - ChromaDB для векторной базы данных

# См. ai_integration.py для полных примеров
```

### Для RAG (Retrieval-Augmented Generation)

```python
# 1. Индексировать все уровни системы знаний
# 2. На вопрос пользователя найти релевантные фрагменты
# 3. Передать в LLM как контекст
# 4. Получить ответ на основе знаний

# См. ai_integration.py для реализации
```

## 📖 Структура данных

Каждый файл содержит 4 уровня:

```
level_1_formula:        # Формула - абстрактное, техническое
  ├─ expression         # Математическое выражение
  └─ variables          # Переменные и их значения

level_2_archetype:      # Архетип - расширенная формула
  ├─ components         # Компоненты системы
  └─ extended_formula   # Детальная формула

level_3_algorithm:      # Алгоритм - пошаговый процесс
  ├─ steps[]            # Массив шагов
  └─ pipeline_name      # Название пайплайна

level_4_theorem:        # Теорема - конкретные примеры
  ├─ main_theorem       # Главный афоризм/теорема
  ├─ key_insights[]     # Ключевые инсайты
  ├─ real_world_examples[]  # Реальные примеры
  └─ practical_advice[] # Практические советы
```

## 🔧 API модуля knowledge_system.py

### Классы

- **`KnowledgeSystem`** - главный класс для работы с системой знаний
- **`Formula`** - уровень 1 (формула)
- **`Archetype`** - уровень 2 (архетип)
- **`Algorithm`** - уровень 3 (алгоритм)
- **`Theorem`** - уровень 4 (теорема)

### Основные методы

```python
# Загрузка
ks = KnowledgeSystem.from_json(filepath)
ks = KnowledgeSystem.from_yaml(filepath)

# Получение уровней
ks.get_formula()        # Уровень 1
ks.get_archetype()      # Уровень 2
ks.get_algorithm()      # Уровень 3
ks.get_theorem()        # Уровень 4

# Поиск
ks.search(keyword)                 # Поиск по всем уровням
ks.find_examples(keyword)          # Поиск примеров
ks.get_practical_advice()          # Практические советы
ks.get_aphorisms()                 # Афоризмы

# Экспорт
ks.to_summary()                    # Краткое резюме
ks.export_to_json(filepath)        # Экспорт в JSON
ks.export_to_yaml(filepath)        # Экспорт в YAML
```

### Вспомогательные функции

```python
# Сравнение систем
compare_knowledge_systems(ks1, ks2)

# Извлечение ключевых слов
extract_keywords(ks, top_n=10)

# Генерация тренировочных данных
generate_training_data(ks)
```

## 📈 Применения

### 1. Чатботы и Q&A системы
- Индексировать знания
- Отвечать на вопросы пользователей
- Предоставлять контекстные советы

### 2. LLM Fine-tuning
- Генерация датасетов для обучения
- Supervised fine-tuning
- RLHF (Reinforcement Learning from Human Feedback)

### 3. Semantic Search
- Векторный поиск по знаниям
- Рекомендации похожих тем
- Кластеризация контента

### 4. Knowledge Graphs
- Построение графов знаний
- Связи между концепциями
- Визуализация системы

### 5. Аналитика и insights
- Извлечение ключевых слов
- Анализ тенденций
- Выявление паттернов

## 🛠️ Расширение

Чтобы добавить новую тему:

1. Создайте JSON/YAML файл с той же структурой
2. Используйте `KnowledgeSystem.from_json()` для загрузки
3. Все методы работают автоматически

Пример:

```python
# Создание новой темы
new_topic = {
    "metadata": {
        "topic": "квантовые-вычисления",
        "title": "Квантовые вычисления",
        ...
    },
    "level_1_formula": {...},
    "level_2_archetype": {...},
    "level_3_algorithm": {...},
    "level_4_theorem": {...}
}

# Сохранение
with open('квантовые-вычисления.json', 'w') as f:
    json.dump(new_topic, f, ensure_ascii=False, indent=2)

# Загрузка и использование
ks = KnowledgeSystem.from_json('квантовые-вычисления.json')
```

## 📚 Дополнительные ресурсы

- `demo.py` - интерактивные примеры использования
- `ai_integration.py` - интеграция с AI/ML библиотеками
- `knowledge_system.py` - исходный код модуля с документацией

## 🤝 Использование в проектах

Эти форматы могут быть использованы в:

- **Web приложениях** - JSON API для фронтенда
- **Микросервисах** - обмен данными между сервисами
- **ML пайплайнах** - предобработка для моделей
- **Базах данных** - NoSQL (MongoDB), векторных БД (Pinecone, Weaviate)
- **Поисковых системах** - Elasticsearch, Algolia
- **GraphQL** - схема для запросов

## 📝 Лицензия

Свободное использование для образовательных и исследовательских целей.

---

**Версия**: 1.0
**Дата**: 2026-01-26
**Формат**: 4-уровневая система познания (Формула → Архетип → Алгоритм → Теорема)
