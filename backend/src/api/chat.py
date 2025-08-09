"""
Chat API endpoints for session management and messaging.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, get_current_user
from database.session import get_db
from models.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionUpdate,
    ChatSessionWithMessages,
    MessageType,
    SessionStatus,
)
from services.chat_service import ChatService
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
            context_window=session_data.context_window,
        )

        logger.info(
            f"Created chat session {session.id} for user {current_user.user_id}"
        )

        return ChatSessionResponse.from_orm(session)

    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session",
        ) from e


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def get_chat_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: SessionStatus | None = Query(None, alias="status"),
):
    """Get user's chat sessions."""
    try:
        chat_service = ChatService(db)

        sessions = await chat_service.get_user_sessions(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            limit=limit,
            offset=offset,
            status=status_filter,
        )

        return [ChatSessionResponse.from_orm(session) for session in sessions]

    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat sessions",
        ) from e


@router.get("/sessions/paginated")
async def get_chat_sessions_paginated(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: SessionStatus | None = Query(None, alias="status"),
    include_message_count: bool = Query(True),
):
    """Get user's chat sessions with optimized pagination for large datasets."""
    try:
        chat_service = ChatService(db)

        sessions, total_count = await chat_service.get_user_sessions_paginated(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            include_message_count=include_message_count,
        )

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "status": "success",
            "data": {
                "sessions": sessions,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            },
        }

    except Exception as e:
        logger.error(f"Error getting paginated chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get paginated chat sessions",
        ) from e


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    include_messages: bool = Query(True),
):
    """Get a specific chat session with optional messages."""
    try:
        chat_service = ChatService(db)

        session = await chat_service.get_session(
            session_id=session_id,
            user_id=current_user.user_id,
            include_messages=include_messages,
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        # Get messages separately for better control
        messages = []
        if include_messages:
            messages = await chat_service.get_session_messages(
                session_id=session_id, user_id=current_user.user_id
            )

        session_dict = ChatSessionResponse.from_orm(session).dict()
        session_dict["messages"] = [
            ChatMessageResponse.from_orm(msg) for msg in messages
        ]

        return ChatSessionWithMessages(**session_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat session",
        ) from e


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: UUID,
    session_updates: ChatSessionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a chat session."""
    try:
        chat_service = ChatService(db)

        session = await chat_service.update_session(
            session_id=session_id,
            user_id=current_user.user_id,
            updates=session_updates.dict(exclude_unset=True),
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        logger.info(f"Updated chat session {session_id}")

        return ChatSessionResponse.from_orm(session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat session",
        ) from e


@router.post("/sessions/{session_id}/archive")
async def archive_chat_session(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Archive a chat session."""
    try:
        chat_service = ChatService(db)

        success = await chat_service.archive_session(
            session_id=session_id, user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        logger.info(f"Archived chat session {session_id}")

        return {"message": "Chat session archived successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive chat session",
        ) from e


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session (soft delete)."""
    try:
        chat_service = ChatService(db)

        success = await chat_service.delete_session(
            session_id=session_id, user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        logger.info(f"Deleted chat session {session_id}")

        return {"message": "Chat session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session",
        ) from e


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_session_messages(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    before_message_id: UUID | None = Query(None),
):
    """Get messages for a chat session with pagination."""
    try:
        chat_service = ChatService(db)

        messages = await chat_service.get_session_messages(
            session_id=session_id,
            user_id=current_user.user_id,
            limit=limit,
            before_message_id=before_message_id,
        )

        return [ChatMessageResponse.from_orm(msg) for msg in messages]

    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session messages",
        ) from e


@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    completion_request: ChatCompletionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a chat completion (create user message and AI response)."""
    try:
        from datetime import datetime

        from models.chat import ChatMessage

        chat_service = ChatService(db)

        # Get or create session
        if completion_request.session_id:
            session = await chat_service.get_session(
                session_id=completion_request.session_id, user_id=current_user.user_id
            )
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found",
                )
        else:
            # Create new session
            session = await chat_service.create_session(
                user_id=current_user.user_id,
                tenant_id=current_user.tenant_id,
                model_config=completion_request.model_config,
            )

        # Create user message
        user_message = ChatMessage(
            session_id=session.id,
            user_id=current_user.user_id,
            message=completion_request.message,
            message_type=MessageType.USER,
            timestamp=datetime.now(),
        )

        # Save user message
        user_message = await chat_service.save_message(user_message)

        # Broadcast user message via WebSocket
        await websocket_manager.broadcast_chat_message(
            {
                "id": str(user_message.id),
                "session_id": str(session.id),
                "user_id": str(current_user.user_id),
                "message": completion_request.message,
                "message_type": "user",
                "timestamp": user_message.timestamp.isoformat(),
            },
            str(session.id),
        )

        # Generate AI response
        ai_response = await chat_service.generate_response(
            message=completion_request.message,
            session_id=session.id,
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            model_config=completion_request.model_config,
            include_documents=completion_request.include_documents,
        )

        if not ai_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate AI response",
            )

        # Create AI message
        ai_message = ChatMessage(
            session_id=session.id,
            user_id=None,  # AI assistant has no user_id
            message=ai_response,
            message_type=MessageType.ASSISTANT,
            timestamp=datetime.now(),
            metadata={"model": "default", "tenant_id": str(current_user.tenant_id)},
        )

        # Save AI message
        ai_message = await chat_service.save_message(ai_message)

        # Broadcast AI message via WebSocket
        await websocket_manager.broadcast_chat_message(
            {
                "id": str(ai_message.id),
                "session_id": str(session.id),
                "user_id": None,
                "message": ai_response,
                "message_type": "assistant",
                "timestamp": ai_message.timestamp.isoformat(),
                "metadata": ai_message.metadata,
            },
            str(session.id),
        )

        logger.info(f"Generated chat completion for session {session.id}")

        return ChatCompletionResponse(
            session_id=session.id,
            user_message_id=user_message.id,
            assistant_message_id=ai_message.id,
            response=ai_response,
            tokens_used=ai_message.tokens_used,
            processing_time_ms=ai_message.processing_time_ms,
            model_info=ai_message.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat completion",
        ) from e


@router.get("/stats")
async def get_chat_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's chat statistics."""
    try:
        chat_service = ChatService(db)

        stats = await chat_service.get_session_stats(
            user_id=current_user.user_id, tenant_id=current_user.tenant_id
        )

        return {"status": "success", "data": stats}

    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat statistics",
        ) from e


@router.get("/search")
async def search_chat_sessions(
    q: str = Query(..., min_length=1, max_length=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=50),
):
    """Search user's chat sessions."""
    try:
        chat_service = ChatService(db)

        sessions = await chat_service.search_sessions(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            query=q,
            limit=limit,
        )

        return {
            "status": "success",
            "data": {
                "query": q,
                "results": [
                    ChatSessionResponse.from_orm(session) for session in sessions
                ],
                "total": len(sessions),
            },
        }

    except Exception as e:
        logger.error(f"Error searching chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search chat sessions",
        ) from e


@router.get("/sessions/{session_id}/messages/optimized")
async def get_session_messages_optimized(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    cursor_timestamp: str | None = Query(None),
):
    """Get session messages with optimized cursor-based pagination."""
    try:
        from datetime import datetime

        chat_service = ChatService(db)

        # Parse cursor timestamp if provided
        cursor_dt = None
        if cursor_timestamp:
            try:
                cursor_dt = datetime.fromisoformat(
                    cursor_timestamp.replace("Z", "+00:00")
                )
            except ValueError as ve:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid cursor timestamp format",
                ) from ve

        messages, has_more = await chat_service.get_session_messages_optimized(
            session_id=session_id,
            user_id=current_user.user_id,
            page=page,
            page_size=page_size,
            cursor_timestamp=cursor_dt,
        )

        # Prepare next cursor
        next_cursor = None
        if has_more and messages:
            next_cursor = messages[-1].timestamp.isoformat()

        return {
            "status": "success",
            "data": {
                "messages": [ChatMessageResponse.from_orm(msg) for msg in messages],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "has_more": has_more,
                    "next_cursor": next_cursor,
                },
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting optimized session messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session messages",
        ) from e


