#!/usr/bin/env python3
"""
ПЕРСИСТЕНТНОЕ ХРАНИЛИЩЕ ДЛЯ RAG СИСТЕМЫ
========================================

Сохранение данных между перезапусками:
- Кэш запросов и результатов
- История запросов
- Выученные паттерны
- Статистика и метрики

ПОДДЕРЖИВАЕМЫЕ БЭКЕНДЫ:
- SQLite (по умолчанию, без зависимостей)
- Redis (опциональный, для distributed систем)
- JSON файлы (fallback)

ИСПОЛЬЗОВАНИЕ:
    storage = PersistentStorage(backend="sqlite")
    storage.set("cache_key", {"data": "value"}, ttl=3600)
    data = storage.get("cache_key")
"""

import sqlite3
import json
import time
import pickle
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import hashlib

# Попытка импорта Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class StorageBackend(ABC):
    """Абстрактный базовый класс для storage бэкендов"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Получить значение"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установить значение с опциональным TTL (время жизни в секундах)"""
        pass

    @abstractmethod
    def delete(self, key: str):
        """Удалить ключ"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        pass

    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """Получить список ключей по паттерну"""
        pass

    @abstractmethod
    def clear(self):
        """Очистить всё хранилище"""
        pass


class SQLiteBackend(StorageBackend):
    """
    SQLite бэкенд для персистентного хранилища

    Преимущества:
    - Нет внешних зависимостей
    - Персистентность на диске
    - SQL запросы для сложной аналитики
    - ACID гарантии
    """

    def __init__(self, db_path: str = "storage.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Инициализация схемы БД"""
        cursor = self.conn.cursor()

        # Таблица для key-value хранилища
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at TEXT,
                expires_at TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT
            )
        """)

        # Таблица для истории запросов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                method TEXT,
                results_count INTEGER,
                confidence REAL,
                elapsed_ms REAL,
                created_at TEXT
            )
        """)

        # Таблица для паттернов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data BLOB,
                confidence REAL,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Индексы для производительности
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at
            ON kv_store(expires_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_created
            ON query_history(created_at)
        """)

        self.conn.commit()

    def get(self, key: str) -> Optional[Any]:
        """Получить значение"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT value, expires_at
            FROM kv_store
            WHERE key = ?
        """, (key,))

        row = cursor.fetchone()

        if row is None:
            return None

        # Проверка TTL
        if row['expires_at']:
            expires_at = datetime.fromisoformat(row['expires_at'])
            if datetime.now() > expires_at:
                # Истёк TTL
                self.delete(key)
                return None

        # Обновление статистики доступа
        cursor.execute("""
            UPDATE kv_store
            SET access_count = access_count + 1,
                last_accessed = ?
            WHERE key = ?
        """, (datetime.now().isoformat(), key))

        self.conn.commit()

        # Десериализация
        return pickle.loads(row['value'])

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установить значение"""
        cursor = self.conn.cursor()

        # Сериализация
        value_blob = pickle.dumps(value)

        # Вычисление expires_at
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO kv_store
            (key, value, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (key, value_blob, datetime.now().isoformat(), expires_at))

        self.conn.commit()

    def delete(self, key: str):
        """Удалить ключ"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM kv_store WHERE key = ?", (key,))
        self.conn.commit()

    def exists(self, key: str) -> bool:
        """Проверка существования"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM kv_store WHERE key = ?", (key,))
        return cursor.fetchone() is not None

    def keys(self, pattern: str = "*") -> List[str]:
        """Получить список ключей"""
        cursor = self.conn.cursor()

        # Простой wildcard поиск
        if pattern == "*":
            cursor.execute("SELECT key FROM kv_store")
        else:
            # SQLite LIKE паттерн
            like_pattern = pattern.replace("*", "%")
            cursor.execute("SELECT key FROM kv_store WHERE key LIKE ?", (like_pattern,))

        return [row['key'] for row in cursor.fetchall()]

    def clear(self):
        """Очистить хранилище"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM kv_store")
        self.conn.commit()

    def cleanup_expired(self):
        """Очистка истёкших записей"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM kv_store
            WHERE expires_at IS NOT NULL
            AND expires_at < ?
        """, (datetime.now().isoformat(),))

        deleted = cursor.rowcount
        self.conn.commit()

        return deleted

    def log_query(self, query: str, method: str, results_count: int,
                  confidence: float, elapsed_ms: float):
        """Логирование запроса"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO query_history
            (query, method, results_count, confidence, elapsed_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (query, method, results_count, confidence, elapsed_ms,
              datetime.now().isoformat()))

        self.conn.commit()

    def get_query_history(self, limit: int = 100) -> List[Dict]:
        """Получить историю запросов"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM query_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def save_pattern(self, pattern_type: str, pattern_data: Any, confidence: float):
        """Сохранение выученного паттерна"""
        cursor = self.conn.cursor()

        pattern_blob = pickle.dumps(pattern_data)

        cursor.execute("""
            INSERT INTO learned_patterns
            (pattern_type, pattern_data, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (pattern_type, pattern_blob, confidence,
              datetime.now().isoformat(), datetime.now().isoformat()))

        self.conn.commit()

    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Dict]:
        """Получить выученные паттерны"""
        cursor = self.conn.cursor()

        if pattern_type:
            cursor.execute("""
                SELECT * FROM learned_patterns
                WHERE pattern_type = ?
                ORDER BY confidence DESC
            """, (pattern_type,))
        else:
            cursor.execute("""
                SELECT * FROM learned_patterns
                ORDER BY confidence DESC
            """)

        patterns = []
        for row in cursor.fetchall():
            pattern = dict(row)
            pattern['pattern_data'] = pickle.loads(pattern['pattern_data'])
            patterns.append(pattern)

        return patterns

    def get_statistics(self) -> Dict:
        """Получить статистику хранилища"""
        cursor = self.conn.cursor()

        # KV store stats
        cursor.execute("SELECT COUNT(*) as count FROM kv_store")
        kv_count = cursor.fetchone()['count']

        cursor.execute("""
            SELECT SUM(access_count) as total_accesses
            FROM kv_store
        """)
        total_accesses = cursor.fetchone()['total_accesses'] or 0

        # Query history stats
        cursor.execute("SELECT COUNT(*) as count FROM query_history")
        queries_count = cursor.fetchone()['count']

        cursor.execute("""
            SELECT AVG(confidence) as avg_confidence,
                   AVG(elapsed_ms) as avg_elapsed
            FROM query_history
        """)
        query_stats = cursor.fetchone()

        # Patterns stats
        cursor.execute("SELECT COUNT(*) as count FROM learned_patterns")
        patterns_count = cursor.fetchone()['count']

        return {
            "kv_store": {
                "total_keys": kv_count,
                "total_accesses": int(total_accesses)
            },
            "query_history": {
                "total_queries": queries_count,
                "avg_confidence": float(query_stats['avg_confidence'] or 0),
                "avg_elapsed_ms": float(query_stats['avg_elapsed'] or 0)
            },
            "learned_patterns": {
                "total_patterns": patterns_count
            }
        }

    def close(self):
        """Закрытие соединения"""
        self.conn.close()


