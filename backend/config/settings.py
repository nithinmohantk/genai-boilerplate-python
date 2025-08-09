"""
Configuration management using Pydantic Settings.
Handles all environment variables and application configuration.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Configuration
    app_name: str = Field(default="GenAI Chatbot", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(
        default="Production-ready GenAI Chatbot with RAG",
        description="Application description",
    )
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")
    workers: int = Field(default=1, description="Number of worker processes")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins",
    )
    cors_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="CORS allowed methods",
    )
    cors_headers: List[str] = Field(default=["*"], description="CORS allowed headers")

    # Security
    secret_key: str = Field(
        default="your-super-secret-key-here-change-in-production",
        description="Secret key for JWT tokens",
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")

    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/genai_chatbot",
        description="Database URL",
    )
    database_echo: bool = Field(default=False, description="SQLAlchemy echo SQL queries")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    # AI Provider Configuration
    # OpenAI
    openai_api_key: Optional[str] = Field(
        default=None, description="OpenAI API key"
    )
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model")
    openai_max_tokens: int = Field(
        default=1000, description="OpenAI max tokens"
    )
    openai_temperature: float = Field(
        default=0.7, description="OpenAI temperature"
    )

    # Anthropic
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    anthropic_model: str = Field(
        default="claude-3-haiku-20240307", description="Anthropic model"
    )

    # Google
    google_api_key: Optional[str] = Field(
        default=None, description="Google API key"
    )
    google_project_id: Optional[str] = Field(
        default=None, description="Google project ID"
    )
    google_model: str = Field(default="gemini-pro", description="Google model")

    # Azure OpenAI
    azure_openai_api_key: Optional[str] = Field(
        default=None, description="Azure OpenAI API key"
    )
    azure_openai_endpoint: Optional[str] = Field(
        default=None, description="Azure OpenAI endpoint"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-01", description="Azure OpenAI API version"
    )
    azure_openai_deployment: Optional[str] = Field(
        default=None, description="Azure OpenAI deployment name"
    )

    # Hugging Face
    huggingface_api_key: Optional[str] = Field(
        default=None, description="Hugging Face API key"
    )
    huggingface_model: str = Field(
        default="microsoft/DialoGPT-medium", description="Hugging Face model"
    )

    # Vector Store Configuration
    vector_store_type: str = Field(
        default="faiss", description="Vector store type (faiss, chroma, pinecone)"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model"
    )
    embedding_dimension: int = Field(
        default=384, description="Embedding dimension"
    )
    chunk_size: int = Field(default=1000, description="Text chunk size")
    chunk_overlap: int = Field(default=200, description="Text chunk overlap")

    # FAISS Configuration
    faiss_index_path: str = Field(
        default="./data/embeddings/faiss_index", description="FAISS index path"
    )
    faiss_metadata_path: str = Field(
        default="./data/embeddings/metadata.json", description="FAISS metadata path"
    )

    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./data/embeddings/chroma", description="ChromaDB persist directory"
    )
    chroma_collection_name: str = Field(
        default="documents", description="ChromaDB collection name"
    )

    # Pinecone Configuration
    pinecone_api_key: Optional[str] = Field(
        default=None, description="Pinecone API key"
    )
    pinecone_environment: str = Field(
        default="us-west1-gcp-free", description="Pinecone environment"
    )
    pinecone_index_name: str = Field(
        default="genai-chatbot", description="Pinecone index name"
    )

    # Document Processing
    documents_path: str = Field(
        default="./data/documents", description="Documents storage path"
    )
    max_file_size: int = Field(
        default=10485760, description="Maximum file size in bytes (10MB)"
    )
    allowed_file_types: List[str] = Field(
        default=["pdf", "txt", "docx", "xlsx", "csv", "md"],
        description="Allowed file types",
    )

    # RAG Configuration
    rag_retrieval_type: str = Field(
        default="similarity", description="RAG retrieval type"
    )
    rag_k: int = Field(
        default=5, description="Number of documents to retrieve"
    )
    rag_score_threshold: float = Field(
        default=0.7, description="RAG score threshold"
    )
    rag_fetch_k: int = Field(
        default=10, description="Number of documents to fetch before filtering"
    )

    # Chat Configuration
    max_chat_history: int = Field(
        default=10, description="Maximum chat history length"
    )
    system_message: str = Field(
        default="You are a helpful AI assistant. Use the provided context to answer questions accurately and helpfully.",
        description="System message for the AI",
    )
    default_response: str = Field(
        default="I'm sorry, I don't have enough information to answer that question accurately.",
        description="Default response when no relevant context is found",
    )

    # Monitoring and Observability
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=8001, description="Metrics server port")
    enable_health_checks: bool = Field(default=True, description="Enable health checks")
    health_check_interval: int = Field(
        default=30, description="Health check interval in seconds"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100, description="Rate limit requests per window"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    # Cache Configuration
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")

    # Celery Configuration
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0", description="Celery result backend"
    )
    celery_task_serializer: str = Field(
        default="json", description="Celery task serializer"
    )
    celery_accept_content: List[str] = Field(
        default=["json"], description="Celery accepted content types"
    )
    celery_result_serializer: str = Field(
        default="json", description="Celery result serializer"
    )
    celery_timezone: str = Field(default="UTC", description="Celery timezone")

    # File Upload Configuration
    upload_path: str = Field(
        default="./data/uploads", description="File upload path"
    )
    max_upload_size: int = Field(
        default=50485760, description="Maximum upload size in bytes (50MB)"
    )
    allowed_upload_extensions: List[str] = Field(
        default=["pdf", "txt", "docx", "xlsx", "csv", "md", "json"],
        description="Allowed upload file extensions",
    )

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    docs_url: str = Field(default="/docs", description="OpenAPI docs URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI JSON URL")

    # Development Configuration
    reload_dirs: List[str] = Field(default=["src"], description="Reload directories")
    reload_extensions: List[str] = Field(
        default=[".py"], description="Reload file extensions"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("cors_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("cors_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v

    @field_validator("allowed_upload_extensions", mode="before")
    @classmethod
    def parse_allowed_upload_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse allowed upload extensions from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @field_validator("celery_accept_content", mode="before")
    @classmethod
    def parse_celery_accept_content(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse Celery accept content from string or list."""
        if isinstance(v, str):
            return [content.strip() for content in v.split(",")]
        return v

    @field_validator("reload_dirs", mode="before")
    @classmethod
    def parse_reload_dirs(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse reload directories from string or list."""
        if isinstance(v, str):
            return [dir_path.strip() for dir_path in v.split(",")]
        return v

    @field_validator("reload_extensions", mode="before")
    @classmethod
    def parse_reload_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse reload extensions from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
        }

    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
            "password": self.redis_password,
            "db": self.redis_db,
        }

    @property
    def cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration dictionary."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
