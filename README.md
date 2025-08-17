# 🤖 GenAI Chatbot Boilerplate

A production-ready, multi-tenant GenAI chatbot platform built with **FastAPI**, **React**, and **PostgreSQL**. Features real-time chat, document processing, RAG capabilities, and comprehensive admin management.

## ✨ Key Features

### 🎯 **Core Functionality**
- **Real-time WebSocket Chat** with typing indicators and message broadcasting
- **Multi-tenant Architecture** with complete tenant isolation
- **Document Upload & RAG** with automatic text extraction and chunking
- **AI Model Integration** supporting OpenAI, Anthropic, Google, and custom models
- **Chat History Persistence** with full message search and session management

### 🔐 **Authentication & Security**
- **JWT Authentication** with refresh token rotation
- **OAuth Support** framework (Google, Microsoft, Apple ready)
- **Role-Based Access Control** (Super Admin, Tenant Admin, User, Viewer)
- **Multi-factor Security** with bcrypt password hashing
- **API Key Management** for tenant-specific AI provider keys

### 👑 **Admin Center**
- **Tenant Management** - Create, configure, and monitor tenants
- **User Management** - Role assignment, activation/deactivation
- **System Statistics** - Usage metrics and analytics
- **API Key Configuration** - Secure AI provider key management
- **Real-time Monitoring** - Connection stats and system health

### 🏗️ **Technical Excellence**
- **Async/Await Throughout** - High performance with FastAPI + AsyncIO
- **Type Safety** - Full Pydantic validation and SQLAlchemy typing
- **Clean Architecture** - Proper service layer separation
- **Comprehensive Logging** - Structured logging with Loguru
- **Health Checks & Metrics** - Kubernetes-ready with Prometheus support

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** and **Node.js 18+**
- **PostgreSQL 13+** and **Redis 6+**
- **Git** for cloning

### 1. Clone & Setup
```bash
git clone https://github.com/nithinmohantk/genai-boilerplate-python.git
cd genai-boilerplate-python
```

### 2. Backend Setup
```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database and API keys
```

### 3. Database Setup
```bash
# Start PostgreSQL and Redis
# Then initialize the database with default tenant and admin
python scripts/init_db.py
```

### 4. Start Backend
```bash
python src/main.py
```
🎉 **Backend running at http://localhost:8000**

