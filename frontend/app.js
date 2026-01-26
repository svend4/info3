// ============================================================================
// RAG KNOWLEDGE BASE DASHBOARD - React Application
// ============================================================================
// Production-ready dashboard for semantic search with real-time updates
// Features: JWT auth, WebSocket streaming, metrics visualization, history
// ============================================================================

const { useState, useEffect, useRef, useCallback } = React;

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8001/ws',
    DEFAULT_TOP_K: 5,
    DEFAULT_METHOD: 'hybrid',
    DEBOUNCE_MS: 300,
    CHART_UPDATE_INTERVAL: 5000,
};

// ============================================================================
// API SERVICE
// ============================================================================

class APIService {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.token = localStorage.getItem('access_token');
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    async register(username, password) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        this.token = data.access_token;
        localStorage.setItem('access_token', this.token);
        localStorage.setItem('username', username);
        return data;
    }

    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        this.token = data.access_token;
        localStorage.setItem('access_token', this.token);
        localStorage.setItem('username', username);
        return data;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('username');
    }

    async query(query, method = 'hybrid', top_k = 5) {
        return this.request('/query', {
            method: 'POST',
            body: JSON.stringify({ query, method, top_k }),
        });
    }

    async getStats() {
        return this.request('/admin/stats');
    }

    async getHealth() {
        return this.request('/health/detailed');
    }

    isAuthenticated() {
        return !!this.token;
    }

    getUsername() {
        return localStorage.getItem('username') || 'Guest';
    }
}

// ============================================================================
// WEBSOCKET SERVICE
// ============================================================================

class WebSocketService {
    constructor(onMessage, onConnect, onDisconnect) {
        this.ws = null;
        this.onMessage = onMessage;
        this.onConnect = onConnect;
        this.onDisconnect = onDisconnect;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    connect() {
        if (this.ws?.readyState === WebSocket.OPEN) return;

        this.ws = new WebSocket(`${CONFIG.WS_URL}?client_id=${this.clientId}`);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.onConnect?.();
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.onMessage?.(message);
            } catch (error) {
                console.error('WebSocket message parse error:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.onDisconnect?.();
            this.attemptReconnect();
        };
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
            setTimeout(() => this.connect(), delay);
        }
    }

    send(type, data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, data }));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    query(query, method = 'hybrid', top_k = 5) {
        this.send('query', { query, method, top_k });
    }

    subscribe(topic) {
        this.send('subscribe', { topic });
    }

    disconnect() {
        this.ws?.close();
    }
}

// ============================================================================
// AUTHENTICATION COMPONENT
// ============================================================================

function AuthForm({ apiService, onAuthSuccess }) {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                await apiService.login(username, password);
            } else {
                await apiService.register(username, password);
            }
            onAuthSuccess();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center gradient-bg">
            <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md">
                <h2 className="text-3xl font-bold text-center mb-6 text-gray-800">
                    {isLogin ? 'Вход' : 'Регистрация'}
                </h2>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-700 mb-2">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-gray-700 mb-2">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                    >
                        {loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
                    </button>
                </form>

                <div className="mt-4 text-center">
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        className="text-purple-600 hover:underline"
                    >
                        {isLogin ? 'Нет аккаунта? Зарегистрируйтесь' : 'Уже есть аккаунт? Войдите'}
                    </button>
                </div>
            </div>
        </div>
    );
}

// ============================================================================
// SEARCH BAR COMPONENT
// ============================================================================

