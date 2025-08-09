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

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │  FastAPI API    │    │  PostgreSQL     │
│                 │    │                 │    │                 │
│ • Chat UI       │◄──►│ • REST API      │◄──►│ • Multi-tenant  │
│ • Admin Panel   │    │ • WebSocket     │    │ • Chat History  │
│ • Auth Flow     │    │ • Auth & RBAC   │    │ • Documents     │
└─────────────────┘    │ • Document RAG  │    │ • Users/Tenants │
                       │ • AI Integration│    └─────────────────┘
                       └─────────────────┘              │
                              │                         │
                    ┌─────────────────┐    ┌─────────────────┐
                    │      Redis      │    │   AI Providers  │
                    │                 │    │                 │
                    │ • Sessions      │    │ • OpenAI        │
                    │ • Cache         │    │ • Anthropic     │
                    │ • Task Queue    │    │ • Google        │
                    └─────────────────┘    │ • Custom APIs   │
                                          └─────────────────┘
```

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
Each tenant can configure their own AI provider keys through the admin panel:
- **OpenAI**: GPT-4, GPT-3.5 Turbo, GPT-3.5 Turbo 16K
- **Anthropic**: Claude 3 (Haiku, Sonnet, Opus)  
- **Google**: Gemini Pro, Gemini Pro Vision
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