### 5. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm start
```
🎉 **Frontend running at http://localhost:3000**

### 6. Login & Test
- **Admin Login**: `admin@example.com` / `admin123!`
- **API Docs**: http://localhost:8000/docs
- **WebSocket Test**: Use scripts/test_auth.py

## 📚 API Documentation

### Authentication Endpoints
```bash
POST /api/v1/auth/login          # User login
POST /api/v1/auth/register       # User registration  
POST /api/v1/auth/refresh        # Token refresh
GET  /api/v1/auth/me             # Current user info
PUT  /api/v1/auth/me             # Update profile
POST /api/v1/auth/logout         # User logout
```

### Chat Endpoints
```bash
POST /api/v1/chat/sessions       # Create chat session
GET  /api/v1/chat/sessions       # List user sessions
GET  /api/v1/chat/sessions/{id}  # Get session with messages
POST /api/v1/chat/completions    # Generate AI response
GET  /api/v1/chat/models         # Available AI models
GET  /api/v1/chat/search         # Search sessions
```

### Document Endpoints
```bash
POST /api/v1/documents/upload    # Upload document
GET  /api/v1/documents/          # List documents
POST /api/v1/documents/{id}/process  # Process for RAG
GET  /api/v1/documents/{id}/chunks   # View document chunks
```

### Admin Endpoints
```bash
GET  /api/v1/admin/tenants       # Manage tenants (Super Admin)
GET  /api/v1/admin/users         # Manage users (Tenant Admin)
GET  /api/v1/admin/api-keys      # Manage API keys
GET  /api/v1/admin/system/stats  # System statistics
```

### WebSocket Endpoints
```bash
WS   /api/v1/ws/{session_id}     # Real-time chat
GET  /api/v1/ws/stats            # Connection statistics
```

# 🏛️ Architecture Documentation

## 🌐 High-Level Design (HLD)

### System Overview
The GenAI Chatbot platform is designed as a **microservices-based, multi-tenant SaaS application** that provides AI-powered conversational capabilities with document processing, RAG (Retrieval-Augmented Generation), and comprehensive administration features.

### Core Architectural Principles
- **Multi-Tenancy**: Complete data isolation between tenants
- **Event-Driven**: Asynchronous processing with WebSocket real-time updates
- **API-First**: RESTful APIs with OpenAPI documentation
- **Cloud-Native**: Container-ready with Kubernetes support
- **Security-First**: JWT authentication, RBAC, and encrypted storage
- **Scalability**: Horizontal scaling with load balancers and database clustering

### System Architecture Diagram
```mermaid
graph TB
    subgraph "Client Layer"
        WEB["🌐 React SPA\n• Chat Interface\n• Admin Dashboard\n• Theme System"]
        MOBILE["📱 Mobile App\n(Future)"]
        API_CLIENT["🔧 API Clients"]
    end
    
    subgraph "Load Balancer"
        LB["⚖️ Nginx/HAProxy\n• SSL Termination\n• Rate Limiting\n• Request Routing"]
    end
    
    subgraph "Application Layer"
        API["🚀 FastAPI Backend\n• REST API\n• WebSocket Server\n• Authentication\n• Business Logic"]
        WEBSOCKET["🔌 WebSocket Manager\n• Real-time Chat\n• Connection Pool\n• Event Broadcasting"]
    end
    
    subgraph "Service Layer"
        AUTH["🔐 Auth Service\n• JWT Management\n• User Sessions\n• Role-based Access"]
        CHAT["💬 Chat Service\n• Message Processing\n• AI Integration\n• Context Management"]
        DOC["📄 Document Service\n• File Processing\n• Text Extraction\n• RAG Pipeline"]
        ADMIN["👑 Admin Service\n• Tenant Management\n• User Administration\n• System Monitoring"]
        THEME["🎨 Theme Service\n• Theme Management\n• Dynamic Styling\n• Customization"]
    end
    
    subgraph "Data Layer"
        PG[("🐘 PostgreSQL\n• Multi-tenant Data\n• Transactional\n• ACID Compliance")]
        REDIS[("🔴 Redis\n• Session Storage\n• Real-time Cache\n• Message Queue")]
        VECTOR[("🧮 Vector Store\n• Document Embeddings\n• Semantic Search\n• RAG Context")]
    end
    
    subgraph "External Services"
        OPENAI["🤖 OpenAI\n• GPT Models\n• Embeddings"]
        ANTHROPIC["🎭 Anthropic\n• Claude Models"]
        GOOGLE["🔍 Google AI\n• Gemini Models"]
        STORAGE["☁️ Cloud Storage\n• File Storage\n• Backups"]
    end
    
    WEB --> LB
    MOBILE --> LB
    API_CLIENT --> LB
    LB --> API
    API --> WEBSOCKET
    API --> AUTH
    API --> CHAT
    API --> DOC
    API --> ADMIN
    API --> THEME
    
    AUTH --> PG
    AUTH --> REDIS
    CHAT --> PG
    CHAT --> REDIS
    CHAT --> VECTOR
    DOC --> PG
    DOC --> VECTOR
    DOC --> STORAGE
    ADMIN --> PG
    ADMIN --> REDIS
    THEME --> PG
    
    CHAT --> OPENAI
    CHAT --> ANTHROPIC
    CHAT --> GOOGLE
```

## 🔧 Low-Level Design (LLD)

### Backend Architecture (FastAPI)

#### Directory Structure
```
backend/
├── src/
│   ├── api/                    # API endpoint handlers
│   │   ├── v1/                 # API version 1
│   │   │   └── router.py       # Main API router
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── chat.py             # Chat endpoints
│   │   ├── documents.py        # Document management
│   │   ├── admin.py            # Admin endpoints
│   │   ├── websocket.py        # WebSocket handlers
│   │   └── themes.py           # Theme management
│   ├── core/                   # Core functionality
│   │   ├── database.py         # Database connection
│   │   ├── cache.py            # Redis operations
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging.py          # Logging configuration
│   │   └── genai_client.py     # AI provider clients
│   ├── models/                 # Pydantic & SQLAlchemy models
│   │   ├── auth.py             # User, Tenant, Permissions
│   │   ├── chat.py             # Chat, Message, Session
│   │   └── theme.py            # Theme models
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── chat_service.py     # Chat processing
│   │   ├── document_service.py # Document processing
│   │   ├── memory_service.py   # Conversation memory
│   │   ├── persona_service.py  # AI persona management
│   │   └── websocket_manager.py# WebSocket management
│   ├── auth/                   # Authentication utilities
│   │   └── dependencies.py     # FastAPI dependencies
│   └── startup/                # Application startup
│       └── theme_init.py       # Theme initialization
├── config/                     # Configuration management
│   ├── settings.py             # Environment settings
│   └── ai_models.py            # AI model configurations
└── scripts/                    # Utility scripts
    ├── init_db.py              # Database initialization
    └── test_auth.py            # Authentication testing
```

#### Component Interaction Flow
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Database
    participant Cache
    participant AI_Provider
    
    Client->>API: HTTP Request + JWT
    API->>API: Validate JWT Token
    API->>Service: Business Logic Call
    Service->>Database: Query/Update Data
    Database-->>Service: Result
    Service->>Cache: Cache Operations
    Cache-->>Service: Cached Data
    Service->>AI_Provider: AI API Call
    AI_Provider-->>Service: AI Response
    Service-->>API: Processed Result
    API-->>Client: HTTP Response
```

### Frontend Architecture (React + TypeScript)

#### Directory Structure
```
frontend/
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── Layout.tsx          # Main layout with sidebar
│   │   ├── NavigationMonitor.tsx # Navigation state manager
│   │   ├── ThemeSelector.tsx   # Dynamic theme selection
│   │   ├── DarkModeToggle.tsx  # Theme mode toggle
│   │   └── ErrorBoundary.tsx   # Error handling wrapper
│   ├── pages/                  # Page-level components
│   │   ├── ChatPage.tsx        # Main chat interface
│   │   ├── DocumentsPage.tsx   # Document management
│   │   ├── SettingsPage.tsx    # User settings
│   │   └── AdminPage.tsx       # Admin dashboard
│   ├── contexts/               # React Context providers
│   │   ├── ThemeContext.tsx    # Theme management
│   │   ├── ThemeApplicationContext.tsx # Theme application
│   │   └── theme-constants.ts  # Theme constants
│   ├── hooks/                  # Custom React hooks
│   │   └── useThemeApplication.ts # Theme hook
│   ├── utils/                  # Utility functions
│   │   └── globalThemeManager.ts # Global theme manager
│   └── types/                  # TypeScript type definitions
└── public/                     # Static assets
```

#### React Component Hierarchy
```mermaid
graph TD
    APP["App.tsx\n• Router Setup\n• Context Providers"] --> LAYOUT["Layout.tsx\n• Sidebar Navigation\n• App Bar\n• Refresh Logic"]
    
    LAYOUT --> CHAT["ChatPage.tsx\n• Message Display\n• Input Interface\n• WebSocket Connection"]
    LAYOUT --> DOCS["DocumentsPage.tsx\n• File Upload\n• Document List\n• Processing Status"]
    LAYOUT --> SETTINGS["SettingsPage.tsx\n• User Preferences\n• Theme Selection\n• AI Configuration"]
    LAYOUT --> ADMIN["AdminPage.tsx\n• User Management\n• System Stats\n• Theme Administration"]
    
    LAYOUT --> THEME["ThemeSelector.tsx\n• Theme Preview\n• Dynamic Loading\n• Real-time Updates"]
    LAYOUT --> TOGGLE["DarkModeToggle.tsx\n• Light/Dark Switch\n• System Detection"]
    
    subgraph "Context Providers"
        THEME_CTX["ThemeContext\n• Theme State\n• Mode Management"]
        APP_CTX["ThemeApplicationContext\n• Dynamic Styling\n• CSS Variables"]
    end
    
    APP --> THEME_CTX
    APP --> APP_CTX
```

## 🗄️ Data Architecture

### Database Schema Design

#### Entity Relationship Diagram
```mermaid
erDiagram
    TENANT ||--o{ USER : contains
    TENANT ||--o{ TENANT_API_KEY : has
    TENANT ||--o{ CHAT_SESSION : owns
    TENANT ||--o{ CHAT_DOCUMENT : stores
    TENANT ||--o{ THEME : customizes
    
    USER ||--o{ USER_AUTH_PROVIDER : authenticates
    USER ||--o{ CHAT_SESSION : creates
    USER ||--o{ CHAT_MESSAGE : sends
    USER ||--o{ CHAT_DOCUMENT : uploads
    USER ||--o{ USER_MEMORY : remembers
    
    CHAT_SESSION ||--o{ CHAT_MESSAGE : contains
    CHAT_SESSION ||--o{ CHAT_DOCUMENT : references
    CHAT_SESSION ||--o{ USER_MEMORY : generates
    
    CHAT_DOCUMENT ||--o{ DOCUMENT_CHUNK : splits
    
    PERSONA ||--o{ CHAT_SESSION : influences
    
    TENANT {
        uuid id PK
        string name
        string domain UK
        enum status
        json settings
        json branding
        json limits
        timestamp created_at
        timestamp updated_at
        uuid created_by FK
    }
    
    USER {
        uuid id PK
        uuid tenant_id FK
        string email
        string username
        string full_name
        string hashed_password
        boolean is_active
        boolean is_verified
        enum role
        json permissions
        string avatar_url
        string timezone
        string language
        json preferences
        timestamp created_at
        timestamp updated_at
        timestamp last_login_at
    }
    
    CHAT_SESSION {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        string title
        enum status
        json model_config
        text system_prompt
        integer context_window
        timestamp created_at
        timestamp updated_at
        timestamp archived_at
    }
    
    CHAT_MESSAGE {
        uuid id PK
        uuid session_id FK
        uuid user_id FK
        text message
        enum message_type
        json message_metadata
        integer tokens_used
        integer processing_time_ms
        timestamp timestamp
    }
    
    CHAT_DOCUMENT {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        uuid session_id FK
        string filename
        string content_type
        integer file_size
        string file_path
        boolean processed
        text extracted_text
        json metadata
        timestamp created_at
        timestamp processed_at
    }
    
    THEME {
        uuid id PK
        string name UK
        string display_name
        text description
        enum category
        json color_scheme
        boolean supports_dark_mode
        json accessibility_features
        json css_variables
        boolean is_system
        boolean is_active
        integer usage_count
        timestamp created_at
        timestamp updated_at
    }
```

### Multi-Tenant Data Isolation

#### Tenant Isolation Strategy
```sql
-- Row-Level Security (RLS) Example
CREATE POLICY tenant_isolation_policy ON chat_messages
    FOR ALL TO app_user
    USING (session_id IN (
        SELECT id FROM chat_sessions 
        WHERE tenant_id = current_setting('app.current_tenant_id')::uuid
    ));

-- Tenant-aware queries with automatic filtering
SELECT cm.* 
FROM chat_messages cm
INNER JOIN chat_sessions cs ON cm.session_id = cs.id
WHERE cs.tenant_id = $1;  -- Tenant ID from JWT
```