class RedisBackend(StorageBackend):
    """
    Redis бэкенд для distributed систем

    Преимущества:
    - Очень быстрый (in-memory)
    - Distributed caching
    - Pub/Sub для real-time updates
    - TTL встроен
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis не установлен. pip install redis")

        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False  # Binary mode для pickle
        )

        # Проверка подключения
        try:
            self.client.ping()
        except redis.ConnectionError:
            raise RuntimeError(f"Не удалось подключиться к Redis на {host}:{port}")

    def get(self, key: str) -> Optional[Any]:
        """Получить значение"""
        value = self.client.get(key)

        if value is None:
            return None

        return pickle.loads(value)

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установить значение"""
        value_blob = pickle.dumps(value)

        if ttl:
            self.client.setex(key, ttl, value_blob)
        else:
            self.client.set(key, value_blob)

    def delete(self, key: str):
        """Удалить ключ"""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Проверка существования"""
        return bool(self.client.exists(key))

    def keys(self, pattern: str = "*") -> List[str]:
        """Получить список ключей"""
        keys = self.client.keys(pattern)
        return [k.decode() if isinstance(k, bytes) else k for k in keys]

    def clear(self):
        """Очистить хранилище"""
        self.client.flushdb()

    def close(self):
        """Закрытие соединения"""
        self.client.close()


class JSONBackend(StorageBackend):
    """
    JSON файлы бэкенд (простейший fallback)

    Преимущества:
    - Нет зависимостей
    - Читаемость (можно открыть в текстовом редакторе)
    - Простота отладки

    Недостатки:
    - Медленный
    - Не concurrent-safe
    - Ограниченные типы данных
    """

    def __init__(self, storage_dir: str = ".storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def _key_to_path(self, key: str) -> Path:
        """Преобразование ключа в путь к файлу"""
        # Хэш для избежания проблем с файловой системой
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.storage_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Получить значение"""
        path = self._key_to_path(key)

        if not path.exists():
            return None

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Проверка TTL
            if 'expires_at' in data and data['expires_at']:
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() > expires_at:
                    self.delete(key)
                    return None

            return data['value']

        except (json.JSONDecodeError, KeyError):
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установить значение"""
        path = self._key_to_path(key)

        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

        data = {
            "key": key,
            "value": value,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at
        }

        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def delete(self, key: str):
        """Удалить ключ"""
        path = self._key_to_path(key)
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        """Проверка существования"""
        return self._key_to_path(key).exists()

    def keys(self, pattern: str = "*") -> List[str]:
        """Получить список ключей"""
        keys = []

        for path in self.storage_dir.glob("*.json"):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if 'key' in data:
                        keys.append(data['key'])
            except:
                pass

        return keys

    def clear(self):
        """Очистить хранилище"""
        for path in self.storage_dir.glob("*.json"):
            path.unlink()


class PersistentStorage:
    """
    Главный класс персистентного хранилища

    Автоматически выбирает лучший доступный бэкенд
    """

    def __init__(self, backend: str = "auto", **kwargs):
        """
        Args:
            backend: "auto", "sqlite", "redis", или "json"
            **kwargs: Параметры для конкретного бэкенда
        """

        if backend == "auto":
            # Автовыбор
            if REDIS_AVAILABLE:
                try:
                    self.backend = RedisBackend(**kwargs)
                    print("✓ Используется Redis backend")
                except:
                    self.backend = SQLiteBackend(**kwargs)
                    print("✓ Используется SQLite backend")
            else:
                self.backend = SQLiteBackend(**kwargs)
                print("✓ Используется SQLite backend")

        elif backend == "sqlite":
            self.backend = SQLiteBackend(**kwargs)
            print("✓ Используется SQLite backend")

        elif backend == "redis":
            self.backend = RedisBackend(**kwargs)
            print("✓ Используется Redis backend")

        elif backend == "json":
            self.backend = JSONBackend(**kwargs)
            print("✓ Используется JSON backend")

        else:
            raise ValueError(f"Неизвестный backend: {backend}")

    def get(self, key: str) -> Optional[Any]:
        """Получить значение"""
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установить значение"""
        self.backend.set(key, value, ttl)

    def delete(self, key: str):
        """Удалить ключ"""
        self.backend.delete(key)

    def exists(self, key: str) -> bool:
        """Проверка существования"""
        return self.backend.exists(key)

    def keys(self, pattern: str = "*") -> List[str]:
        """Получить список ключей"""
        return self.backend.keys(pattern)

    def clear(self):
        """Очистить хранилище"""
        self.backend.clear()

    # Дополнительные методы (если бэкенд поддерживает)
    def log_query(self, *args, **kwargs):
        """Логирование запроса (только для SQLite)"""
        if isinstance(self.backend, SQLiteBackend):
            return self.backend.log_query(*args, **kwargs)

    def get_query_history(self, *args, **kwargs):
        """История запросов (только для SQLite)"""
        if isinstance(self.backend, SQLiteBackend):
            return self.backend.get_query_history(*args, **kwargs)
        return []

    def save_pattern(self, *args, **kwargs):
        """Сохранение паттерна (только для SQLite)"""
        if isinstance(self.backend, SQLiteBackend):
            return self.backend.save_pattern(*args, **kwargs)

    def get_patterns(self, *args, **kwargs):
        """Получить паттерны (только для SQLite)"""
        if isinstance(self.backend, SQLiteBackend):
            return self.backend.get_patterns(*args, **kwargs)
        return []

    def get_statistics(self):
        """Статистика"""
        if isinstance(self.backend, SQLiteBackend):
            return self.backend.get_statistics()
        return {}

    def cleanup_expired(self):
        """Очистка истёкших записей (только для SQLite)"""
        if isinstance(self.backend, SQLiteBackend):
            return self.backend.cleanup_expired()
        return 0

    def close(self):
        """Закрытие соединения"""
        self.backend.close()


