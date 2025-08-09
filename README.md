# GenAI Chatbot Boilerplate

A production-ready, highly configurable GenAI Chatbot with RAG (Retrieval Augmented Generation) capabilities, built with Python/FastAPI backend and React/TypeScript frontend.

## 🌟 Features

### Backend (Python/FastAPI)
- **Multiple AI Providers**: OpenAI, Anthropic, Google (Gemini), Azure OpenAI, Hugging Face
- **RAG Implementation**: FAISS vector database for document retrieval
- **Document Processing**: PDF, DOCX, TXT, MD, XLSX, CSV support
- **Highly Configurable**: Environment-based configuration with Pydantic Settings
- **Production Ready**: Logging, monitoring, health checks, caching (Redis)
- **Database Support**: PostgreSQL with SQLAlchemy and Alembic migrations
- **Testing**: Comprehensive test suite with pytest
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Background Tasks**: Celery for document processing

### Frontend (React/TypeScript)
- **Modern UI**: Material-UI components with responsive design
- **Real-time Chat**: WebSocket support for live conversations
- **Document Management**: Upload, process, and manage documents
- **Settings Panel**: Configure AI models, RAG parameters, and preferences
- **State Management**: React Query for server state management
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS + Material-UI theme integration

## 🏗 Project Structure

```
genai-boilerplate-python/
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/            # API endpoints and routing
│   │   ├── core/           # Core functionality (database, cache, etc.)
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions
│   │   └── tests/          # Test files
│   ├── config/             # Configuration files
│   ├── data/              # Data storage (documents, embeddings)
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml     # Python project configuration
│   └── .env.example       # Environment variables template
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service functions
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── public/            # Static files
│   └── package.json       # Node.js dependencies
├── scripts/               # Deployment and utility scripts
├── deployment/            # Docker and Kubernetes configs
└── docs/                  # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up database:**
```bash
# Run database migrations (once implemented)
alembic upgrade head
```

6. **Start the backend server:**
```bash
python src/main.py
```

The backend API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

The application is highly configurable through environment variables. Copy `.env.example` to `.env` and configure:

#### Core Settings
- `APP_NAME`: Application name
- `ENVIRONMENT`: Environment (development/production)
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL

#### AI Providers
Configure your preferred AI provider API keys:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_API_KEY`: Google API key
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `HUGGINGFACE_API_KEY`: Hugging Face API key

#### RAG Configuration
- `VECTOR_STORE_TYPE`: Vector store type (faiss/chroma/pinecone)
- `EMBEDDING_MODEL`: Embedding model name
- `CHUNK_SIZE`: Text chunk size for processing
- `RAG_K`: Number of documents to retrieve

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Docker

Build and run with Docker Compose:

```bash
docker-compose up -d
```

### Kubernetes

Deploy to Kubernetes:

```bash
kubectl apply -f deployment/kubernetes/
```

## 🛠 Development

### Backend Development

The backend uses:
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings
- **SQLAlchemy**: Database ORM
- **LangChain**: AI/ML integrations
- **FAISS**: Vector similarity search
- **Redis**: Caching and sessions
- **Celery**: Background tasks
- **Loguru**: Structured logging

### Frontend Development

The frontend uses:
- **React 19**: Modern React with hooks
- **TypeScript**: Type safety
- **Material-UI**: Component library
- **React Query**: Server state management
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first styling

### Code Quality

Both backend and frontend include:
- Linting and formatting
- Pre-commit hooks
- Type checking
- Automated testing

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] WebSocket support for real-time chat
- [ ] Authentication and user management
- [ ] Chat history persistence
- [ ] Advanced RAG features (re-ranking, hybrid search)
- [ ] Model fine-tuning support
- [ ] Multi-language support
- [ ] Plugin system
- [ ] Analytics dashboard

## 🆘 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the configuration options in `.env.example`

## ⚡ Performance Tips

- Use Redis for caching frequently accessed data
- Configure vector store properly for your use case
- Adjust chunk size based on your document types
- Monitor API usage and costs
- Use connection pooling for databases
- Enable compression for API responses

Happy coding! 🚀