#### Database Indexing Strategy
```sql
-- Composite indexes for multi-tenant queries
CREATE INDEX idx_session_tenant_user ON chat_sessions(tenant_id, user_id);
CREATE INDEX idx_message_session_timestamp ON chat_messages(session_id, timestamp DESC);
CREATE INDEX idx_user_tenant_email ON users(tenant_id, email);
CREATE INDEX idx_document_tenant_user ON chat_documents(tenant_id, user_id, created_at DESC);

-- Partial indexes for active records
CREATE INDEX idx_active_sessions ON chat_sessions(tenant_id, updated_at DESC) 
    WHERE status = 'active';
CREATE INDEX idx_active_users ON users(tenant_id) 
    WHERE is_active = true;
```

### Caching Strategy

#### Redis Data Structure
```
Redis Key Patterns:
├── session:{session_id}                    # Session metadata
├── user:{user_id}:sessions                 # User's active sessions
├── tenant:{tenant_id}:config               # Tenant configuration
├── ws:connections:{session_id}             # WebSocket connections
├── chat:history:{session_id}:messages      # Recent chat messages
├── rag:cache:{document_hash}:chunks        # Document chunks cache
├── ai:response:{query_hash}                # AI response cache
└── theme:{tenant_id}:active                # Active theme cache
```

#### Cache Invalidation Strategy
```python
# Example cache invalidation logic
class CacheManager:
    async def invalidate_user_sessions(self, user_id: UUID):
        """Invalidate all caches related to a user."""
        await self.redis.delete(f"user:{user_id}:sessions")
        
    async def invalidate_tenant_config(self, tenant_id: UUID):
        """Invalidate tenant-specific configuration cache."""
        pattern = f"tenant:{tenant_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

## 🚀 Deployment Architecture

### Container Orchestration
```yaml
# Kubernetes Deployment Example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: genai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: genai-backend
  template:
    metadata:
      labels:
        app: genai-backend
    spec:
      containers:
      - name: backend
        image: thingxcloud/genai-chatbot-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### Scalability Considerations
- **Horizontal Pod Autoscaling**: Based on CPU/memory usage
- **Database Connection Pooling**: PgBouncer for PostgreSQL
- **Redis Clustering**: For high availability caching
- **CDN Integration**: Static asset delivery
- **Load Balancing**: Multi-zone deployment

## 🔒 Security Architecture

### Authentication & Authorization Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth_Service
    participant Database
    participant Redis
    
    User->>Frontend: Login Credentials
    Frontend->>API: POST /auth/login
    API->>Auth_Service: Validate Credentials
    Auth_Service->>Database: Check User & Tenant
    Database-->>Auth_Service: User Data
    Auth_Service->>Auth_Service: Generate JWT + Refresh Token
    Auth_Service->>Redis: Store Session
    Auth_Service-->>API: Tokens + User Info
    API-->>Frontend: JWT + Refresh Token
    Frontend->>Frontend: Store Tokens (HttpOnly)
    
    Note over User,Redis: Subsequent API Calls
    Frontend->>API: API Request + JWT
    API->>Auth_Service: Validate JWT
    Auth_Service->>Redis: Check Session
    Redis-->>Auth_Service: Session Valid
    Auth_Service-->>API: User Context
    API->>API: Process Request with Tenant Context
```

### Data Security Measures
- **JWT Tokens**: RS256 algorithm with key rotation
- **Password Security**: bcrypt with salt rounds
- **API Rate Limiting**: Per-user and per-tenant limits
- **SQL Injection Prevention**: Parameterized queries
- **CORS Configuration**: Restricted origins
- **Input Validation**: Pydantic schema validation
- **Audit Logging**: All security events logged

---

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/genai_chatbot
REDIS_URL=redis://localhost:6379/0

# Security  
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers (Optional)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=claude-your-key
GOOGLE_API_KEY=your-google-key

# App Settings
APP_NAME="GenAI Chatbot"
ENVIRONMENT=development
DEBUG=true
```

