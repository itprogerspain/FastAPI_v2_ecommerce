from collections import defaultdict

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """
    Manages all active WebSocket connections.

    Supports three sending modes:
        - personal  : send to a specific user (all their tabs/devices)
        - room      : send to all users in a named room (e.g. product, chat)
        - broadcast : send to every connected client (flash sales, system messages)

    Room ID naming conventions used across the project:
        order_{order_id}           — order status updates
        product_{product_id}       — real-time stock updates
        chat_{min_uid}_{max_uid}   — buyer ↔ seller chat (sorted user IDs)
        support_{ticket_id}        — support chat

    NOTE: this is an in-memory manager — works correctly on a single server.
    TODO: replace internal dicts with Redis Pub/Sub when scaling to multiple
          server instances (Redis is already available via Celery broker).
    """

    def __init__(self):
        # personal: user_id → set of websockets (one user may have multiple tabs)
        self._personal: dict[int, set[WebSocket]] = defaultdict(set)
        # rooms: room_id → set of websockets
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)
        # all active connections — used for broadcast
        self._all: set[WebSocket] = set()

    # -------------------------
    # Connect / disconnect
    # -------------------------

    async def connect_personal(self, user_id: int, ws: WebSocket) -> None:
        """Accept and register a personal connection for the given user."""
        await ws.accept()
        self._personal[user_id].add(ws)
        self._all.add(ws)
        logger.info(f"WS connected: personal user_id={user_id}")

    async def disconnect_personal(self, user_id: int, ws: WebSocket) -> None:
        """Remove a personal connection. Cleans up empty user entries."""
        self._personal[user_id].discard(ws)
        if not self._personal[user_id]:
            del self._personal[user_id]
        self._all.discard(ws)
        logger.info(f"WS disconnected: personal user_id={user_id}")

    async def connect_room(self, room_id: str, ws: WebSocket) -> None:
        """Accept and register a connection in the given room."""
        await ws.accept()
        self._rooms[room_id].add(ws)
        self._all.add(ws)
        logger.info(f"WS connected: room={room_id}")

    async def disconnect_room(self, room_id: str, ws: WebSocket) -> None:
        """Remove a connection from a room. Cleans up empty room entries."""
        self._rooms[room_id].discard(ws)
        if not self._rooms[room_id]:
            del self._rooms[room_id]
        self._all.discard(ws)
        logger.info(f"WS disconnected: room={room_id}")

    # -------------------------
    # Send methods
    # -------------------------

    async def send_personal(self, user_id: int, message: dict) -> None:
        """
        Send a message to all active connections of a specific user.
        Silently removes broken connections (closed browser tab, lost network).
        """
        for ws in list(self._personal.get(user_id, set())):
            try:
                await ws.send_json(message)
            except Exception:
                # Connection was closed unexpectedly — clean up
                self._personal[user_id].discard(ws)
                self._all.discard(ws)

    async def send_to_room(self, room_id: str, message: dict) -> None:
        """
        Send a message to all connections in a specific room.
        Silently removes broken connections.
        """
        for ws in list(self._rooms.get(room_id, set())):
            try:
                await ws.send_json(message)
            except Exception:
                self._rooms[room_id].discard(ws)
                self._all.discard(ws)

    async def broadcast(self, message: dict) -> None:
        """
        Send a message to ALL connected clients.
        Used for flash sales, system announcements, etc.
        Silently removes broken connections.

        NOTE: expensive at scale — at high user counts consider switching
        to push notifications (Firebase FCM) or SSE for one-directional updates.
        """
        for ws in list(self._all):
            try:
                await ws.send_json(message)
            except Exception:
                self._all.discard(ws)


# Global singleton — one instance shared across all WebSocket endpoints.
# FastAPI runs in a single async event loop, so this is safe without locks.
manager = ConnectionManager()