@router.get("/sessions/{session_id}/preview")
async def get_session_preview(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a lightweight session preview with last message."""
    try:
        chat_service = ChatService(db)

        preview = await chat_service.get_session_preview(
            session_id=session_id, user_id=current_user.user_id
        )

        if not preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        return {"status": "success", "data": preview}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session preview",
        ) from e


@router.post("/sessions/bulk/archive")
async def bulk_archive_sessions(
    session_ids: list[UUID],
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk archive multiple chat sessions."""
    try:
        if not session_ids or len(session_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide 1-100 session IDs",
            )

        chat_service = ChatService(db)

        archived_count = await chat_service.bulk_archive_sessions(
            session_ids=session_ids, user_id=current_user.user_id
        )

        logger.info(
            f"Bulk archived {archived_count} sessions for user {current_user.user_id}"
        )

        return {
            "status": "success",
            "data": {
                "requested_count": len(session_ids),
                "archived_count": archived_count,
                "message": f"Successfully archived {archived_count} sessions",
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk archiving sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk archive sessions",
        ) from e


@router.post("/cleanup")
async def cleanup_old_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days_old: int = Query(90, ge=1, le=365),
    max_sessions: int = Query(1000, ge=1, le=5000),
):
    """Clean up old sessions for better performance."""
    try:
        chat_service = ChatService(db)

        cleaned_count = await chat_service.cleanup_old_sessions(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            days_old=days_old,
            max_sessions=max_sessions,
        )

        logger.info(
            f"Cleaned up {cleaned_count} sessions for user {current_user.user_id}"
        )

        return {
            "status": "success",
            "data": {
                "cleaned_count": cleaned_count,
                "days_old": days_old,
                "message": f"Cleaned up {cleaned_count} sessions older than {days_old} days",
            },
        }

    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clean up sessions",
        ) from e


@router.post("/completions/with-files", response_model=ChatCompletionResponse)
async def create_chat_completion_with_files(
    message: str,
    files: list[UploadFile],
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    session_id: UUID | None = None,
    stream: bool = False,
    process_uploaded_files: bool = True,
    include_documents: bool = True,
):
    """Generate a chat completion with file uploads support."""
    try:
        from datetime import datetime

        from models.chat import ChatMessage
        from services.document_service import DocumentService

        if len(files) > 10:  # Limit file uploads
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per message",
            )

        chat_service = ChatService(db)
        doc_service = DocumentService(db)

        # Get or create session
        if session_id:
            session = await chat_service.get_session(
                session_id=session_id, user_id=current_user.user_id
            )
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found",
                )
        else:
            # Create new session
            session = await chat_service.create_session(
                user_id=current_user.user_id,
                tenant_id=current_user.tenant_id,
                title=f"Chat with {len(files)} file(s)",
            )

        uploaded_documents = []

        # Process uploaded files
        for file in files:
            try:
                # Upload document to session
                document = await doc_service.upload_document(
                    file=file,
                    user_id=current_user.user_id,
                    tenant_id=current_user.tenant_id,
                    session_id=session.id,
                )
                uploaded_documents.append(document)

                # Auto-process for RAG if enabled
                if process_uploaded_files:
                    await doc_service.process_document(document.id)

                logger.info(
                    f"Uploaded and processed document {document.id} to session {session.id}"
                )

            except Exception as e:
                logger.error(f"Error processing uploaded file {file.filename}: {e}")
                # Continue with other files

        # Create user message with file references
        file_info = [
            {"filename": doc.filename, "id": str(doc.id), "processed": doc.processed}
            for doc in uploaded_documents
        ]

        user_message = ChatMessage(
            session_id=session.id,
            user_id=current_user.user_id,
            message=message,
            message_type=MessageType.USER,
            timestamp=datetime.now(),
            metadata={
                "uploaded_files": file_info,
                "file_count": len(uploaded_documents),
            },
        )

        # Save user message
        user_message = await chat_service.save_message(user_message)

        # Broadcast user message via WebSocket with file info
        await websocket_manager.broadcast_chat_message(
            {
                "id": str(user_message.id),
                "session_id": str(session.id),
                "user_id": str(current_user.user_id),
                "message": message,
                "message_type": "user",
                "timestamp": user_message.timestamp.isoformat(),
                "uploaded_files": file_info,
            },
            str(session.id),
        )

        # Generate AI response (will include uploaded documents in context)
        ai_response = await chat_service.generate_response(
            message=message,
            session_id=session.id,
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            include_documents=include_documents,
        )

        if not ai_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate AI response",
            )

        # Create AI message
        ai_message = ChatMessage(
            session_id=session.id,
            user_id=None,  # AI assistant has no user_id
            message=ai_response,
            message_type=MessageType.ASSISTANT,
            timestamp=datetime.now(),
            metadata={
                "model": "default",
                "tenant_id": str(current_user.tenant_id),
                "used_documents": len(uploaded_documents) if include_documents else 0,
            },
        )

        # Save AI message
        ai_message = await chat_service.save_message(ai_message)

        # Broadcast AI message via WebSocket
        await websocket_manager.broadcast_chat_message(
            {
                "id": str(ai_message.id),
                "session_id": str(session.id),
                "user_id": None,
                "message": ai_response,
                "message_type": "assistant",
                "timestamp": ai_message.timestamp.isoformat(),
                "metadata": ai_message.metadata,
            },
            str(session.id),
        )

        logger.info(
            f"Generated chat completion with {len(uploaded_documents)} files for session {session.id}"
        )

        return ChatCompletionResponse(
            session_id=session.id,
            user_message_id=user_message.id,
            assistant_message_id=ai_message.id,
            response=ai_response,
            tokens_used=ai_message.tokens_used,
            processing_time_ms=ai_message.processing_time_ms,
            model_info=ai_message.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chat completion with files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat completion with files",
        ) from e


