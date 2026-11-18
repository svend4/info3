# Info3 — Четырёхуровневая система познания и RAG-платформа (`info3`)

## Назначение проекта

Репозиторий `info3` объединяет структурированную базу гуманитарных и технических знаний (формулы, архетипы, алгоритмы и теоремы/афоризмы) с машиночитаемыми форматами (`JSON`/`YAML`), Python-инфраструктурой для псевдо-RAG и AI-агентов, а также веб-интерфейсом для семантического поиска и мониторинга.

## Архитектура и основные компоненты

### 1. Четырёхуровневая система познания (`афоризмы/` и тематические каталоги)

Базовая методология описана в [`ФОРМАТЫ-README.md`](ФОРМАТЫ-README.md), [`афоризмы/УРОВНИ-README.md`](афоризмы/УРОВНИ-README.md) и [`афоризмы/ФОРМУЛЫ-README.md`](афоризмы/ФОРМУЛЫ-README.md). Знания организованы по 4 уровням абстракции:

1. **Уровень 1 — ФОРМУЛА:** компактное математическое или символьное выражение сути явления (например, `S = T × W`).
2. **Уровень 2 — АРХЕТИП:** развёрнутая формула с описанием переменных и факторов.
3. **Уровень 3 — АЛГОРИТМ:** пошаговый процесс, условия и ветвления.
4. **Уровень 4 — ТЕОРЕМА:** конкретные утверждения, афоризмы, контекст и жизненные примеры.

Материалы распределены по:
- **24 корневым тематическим каталогам** парных понятий (например, `бережливость-и-расточительность`, `верность-слову-и-вероломство`, `доверие-и-подозрительность`, `логичность-и-алогичность`, `усердие-и-халатность` и др.);
- **каталогу [`афоризмы/`](афоризмы/)**, объединяющему сотни предметных разделов (в `афоризмы/ФОРМУЛЫ-README.md` упоминается 446 файлов с афоризмами / ~90 000 теорем), сводный индекс `афоризмы/README.md` и руководства по уровням и формулам.

### 2. Машиночитаемые данные, RAG-сервер и агентные модули (`machine-readable/`)

Подробная документация приведена в [`machine-readable/README.md`](machine-readable/README.md) и [`machine-readable/RAG-ARCHITECTURE-ANALYSIS.md`](machine-readable/RAG-ARCHITECTURE-ANALYSIS.md):

- **Данные и базовая библиотека:**
  - `искусственный-интеллект.json`, `искусственный-интеллект.yaml` — эталонные 4-уровневые представления темы «Искусственный интеллект»;
  - `knowledge_system.py` — классы `KnowledgeSystem`, `Formula`, `Archetype`, `Algorithm`, `Theorem`, загрузка/экспорт JSON/YAML, поиск, извлечение ключевых слов (`extract_keywords`) и генерация обучающих пар (`generate_training_data`);
  - `demo.py`, `ai_integration.py`, `integration_examples.py`, `rag_client_examples.py`.
- **Серверы и API:**
  - `production_api.py` (REST API на FastAPI, порт `8000` по умолчанию), `rag_api_server.py`, `websocket_server.py` (потоковая передача результатов по WebSocket, порт `8001`), `persistent_storage.py`.
- **Поиск, графы и экспериментальные модули:**
  - `semantic_search_agent.py`, `graph_knowledge_base.py`, `micro_agent_simple.py`, `advanced_micro_agent.py`, `multi_agent_system.py`, `active_learning.py`, `adversarial_validation.py`, `cognitive_architecture.py`, `neural_symbolic_integration.py`, `self_evolving_kb.py`, `meta_learning.py`, `federated_learning.py`, `swarm_intelligence.py`, `multi_modal_knowledge.py`, `info_broker.py` и ряд исследовательских прототипов (`akashic_records.py`, `automated_extraction.py`, `collective_consciousness.py`, `consciousness_agent.py`, `emergent_synthesis.py`, `knowledge_matrix.py`, `knowledge_telepathy.py`, `quantum_knowledge.py`, `time_traveling_knowledge.py`, `universal_knowledge.py`, `universal_translator.py`).
- **Архитектурная документация:** `ADVANCED-README.md`, `RAG-ARCHITECTURE-ANALYSIS.md` (5 уровней зрелости RAG — от JSON-прототипа до самообучающейся системы), `RAG-QUICKSTART.md`, `IMPLEMENTATION-STATUS.md`, `FUTURE-ROADMAP.md`, `VISUAL-GUIDE.md`.

