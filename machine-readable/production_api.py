#!/usr/bin/env python3
"""
PRODUCTION-READY REST API ДЛЯ RAG СИСТЕМЫ
==========================================

Полнофункциональный API с:
- JWT аутентификацией
- Rate limiting
- CORS поддержкой
- Prometheus метриками
- Health checks
- Request/Response validation
- Structured logging
- Error handling
- OpenAPI документацией

ИСПОЛЬЗОВАНИЕ:
    uvicorn production_api:app --host 0.0.0.0 --port 8000 --reload

ENDPOINTS:
    POST   /auth/register      - Регистрация пользователя
    POST   /auth/login         - Получение JWT token
    POST   /query              - Поиск (требует auth)
    GET    /health             - Health check
    GET    /metrics            - Prometheus метрики
    GET    /docs               - OpenAPI документация
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import time
import hashlib
import secrets
import jwt
import logging
from pathlib import Path

# Rate limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    print("⚠ slowapi не установлен. Rate limiting отключен.")
    print("  Установите: pip install slowapi")

# Prometheus
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("⚠ prometheus_client не установлен. Метрики отключены.")
    print("  Установите: pip install prometheus-client")

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

class Settings:
    """Настройки приложения"""

    # JWT
    SECRET_KEY = secrets.token_urlsafe(32)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000

    # CORS
    CORS_ORIGINS = ["*"]  # В production указать конкретные домены

    # Storage
    STORAGE_BACKEND = "sqlite"
    STORAGE_DB_PATH = "production.db"

    # Knowledge base
    KNOWLEDGE_BASE_PATH = "афоризмы"

    # Logging
    LOG_LEVEL = "INFO"

settings = Settings()

# ═══════════════════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# PROMETHEUS МЕТРИКИ
# ═══════════════════════════════════════════════════════════════════════════

if PROMETHEUS_AVAILABLE:
    # Счётчики запросов
    requests_total = Counter(
        'api_requests_total',
        'Total API requests',
        ['method', 'endpoint', 'status']
    )

    # Время обработки
    request_duration = Histogram(
        'api_request_duration_seconds',
        'Request duration in seconds',
        ['method', 'endpoint']
    )

    # Активные пользователи
    active_users = Gauge(
        'api_active_users',
        'Number of active users'
    )

    # Запросы к базе знаний
    knowledge_queries = Counter(
        'knowledge_queries_total',
        'Total knowledge base queries',
        ['method']
    )

    # Cache hits
    cache_hits = Counter(
        'cache_hits_total',
        'Total cache hits'
    )

    cache_misses = Counter(
        'cache_misses_total',
        'Total cache misses'
    )

# ═══════════════════════════════════════════════════════════════════════════
# PYDANTIC МОДЕЛИ
# ═══════════════════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    """Модель регистрации пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username должен содержать только буквы и цифры')
        return v

class UserLogin(BaseModel):
    """Модель входа"""
    username: str
    password: str

class Token(BaseModel):
    """JWT токен"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class QueryRequest(BaseModel):
    """Запрос поиска"""
    query: str = Field(..., min_length=1, max_length=500)
    method: str = Field("hybrid", regex="^(semantic|keyword|hybrid)$")
    top_k: int = Field(5, ge=1, le=50)
    semantic_weight: float = Field(0.7, ge=0.0, le=1.0)
    keyword_weight: float = Field(0.3, ge=0.0, le=1.0)

class QueryResponse(BaseModel):
    """Ответ поиска"""
    query: str
    method: str
    results: List[Dict[str, Any]]
    count: int
    elapsed_ms: float
    from_cache: bool = False

class HealthResponse(BaseModel):
    """Health check ответ"""
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    error: str
    detail: Optional[str] = None
    timestamp: str

# ═══════════════════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ FASTAPI
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="RAG Knowledge Base API",
    description="Production-ready API для 4-уровневой базы знаний",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ═══════════════════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЕ ЗАВИСИМОСТИ
# ═══════════════════════════════════════════════════════════════════════════

# Storage для пользователей и токенов
user_storage = None
if PersistentStorage:
    user_storage = PersistentStorage(
        backend=settings.STORAGE_BACKEND,
        db_path=settings.STORAGE_DB_PATH
    )

# Semantic search agent
search_agent = None
if SemanticSearchAgent:
    search_agent = SemanticSearchAgent(
        knowledge_base_path=settings.KNOWLEDGE_BASE_PATH
    )

# In-memory хранилища (для примера)
users_db = {}  # username -> {password_hash, email, created_at}
active_tokens = set()  # Активные токены

# Security
security = HTTPBearer()

# ═══════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех запросов"""
    start_time = time.time()

    # Обработка запроса
    response = await call_next(request)

    # Вычисление времени
    elapsed = time.time() - start_time

    # Логирование
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {elapsed*1000:.2f}ms"
    )

    # Prometheus метрики
    if PROMETHEUS_AVAILABLE:
        requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(elapsed)

    return response

# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """Хэширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    return hash_password(password) == hashed

def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Проверка и декодирование токена"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            return None

        return username

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency для получения текущего пользователя"""
    token = credentials.credentials

    if token not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token"
        )

    username = verify_token(token)

    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return username

# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "RAG Knowledge Base API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ─────────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=Token, tags=["Auth"])
async def register(user: UserRegister):
    """Регистрация нового пользователя"""

    # Проверка существования
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Сохранение пользователя
    users_db[user.username] = {
        "password_hash": hash_password(user.password),
        "email": user.email,
        "created_at": datetime.utcnow().isoformat()
    }

    # Создание токена
    access_token = create_access_token(data={"sub": user.username})
    active_tokens.add(access_token)

    logger.info(f"New user registered: {user.username}")

    if PROMETHEUS_AVAILABLE:
        active_users.inc()

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(user: UserLogin):
    """Вход и получение JWT токена"""

    # Проверка пользователя
    if user.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    user_data = users_db[user.username]

    # Проверка пароля
    if not verify_password(user.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Создание токена
    access_token = create_access_token(data={"sub": user.username})
    active_tokens.add(access_token)

    logger.info(f"User logged in: {user.username}")

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/logout", tags=["Auth"])
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Выход (инвалидация токена)"""
    token = credentials.credentials

    if token in active_tokens:
        active_tokens.remove(token)

    return {"message": "Successfully logged out"}