### Multi-Model Configuration
Each tenant can configure their own AI provider keys through the admin panel with support for the latest AI models:

#### **OpenAI Models**
- **GPT-4 Series**: GPT-4, GPT-4 Turbo, GPT-4o, GPT-4o Mini, GPT-4.1, GPT-4.1 Mini, GPT-4.1 Nano
- **GPT-3.5 Series**: GPT-3.5 Turbo, GPT-3.5 Turbo 16K
- **GPT-5 Series**: GPT-5, GPT-5.0 Mini, GPT-5.0 Nano ✨ **Latest Release**
- **Open Source**: GPT-OSS 20B

#### **Anthropic Models**
- **Claude 3 Series**: Claude 3 Haiku, Claude 3 Sonnet, Claude 3 Opus
- **Claude 3.5 Series**: Claude 3.5 Sonnet, Claude 3.5 Haiku
- **Claude 3.7 Series**: Claude 3.7 Sonnet ✨ **Latest Release**
- **Claude 4.0 Series**: Claude 4.0 Opus, Claude 4.0 Sonnet ✨ **Latest Release**

#### **Google Models**
- **Gemini 1.5 Series**: Gemini 1.5 Flash, Gemini 1.5 Pro
- **Gemini 2.5 Series**: Gemini 2.5 Flash, Gemini 2.5 Pro (Latest)
- **Legacy Models**: Gemini Pro, Gemini Pro Vision

#### **Additional Providers**
- **Azure OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Hugging Face**: DialoGPT, Llama 2 (7B/13B/70B), Mistral 7B Instruct
- **Custom**: Any OpenAI-compatible API

## 🎭 User Roles & Permissions

### Role Hierarchy
```
Super Admin    🏆 Full system access, manage all tenants
    │
Tenant Admin   👑 Manage tenant users, settings, API keys  
    │
Tenant User    👤 Chat, upload documents, personal settings
    │
Tenant Viewer  👁️ Read-only access to tenant resources
```

### Permission Matrix
| Feature | Super Admin | Tenant Admin | User | Viewer |
|---------|-------------|--------------|------|--------|
| Manage Tenants | ✅ | ❌ | ❌ | ❌ |
| System Stats | ✅ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅* | ❌ | ❌ |
| API Keys | ✅ | ✅* | ❌ | ❌ |
| Chat & AI | ✅ | ✅ | ✅ | ✅ |
| Upload Docs | ✅ | ✅ | ✅ | ❌ |

*Within their tenant only

## 🔌 WebSocket Integration

### Real-time Features
- **Live Chat Messages** - Instant message delivery
- **Typing Indicators** - See when others are typing
- **Connection Status** - Real-time user presence
- **Multi-device Sync** - Messages sync across devices

### WebSocket Usage
```javascript
// Connect to chat session
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${sessionId}?token=${authToken}`);

// Send message
ws.send(JSON.stringify({
  type: 'chat',
  data: { message: 'Hello AI!' }
}));

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'message') {
    displayMessage(data.data);
  }
};
```

## 📄 Document Processing & RAG

### Supported Formats
- **Text**: `.txt`, `.md` (Markdown)
- **PDF**: `.pdf` with text extraction
- **Word**: `.docx` documents
- **Spreadsheets**: `.xlsx`, `.csv`

### RAG Pipeline
1. **Upload** → Document stored securely per tenant
2. **Process** → Text extraction and intelligent chunking
3. **Index** → Searchable chunks with metadata
4. **Query** → Semantic search during chat
5. **Context** → Relevant chunks added to AI prompts

## 🐳 Docker Deployment

### Quick Docker Setup
```bash
# Build and run with docker-compose
docker-compose up --build

# Or run individual services
docker build -t genai-backend ./backend
docker build -t genai-frontend ./frontend

