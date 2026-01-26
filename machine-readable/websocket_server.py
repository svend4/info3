#!/usr/bin/env python3
"""
WEBSOCKET SERVER ДЛЯ REAL-TIME ОБНОВЛЕНИЙ
=========================================

Потоковая обработка запросов через WebSocket:
- Real-time поиск с прогрессом
- Потоковая отправка результатов
- Bidirectional communication
- Broadcast updates
- Connection management

ИСПОЛЬЗОВАНИЕ:
    uvicorn websocket_server:app --host 0.0.0.0 --port 8001

CLIENT EXAMPLE:
    const ws = new WebSocket('ws://localhost:8001/ws');
    ws.send(JSON.stringify({type: 'query', data: 'AI'}));
    ws.onmessage = (event) => console.log(event.data);
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import asyncio
import json
import time
from datetime import datetime
from collections import defaultdict
import logging

# Локальные импорты
try:
    from semantic_search_agent import SemanticSearchAgent
    from persistent_storage import PersistentStorage
except ImportError:
    print("⚠ Локальные модули не найдены")
    SemanticSearchAgent = None
    PersistentStorage = None

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="WebSocket Real-Time API",
    description="Real-time поиск через WebSocket",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# CONNECTION MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ConnectionManager:
    """Управление WebSocket соединениями"""

    def __init__(self):
        # Активные соединения: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Подписки на топики: topic -> [client_ids]
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)

        # Статистика
        self.stats = {
            "total_connections": 0,
            "total_messages": 0,
            "total_broadcasts": 0
        }

    async def connect(self, websocket: WebSocket, client_id: str):
        """Подключение клиента"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.stats["total_connections"] += 1

        logger.info(f"Client connected: {client_id}")
        logger.info(f"Active connections: {len(self.active_connections)}")

        # Приветственное сообщение
        await self.send_personal_message({
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Welcome to WebSocket API"
        }, client_id)

    def disconnect(self, client_id: str):
        """Отключение клиента"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Удаление из подписок
        for topic in self.subscriptions:
            if client_id in self.subscriptions[topic]:
                self.subscriptions[topic].remove(client_id)

        logger.info(f"Client disconnected: {client_id}")
        logger.info(f"Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, client_id: str):
        """Отправка сообщения конкретному клиенту"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
            self.stats["total_messages"] += 1

    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        """Broadcast сообщение всем клиентам"""
        for client_id, websocket in self.active_connections.items():
            if client_id != exclude:
                try:
                    await websocket.send_json(message)
                except:
                    logger.error(f"Failed to send to {client_id}")

        self.stats["total_broadcasts"] += 1

    async def send_to_topic(self, message: dict, topic: str):
        """Отправка сообщения подписчикам топика"""
        subscribers = self.subscriptions.get(topic, [])

        for client_id in subscribers:
            await self.send_personal_message(message, client_id)

    def subscribe(self, client_id: str, topic: str):
        """Подписка на топик"""
        if client_id not in self.subscriptions[topic]:
            self.subscriptions[topic].append(client_id)

        logger.info(f"Client {client_id} subscribed to {topic}")

    def unsubscribe(self, client_id: str, topic: str):
        """Отписка от топика"""
        if client_id in self.subscriptions[topic]:
            self.subscriptions[topic].remove(client_id)

        logger.info(f"Client {client_id} unsubscribed from {topic}")

    def get_stats(self) -> dict:
        """Получение статистики"""
        return {
            **self.stats,
            "active_connections": len(self.active_connections),
            "topics": {
                topic: len(subscribers)
                for topic, subscribers in self.subscriptions.items()
            }
        }


manager = ConnectionManager()

# ═══════════════════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЕ ЗАВИСИМОСТИ
# ═══════════════════════════════════════════════════════════════════════════

search_agent = None
if SemanticSearchAgent:
    try:
        search_agent = SemanticSearchAgent(knowledge_base_path="афоризмы")
        logger.info("Search agent initialized")
    except Exception as e:
        logger.error(f"Failed to initialize search agent: {e}")