# ─────────────────────────────────────────────────────────────────────────
# QUERY
# ─────────────────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_knowledge_base(
    request: QueryRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Поиск в базе знаний

    Требует JWT аутентификации
    """

    if not search_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search agent not available"
        )

    # Проверка кэша
    cache_key = f"query:{hash_password(request.query)}:{request.method}"
    cached_result = None

    if user_storage:
        cached_result = user_storage.get(cache_key)

    if cached_result:
        logger.info(f"Cache hit for query: {request.query}")

        if PROMETHEUS_AVAILABLE:
            cache_hits.inc()

        return QueryResponse(
            from_cache=True,
            **cached_result
        )

    # Кэш промах
    if PROMETHEUS_AVAILABLE:
        cache_misses.inc()
        knowledge_queries.labels(method=request.method).inc()

    # Выполнение запроса
    try:
        result = search_agent.query(
            query=request.query,
            method=request.method,
            top_k=request.top_k,
            semantic_weight=request.semantic_weight,
            keyword_weight=request.keyword_weight
        )

        # Сохранение в кэш
        if user_storage:
            user_storage.set(cache_key, result, ttl=3600)  # 1 час

            # Логирование в историю
            user_storage.log_query(
                query=request.query,
                method=request.method,
                results_count=result['count'],
                confidence=result.get('confidence', 0.0),
                elapsed_ms=result['elapsed_ms']
            )

        logger.info(
            f"Query executed: {request.query} "
            f"({request.method}, {result['count']} results)"
        )

        return QueryResponse(**result, from_cache=False)

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Rate limited version
if SLOWAPI_AVAILABLE:
    @app.post("/query/limited", response_model=QueryResponse, tags=["Query"])
    @limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
    async def query_limited(
        request: Request,
        query_request: QueryRequest,
        current_user: str = Depends(get_current_user)
    ):
        """Поиск с rate limiting"""
        return await query_knowledge_base(query_request, current_user)

# ─────────────────────────────────────────────────────────────────────────
# HEALTH & METRICS
# ─────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""

    components = {
        "api": "healthy",
        "storage": "healthy" if user_storage else "unavailable",
        "search_agent": "healthy" if search_agent else "unavailable"
    }

    # Проверка компонентов
    overall_status = "healthy"

    if not search_agent:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        components=components
    )

@app.get("/health/detailed", tags=["Health"])
async def detailed_health():
    """Детальный health check"""

    details = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
        "components": {
            "api": "ok",
            "storage": {
                "status": "ok" if user_storage else "unavailable",
                "backend": type(user_storage.backend).__name__ if user_storage else None
            },
            "search_agent": {
                "status": "ok" if search_agent else "unavailable",
                "documents": len(search_agent.documents) if search_agent else 0
            }
        },
        "metrics": {}
    }

    # Добавление метрик
    if user_storage:
        try:
            stats = user_storage.get_statistics()
            details["metrics"]["storage"] = stats
        except:
            pass

    if search_agent:
        try:
            stats = search_agent.get_statistics()
            details["metrics"]["search"] = stats
        except:
            pass

    return details

@app.get("/metrics", tags=["Metrics"])
async def metrics():
    """Prometheus метрики"""

    if not PROMETHEUS_AVAILABLE:
        return PlainTextResponse("Prometheus not available")

    return PlainTextResponse(
        generate_latest(),
        media_type="text/plain"
    )

# ─────────────────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────────────────

@app.get("/admin/stats", tags=["Admin"])
async def get_stats(current_user: str = Depends(get_current_user)):
    """Получение статистики (требует auth)"""

    stats = {
        "users": {
            "total": len(users_db),
            "active_tokens": len(active_tokens)
        },
        "api": {
            "total_requests": "see /metrics"
        }
    }

    if user_storage:
        stats["storage"] = user_storage.get_statistics()

    if search_agent:
        stats["search"] = search_agent.get_statistics()

    return stats

@app.post("/admin/cache/clear", tags=["Admin"])
async def clear_cache(current_user: str = Depends(get_current_user)):
    """Очистка кэша (требует auth)"""

    if user_storage:
        # Очистка только кэша запросов
        keys = user_storage.keys("query:*")
        for key in keys:
            user_storage.delete(key)

        return {"message": f"Cleared {len(keys)} cache entries"}

    return {"message": "Storage not available"}

# ═══════════════════════════════════════════════════════════════════════════
# STARTUP/SHUTDOWN
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    app.state.start_time = time.time()
    logger.info("API started")

    # Создание тестового пользователя
    if "demo" not in users_db:
        users_db["demo"] = {
            "password_hash": hash_password("demo1234"),
            "email": "demo@example.com",
            "created_at": datetime.utcnow().isoformat()
        }
        logger.info("Demo user created: demo / demo1234")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.info("API shutting down")

    if user_storage:
        user_storage.close()

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("  ЗАПУСК PRODUCTION API")
    print("="*80)
    print(f"\n  URL: http://localhost:8000")
    print(f"  Docs: http://localhost:8000/docs")
    print(f"  Health: http://localhost:8000/health")
    print(f"  Metrics: http://localhost:8000/metrics")
    print(f"\n  Demo user: demo / demo1234")
    print("="*80 + "\n")

    uvicorn.run(
        "production_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