docker run -p 8000:8000 genai-backend
docker run -p 3000:3000 genai-frontend
```

### Docker Hub Integration

This project includes Docker Hub integration with pre-configured build and push scripts for the `thingxcloud` account:

```bash
# Build production images locally (no push)
make docker-build-prod

# Build and push to Docker Hub (requires Docker Hub login)
make docker-push

# Or use the script directly
./scripts/docker-push.sh --build-only  # Build only
./scripts/docker-push.sh               # Build and push
```

**Available Images:**
- `thingxcloud/genai-boilerplate-python-backend:latest`
- `thingxcloud/genai-boilerplate-python-frontend:latest`

### Production Deployment
```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Set up reverse proxy (nginx/traefik)
# Configure SSL certificates
# Set environment variables for production
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run authentication tests
python scripts/test_auth.py

# Run all tests (when test suite is added)
pytest tests/

# Check linting
ruff check src/
black --check src/
```

### Frontend Tests
```bash
cd frontend

# Run component tests
npm test

# Run E2E tests
npm run test:e2e

# Check linting
npm run lint
```

## 🔍 Monitoring & Observability

### Health Checks
- `GET /health` - Application health
- `GET /api/v1/health/live` - Liveness probe
- `GET /api/v1/health/ready` - Readiness probe

### Metrics
- `GET /metrics` - Prometheus metrics
- Connection counts, message rates
- Database performance, cache hit rates
- AI API usage and costs

### Logging
Structured JSON logs with:
- Request/response tracking
- Authentication events
- Chat message audit trail
- Error tracking with stack traces

## 🚨 Security Features

### Authentication Security
- **JWT with RS256** (configurable algorithm)
- **Refresh Token Rotation** - Automatic token renewal
- **Session Management** - Device tracking and revocation
- **Rate Limiting** - Prevent brute force attacks

### Data Protection
- **Tenant Isolation** - Complete data separation
- **Encrypted Storage** - Passwords with bcrypt
- **Secure Headers** - CORS, CSP, HSTS configured
- **Input Validation** - Pydantic schema validation

### API Security
- **HTTPS Only** in production
- **API Key Management** - Encrypted storage
- **Request Logging** - Full audit trail
- **Permission Checks** - Role-based access control

## 🤝 Contributing

### Development Setup
```bash
# Backend development
cd backend
pip install -r requirements-dev.txt
pre-commit install

# Frontend development  
cd frontend
npm install
npm run dev
```

### Code Standards
- **Python**: Black formatting, Ruff linting, type hints
- **JavaScript**: Prettier, ESLint, TypeScript
- **Commits**: Conventional commits format
- **Testing**: Unit + integration test coverage

## 📞 Support & Documentation

- **🐛 Issues**: [GitHub Issues](https://github.com/nithinmohantk/genai-boilerplate-python/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/nithinmohantk/genai-boilerplate-python/discussions)  
- **📖 Wiki**: [Project Wiki](https://github.com/nithinmohantk/genai-boilerplate-python/wiki)
- **🚀 Releases**: [Release Notes](https://github.com/nithinmohantk/genai-boilerplate-python/releases)

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🎯 What's Next?

This boilerplate provides a solid foundation for building production GenAI applications. Here are some potential enhancements:

### Immediate Extensions
- **Vector Database Integration** (Pinecone, Weaviate, Chroma)
- **Advanced RAG** with semantic chunking and reranking
- **Streaming Responses** for real-time AI generation
- **Voice Chat** with speech-to-text integration

### Advanced Features
- **Multi-language Support** with i18n
- **Custom Model Fine-tuning** workflows
- **Analytics Dashboard** with usage insights
- **Workflow Automation** with LangChain agents

### Enterprise Features
- **SSO Integration** (SAML, LDAP)
- **Audit Logging** with compliance reports
- **White-label Branding** per tenant
- **API Gateway** with rate limiting and quotas

---

**🚀 Ready to build the next generation of AI-powered applications!**

*Built with ❤️ by [Nithin Mohan](https://github.com/nithinmohantk)*