function SearchBar({ onSearch, loading }) {
    const [query, setQuery] = useState('');
    const [method, setMethod] = useState(CONFIG.DEFAULT_METHOD);
    const [topK, setTopK] = useState(CONFIG.DEFAULT_TOP_K);
    const [suggestions, setSuggestions] = useState([]);

    const popularQueries = [
        'AI and neural networks',
        'blockchain technology',
        'quantum computing',
        'machine learning',
        'cybersecurity',
        'cloud computing',
        'IoT devices',
        '5G networks',
    ];

    const handleQueryChange = (value) => {
        setQuery(value);
        if (value.length > 2) {
            const filtered = popularQueries.filter(q =>
                q.toLowerCase().includes(value.toLowerCase())
            );
            setSuggestions(filtered);
        } else {
            setSuggestions([]);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query, method, topK);
            setSuggestions([]);
        }
    };

    const selectSuggestion = (suggestion) => {
        setQuery(suggestion);
        setSuggestions([]);
        onSearch(suggestion, method, topK);
    };

    return (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <form onSubmit={handleSubmit}>
                <div className="relative mb-4">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => handleQueryChange(e.target.value)}
                        placeholder="Поиск в базе знаний..."
                        className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                        disabled={loading}
                    />

                    {suggestions.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                            {suggestions.map((suggestion, idx) => (
                                <div
                                    key={idx}
                                    onClick={() => selectSuggestion(suggestion)}
                                    className="px-4 py-2 hover:bg-purple-50 cursor-pointer"
                                >
                                    {suggestion}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-gray-700 mb-2">Метод поиска</label>
                        <select
                            value={method}
                            onChange={(e) => setMethod(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                            disabled={loading}
                        >
                            <option value="semantic">Семантический</option>
                            <option value="keyword">Ключевые слова</option>
                            <option value="hybrid">Гибридный (70/30)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-gray-700 mb-2">Результатов: {topK}</label>
                        <input
                            type="range"
                            min="1"
                            max="20"
                            value={topK}
                            onChange={(e) => setTopK(parseInt(e.target.value))}
                            className="w-full"
                            disabled={loading}
                        />
                    </div>

                    <div className="flex items-end">
                        <button
                            type="submit"
                            disabled={loading || !query.trim()}
                            className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Поиск...' : 'Найти'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}

// ============================================================================
// RESULT CARD COMPONENT
// ============================================================================

function ResultCard({ result, index }) {
    const [expanded, setExpanded] = useState(false);

    const getConfidenceColor = (score) => {
        if (score >= 0.8) return 'text-green-600';
        if (score >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getConfidenceBadge = (score) => {
        if (score >= 0.8) return 'bg-green-100 text-green-800';
        if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
        return 'bg-red-100 text-red-800';
    };

    return (
        <div className="bg-white rounded-lg shadow card-shadow hover:card-shadow-hover transition-all duration-300 p-5 mb-4">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center w-10 h-10 bg-purple-100 text-purple-600 rounded-full font-bold">
                        {index + 1}
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800">{result.topic || 'Результат'}</h3>
                        <p className="text-sm text-gray-500">Документ ID: {result.doc_id || index}</p>
                    </div>
                </div>

                <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getConfidenceBadge(result.score)}`}>
                    {(result.score * 100).toFixed(1)}%
                </div>
            </div>

            <div className="mb-3">
                <p className={`text-gray-700 ${expanded ? '' : 'line-clamp-3'}`}>
                    {result.text || result.content || 'Нет содержимого'}
                </p>
            </div>

            {result.metadata && (
                <div className="mb-3 bg-gray-50 rounded p-3">
                    <p className="text-xs text-gray-600 font-mono">
                        {JSON.stringify(result.metadata, null, 2)}
                    </p>
                </div>
            )}

            <div className="flex items-center justify-between text-sm text-gray-600">
                <div className="flex space-x-4">
                    <span className={`font-semibold ${getConfidenceColor(result.score)}`}>
                        Релевантность: {(result.score * 100).toFixed(1)}%
                    </span>
                    {result.method && (
                        <span className="text-gray-500">Метод: {result.method}</span>
                    )}
                </div>

                <button
                    onClick={() => setExpanded(!expanded)}
                    className="text-purple-600 hover:underline"
                >
                    {expanded ? 'Свернуть' : 'Развернуть'}
                </button>
            </div>
        </div>
    );
}

// ============================================================================
// RESULTS LIST COMPONENT
// ============================================================================

function ResultsList({ results, loading, error, streamingProgress }) {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-8">
                <div className="flex flex-col items-center justify-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mb-4"></div>
                    <p className="text-gray-600 text-lg">Поиск...</p>
                    {streamingProgress && (
                        <p className="text-gray-500 text-sm mt-2">{streamingProgress}</p>
                    )}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-300 rounded-lg p-6">
                <h3 className="text-red-800 font-semibold mb-2">Ошибка</h3>
                <p className="text-red-600">{error}</p>
            </div>
        );
    }

    if (!results || results.length === 0) {
        return (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
                <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <p className="text-gray-600 text-lg">Нет результатов</p>
                <p className="text-gray-500 text-sm mt-2">Попробуйте изменить запрос или метод поиска</p>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-800">
                    Найдено результатов: {results.length}
                </h2>
            </div>

            {results.map((result, index) => (
                <ResultCard key={index} result={result} index={index} />
            ))}
        </div>
    );
}

// ============================================================================
// METRICS PANEL COMPONENT
// ============================================================================

function MetricsPanel({ stats }) {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !stats) return;

        const ctx = chartRef.current.getContext('2d');

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        chartInstance.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Semantic', 'Keyword', 'Hybrid'],
                datasets: [{
                    label: 'Queries Count',
                    data: [
                        stats.queries_by_method?.semantic || 0,
                        stats.queries_by_method?.keyword || 0,
                        stats.queries_by_method?.hybrid || 0,
                    ],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(237, 100, 166, 0.8)',
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [stats]);

    if (!stats) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-bold mb-4">Метрики</h3>
                <p className="text-gray-500">Нет данных</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-800">Метрики системы</h3>

            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-purple-50 rounded-lg p-4">
                    <p className="text-purple-600 text-sm font-semibold">Всего запросов</p>
                    <p className="text-3xl font-bold text-purple-900">{stats.total_queries || 0}</p>
                </div>

                <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-blue-600 text-sm font-semibold">Активных пользователей</p>
                    <p className="text-3xl font-bold text-blue-900">{stats.active_users || 0}</p>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                    <p className="text-green-600 text-sm font-semibold">Cache Hit Rate</p>
                    <p className="text-3xl font-bold text-green-900">
                        {stats.cache_hit_rate ? `${(stats.cache_hit_rate * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                </div>

                <div className="bg-yellow-50 rounded-lg p-4">
                    <p className="text-yellow-600 text-sm font-semibold">Avg Response Time</p>
                    <p className="text-3xl font-bold text-yellow-900">
                        {stats.avg_response_time ? `${stats.avg_response_time.toFixed(0)}ms` : 'N/A'}
                    </p>
                </div>
            </div>

            <div className="h-64">
                <canvas ref={chartRef}></canvas>
            </div>
        </div>
    );
}

// ============================================================================
// HISTORY PANEL COMPONENT
// ============================================================================

function HistoryPanel({ history, onQuerySelect }) {
    if (!history || history.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-bold mb-4">История запросов</h3>
                <p className="text-gray-500">История пуста</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-800">История запросов</h3>

            <div className="space-y-2 max-h-96 overflow-y-auto">
                {history.map((item, index) => (
                    <div
                        key={index}
                        onClick={() => onQuerySelect(item.query, item.method)}
                        className="p-3 bg-gray-50 rounded hover:bg-purple-50 cursor-pointer transition"
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="font-semibold text-gray-800">{item.query}</span>
                            <span className="text-xs text-gray-500">{item.method}</span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-gray-600">
                            <span>Результатов: {item.results_count}</span>
                            <span>{item.elapsed_ms?.toFixed(0)}ms</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ============================================================================
// HEADER COMPONENT
// ============================================================================

function Header({ username, onLogout, wsConnected }) {
    return (
        <header className="gradient-bg text-white shadow-lg">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">RAG Knowledge Base</h1>
                        <p className="text-purple-200 text-sm">Semantic Search Dashboard</p>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                            <span className="text-sm">{wsConnected ? 'Connected' : 'Disconnected'}</span>
                        </div>

                        <div className="text-right">
                            <p className="font-semibold">{username}</p>
                            <button
                                onClick={onLogout}
                                className="text-sm text-purple-200 hover:text-white underline"
                            >
                                Выйти
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}

// ============================================================================
// MAIN APPLICATION COMPONENT
// ============================================================================

function App() {
    const [authenticated, setAuthenticated] = useState(false);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [wsConnected, setWsConnected] = useState(false);
    const [streamingProgress, setStreamingProgress] = useState('');

    const apiService = useRef(new APIService());
    const wsService = useRef(null);

    useEffect(() => {
        if (apiService.current.isAuthenticated()) {
            setAuthenticated(true);
            initializeWebSocket();
            loadStats();
        }
    }, []);

    useEffect(() => {
        if (authenticated) {
            const interval = setInterval(loadStats, CONFIG.CHART_UPDATE_INTERVAL);
            return () => clearInterval(interval);
        }
    }, [authenticated]);

    const initializeWebSocket = () => {
        wsService.current = new WebSocketService(
            handleWebSocketMessage,
            () => setWsConnected(true),
            () => setWsConnected(false)
        );
        wsService.current.connect();
    };

    const handleWebSocketMessage = (message) => {
        switch (message.type) {
            case 'connected':
                console.log('WebSocket connected:', message.client_id);
                break;

            case 'progress':
                setStreamingProgress(message.message);
                break;

            case 'result_chunk':
                setResults(prev => {
                    const newResults = [...prev];
                    newResults[message.index] = message.data;
                    return newResults;
                });
                break;

            case 'query_complete':
                setLoading(false);
                setStreamingProgress('');
                loadStats();
                break;

            case 'error':
                setError(message.error);
                setLoading(false);
                setStreamingProgress('');
                break;
        }
    };

    const loadStats = async () => {
        try {
            const statsData = await apiService.current.getStats();
            setStats(statsData);
            if (statsData.recent_queries) {
                setHistory(statsData.recent_queries);
            }
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    };

    const handleSearch = async (query, method, topK) => {
        setLoading(true);
        setError('');
        setResults([]);
        setStreamingProgress('Начинаем поиск...');

        try {
            // Use WebSocket for streaming if connected, fallback to HTTP
            if (wsConnected) {
                wsService.current.query(query, method, topK);
            } else {
                const result = await apiService.current.query(query, method, topK);
                setResults(result.results || []);
                setLoading(false);
                loadStats();
            }
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const handleHistoryQuerySelect = (query, method) => {
        handleSearch(query, method, CONFIG.DEFAULT_TOP_K);
    };

    const handleLogout = () => {
        apiService.current.logout();
        wsService.current?.disconnect();
        setAuthenticated(false);
        setResults([]);
        setStats(null);
        setHistory([]);
    };

    const handleAuthSuccess = () => {
        setAuthenticated(true);
        initializeWebSocket();
        loadStats();
    };

    if (!authenticated) {
        return <AuthForm apiService={apiService.current} onAuthSuccess={handleAuthSuccess} />;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Header
                username={apiService.current.getUsername()}
                onLogout={handleLogout}
                wsConnected={wsConnected}
            />

            <main className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main content - Search and Results */}
                    <div className="lg:col-span-2">
                        <SearchBar onSearch={handleSearch} loading={loading} />
                        <ResultsList
                            results={results}
                            loading={loading}
                            error={error}
                            streamingProgress={streamingProgress}
                        />
                    </div>

                    {/* Sidebar - Metrics and History */}
                    <div className="space-y-6">
                        <MetricsPanel stats={stats} />
                        <HistoryPanel
                            history={history}
                            onQuerySelect={handleHistoryQuerySelect}
                        />
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 mt-12">
                <div className="container mx-auto px-4 py-6 text-center text-gray-600">
                    <p>RAG Knowledge Base Dashboard v1.0</p>
                    <p className="text-sm text-gray-500 mt-1">
                        Semantic Search • Real-time Updates • Production Ready
                    </p>
                </div>
            </footer>
        </div>
    );
}

// ============================================================================
// RENDER APPLICATION
// ============================================================================

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