@router.get("/sessions/{session_id}/documents")
async def get_session_documents(
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get documents uploaded to a specific chat session."""
    try:
        from services.document_service import DocumentService

        # Verify session access
        chat_service = ChatService(db)
        session = await chat_service.get_session(
            session_id=session_id, user_id=current_user.user_id
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        # Get session documents
        doc_service = DocumentService(db)
        documents = await doc_service.get_user_documents(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            session_id=session_id,
        )

        return {
            "status": "success",
            "data": {
                "session_id": str(session_id),
                "documents": [
                    {
                        "id": str(doc.id),
                        "filename": doc.filename,
                        "content_type": doc.content_type,
                        "file_size": doc.file_size,
                        "processed": doc.processed,
                        "chunks_count": doc.chunks_count,
                        "uploaded_at": doc.uploaded_at.isoformat(),
                        "processed_at": (
                            doc.processed_at.isoformat() if doc.processed_at else None
                        ),
                    }
                    for doc in documents
                ],
                "total_documents": len(documents),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session documents",
        ) from e


@router.delete("/sessions/{session_id}/documents/{document_id}")
async def remove_document_from_session(
    session_id: UUID,
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a document from a chat session."""
    try:
        from services.document_service import DocumentService

        # Verify session access
        chat_service = ChatService(db)
        session = await chat_service.get_session(
            session_id=session_id, user_id=current_user.user_id
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )

        # Delete document (will also remove from session)
        doc_service = DocumentService(db)
        success = await doc_service.delete_document(
            document_id=document_id, user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        logger.info(f"Removed document {document_id} from session {session_id}")

        return {
            "status": "success",
            "message": "Document removed from session successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing document from session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove document from session",
        ) from e


@router.get("/models")
async def get_available_models(
    current_user: CurrentUser = Depends(get_current_user),
    provider: str = Query("openai", regex="^(openai|anthropic|google)$"),
):
    """Get available AI models for a provider."""
    try:
        from core.genai_client import genai_client

        models = await genai_client.get_available_models(provider)

        return {"status": "success", "data": {"provider": provider, "models": models}}

    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models",
        ) from e