storage = None
if PersistentStorage:
    try:
        storage = PersistentStorage(backend="sqlite", db_path="websocket.db")
        logger.info("Storage initialized")
    except Exception as e:
        logger.error(f"Failed to initialize storage: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# MESSAGE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

async def handle_query(client_id: str, data: dict):
    """Обработка запроса поиска"""

    query = data.get("query")
    method = data.get("method", "hybrid")
    top_k = data.get("top_k", 5)

    if not query:
        await manager.send_personal_message({
            "type": "error",
            "error": "Query is required"
        }, client_id)
        return

    if not search_agent:
        await manager.send_personal_message({
            "type": "error",
            "error": "Search agent not available"
        }, client_id)
        return

    try:
        # Отправка прогресса
        await manager.send_personal_message({
            "type": "progress",
            "stage": "started",
            "message": "Поиск начат..."
        }, client_id)

        # Выполнение поиска
        result = search_agent.query(
            query=query,
            method=method,
            top_k=top_k
        )

        # Потоковая отправка результатов
        await manager.send_personal_message({
            "type": "progress",
            "stage": "processing",
            "message": f"Найдено {result['count']} результатов"
        }, client_id)

        # Отправка результатов по одному (streaming)
        for i, res in enumerate(result['results']):
            await manager.send_personal_message({
                "type": "result_chunk",
                "index": i,
                "total": result['count'],
                "data": res
            }, client_id)

            # Небольшая задержка для демонстрации streaming
            await asyncio.sleep(0.1)

        # Финальное сообщение
        await manager.send_personal_message({
            "type": "query_complete",
            "query": query,
            "method": method,
            "count": result['count'],
            "elapsed_ms": result['elapsed_ms']
        }, client_id)

        # Логирование
        if storage:
            storage.log_query(
                query=query,
                method=method,
                results_count=result['count'],
                confidence=result.get('confidence', 0.0),
                elapsed_ms=result['elapsed_ms']
            )

    except Exception as e:
        logger.error(f"Query error: {e}")
        await manager.send_personal_message({
            "type": "error",
            "error": str(e)
        }, client_id)

async def handle_subscribe(client_id: str, data: dict):
    """Подписка на топик"""
    topic = data.get("topic")

    if not topic:
        await manager.send_personal_message({
            "type": "error",
            "error": "Topic is required"
        }, client_id)
        return

    manager.subscribe(client_id, topic)

    await manager.send_personal_message({
        "type": "subscribed",
        "topic": topic
    }, client_id)

async def handle_unsubscribe(client_id: str, data: dict):
    """Отписка от топика"""
    topic = data.get("topic")

    if not topic:
        await manager.send_personal_message({
            "type": "error",
            "error": "Topic is required"
        }, client_id)
        return

    manager.unsubscribe(client_id, topic)

    await manager.send_personal_message({
        "type": "unsubscribed",
        "topic": topic
    }, client_id)

async def handle_broadcast(client_id: str, data: dict):
    """Broadcast сообщение"""
    message = data.get("message")

    if not message:
        await manager.send_personal_message({
            "type": "error",
            "error": "Message is required"
        }, client_id)
        return

    await manager.broadcast({
        "type": "broadcast",
        "from": client_id,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }, exclude=client_id)

async def handle_stats(client_id: str, data: dict):
    """Получение статистики"""
    stats = manager.get_stats()

    if search_agent:
        stats["search_agent"] = search_agent.get_statistics()

    if storage:
        stats["storage"] = storage.get_statistics()

    await manager.send_personal_message({
        "type": "stats",
        "data": stats
    }, client_id)

# Маппинг типов сообщений на обработчики
message_handlers = {
    "query": handle_query,
    "subscribe": handle_subscribe,
    "unsubscribe": handle_unsubscribe,
    "broadcast": handle_broadcast,
    "stats": handle_stats
}

# ═══════════════════════════════════════════════════════════════════════════
# WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(default=None)
):
    """
    Главный WebSocket endpoint

    URL: ws://localhost:8001/ws?client_id=my_client_id

    MESSAGE FORMAT:
    {
        "type": "query|subscribe|unsubscribe|broadcast|stats",
        "data": {...}
    }
    """

    # Генерация client_id если не предоставлен
    if not client_id:
        client_id = f"client_{int(time.time() * 1000)}"

    await manager.connect(websocket, client_id)

    try:
        while True:
            # Получение сообщения от клиента
            raw_message = await websocket.receive_text()

            try:
                message = json.loads(raw_message)
                message_type = message.get("type")
                data = message.get("data", {})

                logger.info(f"Message from {client_id}: {message_type}")

                # Обработка сообщения
                if message_type in message_handlers:
                    handler = message_handlers[message_type]
                    await handler(client_id, data)
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "error": f"Unknown message type: {message_type}"
                    }, client_id)

            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "error": "Invalid JSON"
                }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)

    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

# ═══════════════════════════════════════════════════════════════════════════
# HTTP ENDPOINTS (для управления)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "WebSocket Real-Time API",
        "version": "1.0.0",
        "websocket": "ws://localhost:8001/ws?client_id=YOUR_ID",
        "stats": "/stats"
    }

@app.get("/stats")
async def get_stats():
    """Получение статистики через HTTP"""
    stats = manager.get_stats()

    if search_agent:
        stats["search_agent"] = search_agent.get_statistics()

    if storage:
        stats["storage"] = storage.get_statistics()

    return stats

