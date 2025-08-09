"""
WebSocket connection manager for real-time chat functionality.
Handles WebSocket connections, message broadcasting, and connection state management.
"""

import json
import logging
from typing import Dict, List, Set
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str  # 'chat', 'typing', 'status', 'error'
    data: dict
    timestamp: str
    session_id: str
    user_id: str


class ConnectionInfo(BaseModel):
    """WebSocket connection information."""
    connection_id: str
    user_id: str
    tenant_id: str
    session_id: str
    websocket: WebSocket


class WebSocketManager:
    """Manages WebSocket connections for real-time chat."""

    def __init__(self):
        # Active connections: {connection_id: ConnectionInfo}
        self.connections: Dict[str, ConnectionInfo] = {}
        
        # User to connections mapping: {user_id: {connection_id}}
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Session to connections mapping: {session_id: {connection_id}}
        self.session_connections: Dict[str, Set[str]] = {}
        
        # Tenant to connections mapping: {tenant_id: {connection_id}}
        self.tenant_connections: Dict[str, Set[str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        tenant_id: str,
        session_id: str
    ) -> str:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        connection_id = str(uuid4())
        connection_info = ConnectionInfo(
            connection_id=connection_id,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            websocket=websocket
        )
        
        # Store connection
        self.connections[connection_id] = connection_info
        
        # Update mappings
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        if tenant_id not in self.tenant_connections:
            self.tenant_connections[tenant_id] = set()
        self.tenant_connections[tenant_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} (user: {user_id}, tenant: {tenant_id})")
        
        # Send connection success message
        await self.send_personal_message({
            "type": "connection",
            "data": {
                "status": "connected",
                "connection_id": connection_id,
                "message": "Successfully connected to chat"
            }
        }, connection_id)
        
        return connection_id

    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection."""
        if connection_id not in self.connections:
            return
        
        connection_info = self.connections[connection_id]
        user_id = connection_info.user_id
        tenant_id = connection_info.tenant_id
        session_id = connection_info.session_id
        
        # Remove from mappings
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        if tenant_id in self.tenant_connections:
            self.tenant_connections[tenant_id].discard(connection_id)
            if not self.tenant_connections[tenant_id]:
                del self.tenant_connections[tenant_id]
        
        # Remove connection
        del self.connections[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id} (user: {user_id}, tenant: {tenant_id})")

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to a specific connection."""
        if connection_id not in self.connections:
            logger.warning(f"Connection {connection_id} not found")
            return
        
        connection_info = self.connections[connection_id]
        try:
            await connection_info.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self.disconnect(connection_id)

    async def send_message_to_user(self, message: dict, user_id: str):
        """Send message to all connections of a specific user."""
        if user_id not in self.user_connections:
            logger.warning(f"No connections found for user {user_id}")
            return
        
        connection_ids = list(self.user_connections[user_id])
        for connection_id in connection_ids:
            await self.send_personal_message(message, connection_id)

    async def send_message_to_session(self, message: dict, session_id: str):
        """Send message to all connections in a chat session."""
        if session_id not in self.session_connections:
            logger.warning(f"No connections found for session {session_id}")
            return
        
        connection_ids = list(self.session_connections[session_id])
        for connection_id in connection_ids:
            await self.send_personal_message(message, connection_id)

    async def send_message_to_tenant(self, message: dict, tenant_id: str):
        """Send message to all connections in a tenant."""
        if tenant_id not in self.tenant_connections:
            logger.warning(f"No connections found for tenant {tenant_id}")
            return
        
        connection_ids = list(self.tenant_connections[tenant_id])
        for connection_id in connection_ids:
            await self.send_personal_message(message, connection_id)

    async def broadcast_typing_indicator(
        self,
        user_id: str,
        session_id: str,
        is_typing: bool
    ):
        """Broadcast typing indicator to session participants."""
        message = {
            "type": "typing",
            "data": {
                "user_id": user_id,
                "is_typing": is_typing,
                "session_id": session_id
            }
        }
        
        # Send to all session participants except the sender
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id]:
                connection_info = self.connections.get(connection_id)
                if connection_info and connection_info.user_id != user_id:
                    await self.send_personal_message(message, connection_id)

    async def broadcast_chat_message(self, message: dict, session_id: str):
        """Broadcast chat message to all session participants."""
        chat_message = {
            "type": "message",
            "data": message
        }
        await self.send_message_to_session(chat_message, session_id)

    async def send_error_message(self, connection_id: str, error: str, error_code: str = "GENERAL_ERROR"):
        """Send error message to a specific connection."""
        error_message = {
            "type": "error",
            "data": {
                "error": error,
                "error_code": error_code
            }
        }
        await self.send_personal_message(error_message, connection_id)

    async def get_connection_stats(self) -> dict:
        """Get current connection statistics."""
        return {
            "total_connections": len(self.connections),
            "active_users": len(self.user_connections),
            "active_sessions": len(self.session_connections),
            "active_tenants": len(self.tenant_connections),
            "connections_by_tenant": {
                tenant_id: len(connections) 
                for tenant_id, connections in self.tenant_connections.items()
            }
        }

    def get_user_connections(self, user_id: str) -> List[str]:
        """Get all connection IDs for a user."""
        return list(self.user_connections.get(user_id, set()))

    def get_session_connections(self, session_id: str) -> List[str]:
        """Get all connection IDs for a session."""
        return list(self.session_connections.get(session_id, set()))

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user has any active connections."""
        return user_id in self.user_connections and bool(self.user_connections[user_id])


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
