"""
Custom exceptions and exception handlers for the application.
"""

from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
import traceback


class GenAIChatbotException(Exception):
    """Base exception for GenAI Chatbot application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(GenAIChatbotException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class AuthenticationException(GenAIChatbotException):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationException(GenAIChatbotException):
    """Raised when authorization fails."""
    
    def __init__(
        self,
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ResourceNotFoundException(GenAIChatbotException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ConflictException(GenAIChatbotException):
    """Raised when there's a conflict with the current state."""
    
    def __init__(
        self,
        message: str = "Conflict with current state",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class RateLimitException(GenAIChatbotException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


class ExternalServiceException(GenAIChatbotException):
    """Raised when external service fails."""
    
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


class DocumentProcessingException(GenAIChatbotException):
    """Raised when document processing fails."""
    
    def __init__(
        self,
        message: str = "Document processing failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class VectorStoreException(GenAIChatbotException):
    """Raised when vector store operations fail."""
    
    def __init__(
        self,
        message: str = "Vector store operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class AIModelException(GenAIChatbotException):
    """Raised when AI model operations fail."""
    
    def __init__(
        self,
        model_name: str,
        message: str = "AI model error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"{model_name}: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


async def genai_chatbot_exception_handler(
    request: Request,
    exc: GenAIChatbotException,
) -> JSONResponse:
    """Handle GenAI Chatbot custom exceptions."""
    
    logger.error(
        f"GenAI Chatbot Exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "details": {},
            },
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    
    from pydantic import ValidationError
    
    if isinstance(exc, ValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(
            f"Validation Exception: {len(errors)} validation error(s)",
            extra={
                "errors": errors,
                "path": request.url.path,
                "method": request.method,
            },
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Input validation failed",
                    "details": {"errors": errors},
                },
                "request_id": getattr(request.state, "request_id", None),
            },
        )
    
    # Fallback to general exception handler
    return await general_exception_handler(request, exc)


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    
    error_id = id(exc)
    
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "error_id": error_id,
            "exception_type": exc.__class__.__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": {
                    "error_id": error_id,
                },
            },
            "request_id": getattr(request.state, "request_id", None),
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI application."""
    
    from pydantic import ValidationError
    
    # Custom exceptions
    app.add_exception_handler(GenAIChatbotException, genai_chatbot_exception_handler)
    
    # FastAPI exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Validation exceptions
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # General exception handler (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured")
