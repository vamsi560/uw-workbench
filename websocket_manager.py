import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            await self.disconnect(websocket)
    
    async def broadcast_workitem(self, workitem_data: Dict[str, Any]):
        """Broadcast a new work item to all connected clients"""
        if not self.active_connections:
            logger.info("No active WebSocket connections to broadcast to")
            return
        
        # Create the broadcast message
        message = {
            "event": "new_workitem",
            "data": workitem_data
        }
        
        message_json = json.dumps(message)
        logger.info(f"Broadcasting work item to {len(self.active_connections)} connections")
        
        # Send to all active connections
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {str(e)}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for dead_connection in dead_connections:
            await self.disconnect(dead_connection)
    
    async def broadcast_status_update(self, submission_ref: str, new_status: str):
        """Broadcast a status update for a work item"""
        if not self.active_connections:
            return
        
        message = {
            "event": "status_update",
            "data": {
                "submission_ref": submission_ref,
                "status": new_status,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        message_json = json.dumps(message)
        logger.info(f"Broadcasting status update for {submission_ref} to {len(self.active_connections)} connections")
        
        # Send to all active connections
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting status update: {str(e)}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for dead_connection in dead_connections:
            await self.disconnect(dead_connection)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