### 3. Веб-интерфейс (`frontend/`)

Дашборд семантического поиска описан в [`frontend/README.md`](frontend/README.md) и не требует этапа сборки (библиотеки подключаются через CDN):

- `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`, `frontend/serve.py`.
- **Компоненты UI:** `AuthForm` (JWT вход/регистрация) и `Dashboard` (`Header`, `SearchBar` с автодополнением и выбором режима `semantic` / `keyword` / `hybrid`, `ResultsList` / `ResultCard`, `MetricsPanel` с графиками `Chart.js`, `HistoryPanel`).
- Подключается к `production_api` (`http://localhost:8000`) и `websocket_server` (`ws://localhost:8001/ws`).

## Стек технологий и структура каталогов

- **Backend / AI / RAG (`machine-readable/requirements.txt`):**
  - Python 3, `fastapi>=0.104.0`, `uvicorn[standard]>=0.24.0`, `pydantic>=2.5.0`;
  - векторный поиск и ML: `sentence-transformers>=2.2.2`, `faiss-cpu>=1.7.4`, `numpy>=1.24.0`;
  - безопасность, лимиты, метрики и хранение: `pyjwt>=2.8.0`, `slowapi>=0.1.9`, `python-multipart>=0.0.6`, `prometheus-client>=0.19.0`, `redis>=5.0.0`, `neo4j>=5.14.0`, `networkx>=3.0`, `requests>=2.31.0` (опционально `openai`, `langchain`, `pyyaml`, `pillow`).
- **Frontend (`frontend/`):** React 18, TailwindCSS 3, Chart.js 4, Babel Standalone (CDN).
- **Форматы данных:** `.txt` с Unicode-разметкой, Markdown (`.md`), JSON, YAML.

Структура ветки `main`:

```text
info3/
├── LICENSE                                  # Лицензия GNU AGPLv3
├── README.md                                # Обзор репозитория
├── ФОРМАТЫ-README.md                        # Сравнение форматов хранения (.txt, .md, JSON, YAML, XML, SQL, NoSQL, LaTeX)
├── frontend/                                # React-дашборд (index.html, app.js, styles.css, serve.py, README.md)
├── machine-readable/                        # JSON/YAML-данные, Python-модули RAG/агентов, API и документация
├── афоризмы/                                # Сотни тематических разделов с афоризмами и формулами (+ README.md, УРОВНИ-README.md, ФОРМУЛЫ-README.md)
└── <24 тематических каталога пар понятий>/  # Например: бережливость-и-расточительность/, логичность-и-алогичность/ и др.
```

### Быстрый старт (согласно `machine-readable/README.md` и `frontend/README.md`)

```bash
# Базовая демонстрация модуля knowledge_system
cd machine-readable
pip install pyyaml
python demo.py

# Запуск Production API и WebSocket-сервера (после pip install -r requirements.txt)
uvicorn production_api:app --host 0.0.0.0 --port 8000 --reload
uvicorn websocket_server:app --host 0.0.0.0 --port 8001 --reload

# Запуск статического фронтенда (в каталоге frontend/)
cd ../frontend
python3 -m http.server 8080
```

## Ветки и статус разработки

- **`main`** — основная ветка; содержит базу знаний (`афоризмы/` и 24 тематических каталога), `machine-readable/`, `frontend/`, `ФОРМАТЫ-README.md` и файл `LICENSE`.
- **`docs/align-licence-agpl`** (открытый **PR #9**: *«Документация: лицензия приведена в соответствие с LICENSE (AGPL-3.0-only)»*) — приводит формулировки лицензии в шести Markdown-файлах (`README.md`, `machine-readable/README.md`, `machine-readable/RAG-QUICKSTART.md`, `machine-readable/ADVANCED-README.md`, `frontend/README.md`, `афоризмы/ФОРМУЛЫ-README.md`) к единой `AGPL-3.0-only`.
- **`claude/check-repo-status-1j5k7`** — более ранняя ветка с кратким `README.md` (13 байт) и без корневого `LICENSE`.

## Лицензия

Проект распространяется под лицензией **GNU Affero General Public License v3.0 (`AGPL-3.0-only`)** — полный текст находится в файле [`LICENSE`](LICENSE). (В отдельных файлах ветки `main` до влития PR #9 присутствуют устаревшие упоминания MIT / свободного использования для исследований.)