@app.post("/broadcast")
async def http_broadcast(message: dict):
    """HTTP endpoint для broadcast сообщений"""
    await manager.broadcast({
        "type": "broadcast",
        "from": "system",
        "message": message.get("message"),
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "broadcasted"}

# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════════════════════

async def periodic_broadcast():
    """Периодический broadcast (например, обновления системы)"""
    while True:
        await asyncio.sleep(60)  # Каждую минуту

        if manager.active_connections:
            await manager.broadcast({
                "type": "system_update",
                "timestamp": datetime.utcnow().isoformat(),
                "active_connections": len(manager.active_connections)
            })

@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач"""
    logger.info("WebSocket server started")

    # Запуск periodic broadcast (опционально)
    # asyncio.create_task(periodic_broadcast())

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие при остановке"""
    logger.info("WebSocket server shutting down")

    if storage:
        storage.close()

# ═══════════════════════════════════════════════════════════════════════════
# HTML CLIENT (для тестирования)
# ═══════════════════════════════════════════════════════════════════════════

HTML_CLIENT = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test Client</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        #messages { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; margin-bottom: 10px; }
        .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
        .connected { background: #d4edda; }
        .result { background: #d1ecf1; }
        .error { background: #f8d7da; }
        .progress { background: #fff3cd; }
        input, select, button { margin: 5px; padding: 8px; }
    </style>
</head>
<body>
    <h1>WebSocket Test Client</h1>

    <div>
        <input type="text" id="clientId" placeholder="Client ID" value="test_client">
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
        <span id="status">Disconnected</span>
    </div>

    <div id="messages"></div>

    <div>
        <input type="text" id="query" placeholder="Search query..." style="width: 300px;">
        <select id="method">
            <option value="hybrid">Hybrid</option>
            <option value="semantic">Semantic</option>
            <option value="keyword">Keyword</option>
        </select>
        <button onclick="sendQuery()">Search</button>
    </div>

    <div>
        <button onclick="getStats()">Get Stats</button>
        <button onclick="clearMessages()">Clear</button>
    </div>

    <script>
        let ws = null;
        const messagesDiv = document.getElementById('messages');

        function connect() {
            const clientId = document.getElementById('clientId').value;
            ws = new WebSocket(`ws://localhost:8001/ws?client_id=${clientId}`);

            ws.onopen = () => {
                document.getElementById('status').textContent = 'Connected';
                addMessage('connected', 'Connected to server');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('Received:', data);

                if (data.type === 'connected') {
                    addMessage('connected', `Welcome! Client ID: ${data.client_id}`);
                } else if (data.type === 'progress') {
                    addMessage('progress', `Progress: ${data.message}`);
                } else if (data.type === 'result_chunk') {
                    addMessage('result', `Result ${data.index + 1}/${data.total}: ${data.data.topic}`);
                } else if (data.type === 'query_complete') {
                    addMessage('result', `Query complete: ${data.count} results in ${data.elapsed_ms.toFixed(2)}ms`);
                } else if (data.type === 'error') {
                    addMessage('error', `Error: ${data.error}`);
                } else if (data.type === 'stats') {
                    addMessage('result', `Stats: ${JSON.stringify(data.data, null, 2)}`);
                } else {
                    addMessage('result', JSON.stringify(data, null, 2));
                }
            };

            ws.onclose = () => {
                document.getElementById('status').textContent = 'Disconnected';
                addMessage('error', 'Disconnected from server');
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                addMessage('error', 'WebSocket error');
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function sendQuery() {
            if (!ws) {
                alert('Not connected!');
                return;
            }

            const query = document.getElementById('query').value;
            const method = document.getElementById('method').value;

            ws.send(JSON.stringify({
                type: 'query',
                data: {
                    query: query,
                    method: method,
                    top_k: 5
                }
            }));

            addMessage('progress', `Sent query: ${query} (${method})`);
        }

        function getStats() {
            if (!ws) {
                alert('Not connected!');
                return;
            }

            ws.send(JSON.stringify({
                type: 'stats',
                data: {}
            }));
        }

        function addMessage(type, text) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function clearMessages() {
            messagesDiv.innerHTML = '';
        }
    </script>
</body>
</html>
"""

@app.get("/test", response_class=type("HTMLResponse", (), {"media_type": "text/html"}))
async def test_client():
    """HTML клиент для тестирования"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=HTML_CLIENT)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("  ЗАПУСК WEBSOCKET SERVER")
    print("="*80)
    print(f"\n  WebSocket: ws://localhost:8001/ws")
    print(f"  Test Client: http://localhost:8001/test")
    print(f"  Stats: http://localhost:8001/stats")
    print("="*80 + "\n")

    uvicorn.run(
        "websocket_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
