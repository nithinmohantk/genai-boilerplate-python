"""
Chat API endpoints for session management and messaging.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, CurrentUser
from database.session import get_db
from models.chat import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate, ChatSessionWithMessages,
    ChatMessageResponse, ChatCompletionRequest, ChatCompletionResponse,
    SessionStatus, MessageType
)
from services.chat_service import ChatService
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session."""
    try:
        chat_service = ChatService(db)
        
        session = await chat_service.create_session(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            title=session_data.title,
            model_config=session_data.model_config,
            system_prompt=session_data.system_prompt,
            context_window=session_data.context_window
        )
        
        logger.info(f"Created chat session {session.id} for user {current_user.user_id}")
        
        return ChatSessionResponse.from_orm(session)
    
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[SessionStatus] = Query(None, alias="status")
):
    """Get user's chat sessions."""
    try:
        chat_service = ChatService(db)
        
        sessions = await chat_service.get_user_sessions(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            limit=limit,
            offset=offset,
            status=status_filter
        )
        
        return [ChatSessionResponse.from_orm(session) for session in sessions]
    
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat sessions"
        )


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    include_messages: bool = Query(True)
):
    """Get a specific chat session with optional messages."""
    try:
        chat_service = ChatService(db)
        
        session = await chat_service.get_session(
            session_id=session_id,
            user_id=current_user.user_id,
            include_messages=include_messages
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages separately for better control
        messages = []
        if include_messages:
            messages = await chat_service.get_session_messages(
                session_id=session_id,
                user_id=current_user.user_id
            )
        
        session_dict = ChatSessionResponse.from_orm(session).dict()
        session_dict["messages"] = [ChatMessageResponse.from_orm(msg) for msg in messages]
        
        return ChatSessionWithMessages(**session_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat session"
        )


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: UUID,
    session_updates: ChatSessionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a chat session."""
    try:
        chat_service = ChatService(db)
        
        session = await chat_service.update_session(
            session_id=session_id,
            user_id=current_user.user_id,
            updates=session_updates.dict(exclude_unset=True)
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        logger.info(f"Updated chat session {session_id}")
        
        return ChatSessionResponse.from_orm(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat session"
        )


@router.post("/sessions/{session_id}/archive")
async def archive_chat_session(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive a chat session."""
    try:
        chat_service = ChatService(db)
        
        success = await chat_service.archive_session(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        logger.info(f"Archived chat session {session_id}")
        
        return {"message": "Chat session archived successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive chat session"
        )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session (soft delete)."""
    try:
        chat_service = ChatService(db)
        
        success = await chat_service.delete_session(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        logger.info(f"Deleted chat session {session_id}")
        
        return {"message": "Chat session deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    before_message_id: Optional[UUID] = Query(None)
):
    """Get messages for a chat session with pagination."""
    try:
        chat_service = ChatService(db)
        
        messages = await chat_service.get_session_messages(
            session_id=session_id,
            user_id=current_user.user_id,
            limit=limit,
            before_message_id=before_message_id
        )
        
        return [ChatMessageResponse.from_orm(msg) for msg in messages]
    
    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session messages"
        )


@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    completion_request: ChatCompletionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a chat completion (create user message and AI response)."""
    try:
        from datetime import datetime
        from models.chat import ChatMessage
        
        chat_service = ChatService(db)
        
        # Get or create session
        if completion_request.session_id:
            session = await chat_service.get_session(
                session_id=completion_request.session_id,
                user_id=current_user.user_id
            )
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found"
                )
        else:
            # Create new session
            session = await chat_service.create_session(
                user_id=current_user.user_id,
                tenant_id=current_user.tenant_id,
                model_config=completion_request.model_config
            )
        
        # Create user message
        user_message = ChatMessage(
            session_id=session.id,
            user_id=current_user.user_id,
            message=completion_request.message,
            message_type=MessageType.USER,
            timestamp=datetime.now()
        )
        
        # Save user message
        user_message = await chat_service.save_message(user_message)
        
        # Broadcast user message via WebSocket
        await websocket_manager.broadcast_chat_message({
            "id": str(user_message.id),
            "session_id": str(session.id),
            "user_id": str(current_user.user_id),
            "message": completion_request.message,
            "message_type": "user",
            "timestamp": user_message.timestamp.isoformat()
        }, str(session.id))
        
        # Generate AI response
        ai_response = await chat_service.generate_response(
            message=completion_request.message,
            session_id=session.id,
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            model_config=completion_request.model_config,
            include_documents=completion_request.include_documents
        )
        
        if not ai_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate AI response"
            )
        
        # Create AI message
        ai_message = ChatMessage(
            session_id=session.id,
            user_id=None,  # AI assistant has no user_id
            message=ai_response,
            message_type=MessageType.ASSISTANT,
            timestamp=datetime.now(),
            metadata={"model": "default", "tenant_id": str(current_user.tenant_id)}
        )
        
        # Save AI message
        ai_message = await chat_service.save_message(ai_message)
        
        # Broadcast AI message via WebSocket
        await websocket_manager.broadcast_chat_message({
            "id": str(ai_message.id),
            "session_id": str(session.id),
            "user_id": None,
            "message": ai_response,
            "message_type": "assistant",
            "timestamp": ai_message.timestamp.isoformat(),
            "metadata": ai_message.metadata
        }, str(session.id))
        
        logger.info(f"Generated chat completion for session {session.id}")
        
        return ChatCompletionResponse(
            session_id=session.id,
            user_message_id=user_message.id,
            assistant_message_id=ai_message.id,
            response=ai_response,
            tokens_used=ai_message.tokens_used,
            processing_time_ms=ai_message.processing_time_ms,
            model_info=ai_message.metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat completion"
        )


@router.get("/stats")
async def get_chat_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's chat statistics."""
    try:
        chat_service = ChatService(db)
        
        stats = await chat_service.get_session_stats(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id
        )
        
        return {
            "status": "success",
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat statistics"
        )


@router.get("/search")
async def search_chat_sessions(
    q: str = Query(..., min_length=1, max_length=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=50)
):
    """Search user's chat sessions."""
    try:
        chat_service = ChatService(db)
        
        sessions = await chat_service.search_sessions(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            query=q,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "query": q,
                "results": [ChatSessionResponse.from_orm(session) for session in sessions],
                "total": len(sessions)
            }
        }
    
    except Exception as e:
        logger.error(f"Error searching chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search chat sessions"
        )


@router.get("/models")
async def get_available_models(
    current_user: CurrentUser = Depends(get_current_user),
    provider: str = Query("openai", regex="^(openai|anthropic|google)$")
):
    """Get available AI models for a provider."""
    try:
        from core.genai_client import genai_client
        
        models = await genai_client.get_available_models(provider)
        
        return {
            "status": "success",
            "data": {
                "provider": provider,
                "models": models
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )
