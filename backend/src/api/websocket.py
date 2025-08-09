"""
WebSocket API endpoints for real-time chat functionality.
"""

import json
import logging
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)

from database.session import get_db
from models.chat import ChatMessage
from services.chat_service import ChatService
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_websocket_user_info(websocket: WebSocket, token: str = Query(...)):
    """
    Extract user information from WebSocket connection.
    This is a placeholder - will be implemented with proper auth.
    """
    # TODO: Implement proper token validation
    # For now, return mock data
    return {
        "user_id": "user_123",
        "tenant_id": "tenant_default",
        "username": "testuser",
    }


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, session_id: str, token: str = Query(...), db=Depends(get_db)
):
    """WebSocket endpoint for real-time chat."""
    connection_id = None

    try:
        # Get user info from token
        user_info = await get_websocket_user_info(websocket, token)
        user_id = user_info["user_id"]
        tenant_id = user_info["tenant_id"]

        # Connect to WebSocket manager
        connection_id = await websocket_manager.connect(
            websocket=websocket,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
        )

        # Initialize chat service
        chat_service = ChatService(db)

        logger.info(f"WebSocket connected for session {session_id}, user {user_id}")

        while True:
            # Wait for message from client
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")

                if message_type == "chat":
                    await handle_chat_message(
                        chat_service, message_data, user_id, tenant_id, session_id
                    )

                elif message_type == "typing":
                    await handle_typing_indicator(message_data, user_id, session_id)

                elif message_type == "ping":
                    await websocket_manager.send_personal_message(
                        {
                            "type": "pong",
                            "data": {"timestamp": datetime.now().isoformat()},
                        },
                        connection_id,
                    )

                else:
                    await websocket_manager.send_error_message(
                        connection_id,
                        f"Unknown message type: {message_type}",
                        "INVALID_MESSAGE_TYPE",
                    )

            except json.JSONDecodeError:
                await websocket_manager.send_error_message(
                    connection_id, "Invalid JSON format", "INVALID_JSON"
                )

            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket_manager.send_error_message(
                    connection_id, "Internal server error", "SERVER_ERROR"
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if connection_id:
            await websocket_manager.send_error_message(
                connection_id, "Connection error occurred", "CONNECTION_ERROR"
            )

    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id)


async def handle_chat_message(
    chat_service: ChatService,
    message_data: dict,
    user_id: str,
    tenant_id: str,
    session_id: str,
):
    """Handle incoming chat message."""
    try:
        message_content = message_data.get("data", {}).get("message", "")
        if not message_content.strip():
            return

        # Create chat message
        chat_message = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            message=message_content,
            message_type="user",
            timestamp=datetime.now(),
            metadata=message_data.get("data", {}).get("metadata", {}),
        )

        # Store message in database
        stored_message = await chat_service.save_message(chat_message)

        # Broadcast user message to session participants
        await websocket_manager.broadcast_chat_message(
            {
                "id": str(stored_message.id),
                "session_id": session_id,
                "user_id": user_id,
                "message": message_content,
                "message_type": "user",
                "timestamp": stored_message.timestamp.isoformat(),
                "metadata": stored_message.metadata,
            },
            session_id,
        )

        # Generate AI response
        ai_response = await chat_service.generate_response(
            message_content, session_id, user_id, tenant_id
        )

        if ai_response:
            # Create AI message
            ai_message = ChatMessage(
                session_id=session_id,
                user_id="assistant",  # Special user ID for AI
                message=ai_response,
                message_type="assistant",
                timestamp=datetime.now(),
                metadata={"model": "default", "tenant_id": tenant_id},
            )

            # Store AI message
            stored_ai_message = await chat_service.save_message(ai_message)

            # Broadcast AI response
            await websocket_manager.broadcast_chat_message(
                {
                    "id": str(stored_ai_message.id),
                    "session_id": session_id,
                    "user_id": "assistant",
                    "message": ai_response,
                    "message_type": "assistant",
                    "timestamp": stored_ai_message.timestamp.isoformat(),
                    "metadata": stored_ai_message.metadata,
                },
                session_id,
            )

    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        # Send error to all session participants
        error_message = {
            "type": "error",
            "data": {
                "error": "Failed to process message",
                "error_code": "MESSAGE_PROCESSING_ERROR",
            },
        }
        await websocket_manager.send_message_to_session(error_message, session_id)


async def handle_typing_indicator(message_data: dict, user_id: str, session_id: str):
    """Handle typing indicator."""
    try:
        is_typing = message_data.get("data", {}).get("is_typing", False)

        await websocket_manager.broadcast_typing_indicator(
            user_id=user_id, session_id=session_id, is_typing=is_typing
        )

    except Exception as e:
        logger.error(f"Error handling typing indicator: {e}")


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    try:
        stats = await websocket_manager.get_connection_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get WebSocket statistics"
        )


@router.get("/ws/sessions/{session_id}/participants")
async def get_session_participants(session_id: str):
    """Get active participants in a chat session."""
    try:
        connection_ids = websocket_manager.get_session_connections(session_id)
        participants = []

        for conn_id in connection_ids:
            if conn_id in websocket_manager.connections:
                conn_info = websocket_manager.connections[conn_id]
                participants.append(
                    {
                        "user_id": conn_info.user_id,
                        "connection_id": conn_id,
                        "tenant_id": conn_info.tenant_id,
                    }
                )

        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "participant_count": len(participants),
                "participants": participants,
            },
        }

    except Exception as e:
        logger.error(f"Error getting session participants: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get session participants"
        )


@router.post("/ws/sessions/{session_id}/broadcast")
async def broadcast_to_session(session_id: str, message: dict):
    """Broadcast a message to all participants in a session."""
    try:
        await websocket_manager.send_message_to_session(message, session_id)

        return {
            "status": "success",
            "data": {
                "message": "Message broadcasted successfully",
                "session_id": session_id,
            },
        }

    except Exception as e:
        logger.error(f"Error broadcasting to session: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")


@router.delete("/ws/connections/{connection_id}")
async def disconnect_connection(connection_id: str):
    """Forcefully disconnect a WebSocket connection."""
    try:
        await websocket_manager.disconnect(connection_id)

        return {
            "status": "success",
            "data": {
                "message": "Connection disconnected successfully",
                "connection_id": connection_id,
            },
        }

    except Exception as e:
        logger.error(f"Error disconnecting connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to disconnect connection")