# ═══════════════════════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ДЕМОНСТРАЦИЯ ПЕРСИСТЕНТНОГО ХРАНИЛИЩА")
    print("="*80 + "\n")

    # Тест SQLite
    print("─"*80)
    print("  ТЕСТ 1: SQLite Backend")
    print("─"*80)

    storage = PersistentStorage(backend="sqlite", db_path="test_storage.db")

    # Set/Get
    storage.set("user:123", {"name": "Alice", "role": "admin"})
    user = storage.get("user:123")
    print(f"Получено: {user}")

    # TTL
    storage.set("temp:data", {"value": 42}, ttl=5)
    print(f"Temp data (TTL=5s): {storage.get('temp:data')}")

    # Логирование запроса
    storage.log_query(
        query="как работает 5G?",
        method="semantic",
        results_count=5,
        confidence=0.85,
        elapsed_ms=45.2
    )

    # Сохранение паттерна
    storage.save_pattern(
        pattern_type="frequent_query",
        pattern_data={"query_template": "как работает {technology}?"},
        confidence=0.9
    )

    # История
    history = storage.get_query_history(limit=5)
    print(f"\nИстория запросов: {len(history)} записей")
    if history:
        print(f"Последний: {history[0]['query']}")

    # Паттерны
    patterns = storage.get_patterns()
    print(f"Паттернов: {len(patterns)}")

    # Статистика
    stats = storage.get_statistics()
    print(f"\nСтатистика:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Очистка
    expired = storage.cleanup_expired()
    print(f"\nУдалено истёкших записей: {expired}")

    storage.close()

    # Тест JSON
    print("\n" + "─"*80)
    print("  ТЕСТ 2: JSON Backend")
    print("─"*80)

    json_storage = PersistentStorage(backend="json", storage_dir=".test_storage")

    json_storage.set("config", {"theme": "dark", "language": "ru"})
    config = json_storage.get("config")
    print(f"Config: {config}")

    # Список ключей
    all_keys = json_storage.keys()
    print(f"Всего ключей: {len(all_keys)}")

    json_storage.clear()

    print("\n✓ Демонстрация завершена!")
