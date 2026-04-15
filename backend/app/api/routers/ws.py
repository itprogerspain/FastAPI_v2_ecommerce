import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SECRET_KEY, ALGORITHM
from app.core.ws_manager import manager
from app.infrastructure.db import async_session_maker
from app.infrastructure.repositories.user import UserRepository
from app.models.db.user import User as UserModel

router = APIRouter(
    prefix="/ws",
    tags=["websockets"],
)


# -------------------------
# WS authentication helper
# -------------------------

async def _authenticate(token: str) -> UserModel | None:
    """
    Validate a JWT access token passed as a query parameter.

    WebSocket connections cannot send Authorization headers,
    so the token is passed via ?token=<jwt> in the URL.

    Returns the authenticated user or None if the token is invalid/expired.

    TODO: for higher security, accept the token in the first WS message
          instead of the URL (prevents token from appearing in server logs).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if not email or token_type != "access":
            return None
    except jwt.PyJWTError:
        return None

    async with async_session_maker() as db:
        return await UserRepository(db).get_active_by_email(email)


# -------------------------
# Personal notification endpoints
# -------------------------

@router.websocket("/orders/{order_id}")
async def order_status_ws(
    ws: WebSocket,
    order_id: int,
    token: str = Query(...),
):
    """
    Personal WebSocket: sends real-time order status updates to the buyer.

    Client connects to: ws://host/api/v1/ws/orders/{order_id}?token=<jwt>
    Server pushes: {"event": "order_status", "order_id": ..., "status": "..."}

    Integration point: call from orders service when status changes —
        await manager.send_personal(user_id, {"event": "order_status", ...})
    """
    user = await _authenticate(token)
    if not user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    await manager.connect_personal(user.id, ws)
    try:
        while True:
            # Keep connection alive — client may send heartbeat pings
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_personal(user.id, ws)


@router.websocket("/notifications")
async def seller_notifications_ws(
    ws: WebSocket,
    token: str = Query(...),
):
    """
    Personal WebSocket: real-time notifications for sellers.
    Sends alerts when a new order is placed for their products.

    Client connects to: ws://host/api/v1/ws/notifications?token=<jwt>
    Server pushes: {"event": "new_order", "order_id": ..., "total": "..."}

    Integration point: call from orders service when order is created —
        await manager.send_personal(seller_id, {"event": "new_order", ...})
    """
    user = await _authenticate(token)
    if not user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    await manager.connect_personal(user.id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_personal(user.id, ws)


# -------------------------
# Room endpoints
# -------------------------

@router.websocket("/products/{product_id}/stock")
async def product_stock_ws(
    ws: WebSocket,
    product_id: int,
):
    """
    Public room WebSocket: sends real-time stock updates for a product.
    No authentication required — any visitor can subscribe.

    Room ID: product_{product_id}
    Client connects to: ws://host/api/v1/ws/products/{product_id}/stock
    Server pushes: {"event": "stock_update", "product_id": ..., "stock": ...}

    Integration point: call from products service when stock changes —
        await manager.send_to_room(f"product_{product_id}", {"event": "stock_update", ...})
    """
    room_id = f"product_{product_id}"
    await manager.connect_room(room_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_room(room_id, ws)


@router.websocket("/chat/{other_user_id}")
async def chat_ws(
    ws: WebSocket,
    other_user_id: int,
    token: str = Query(...),
):
    """
    Room WebSocket: real-time chat between buyer and seller.

    Room ID is built from sorted user IDs to ensure both sides
    connect to the same room regardless of who initiates:
        chat_12_45  (user 12 and user 45 always get the same room)

    Client connects to: ws://host/api/v1/ws/chat/{other_user_id}?token=<jwt>
    Messages format: {"event": "message", "from_id": ..., "text": "..."}

    TODO: persist messages to DB via ChatService (model + service not yet created).
    """
    user = await _authenticate(token)
    if not user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    # Sort IDs so both users join the same room
    room_id = "chat_{}_{}".format(*sorted([user.id, other_user_id]))
    await manager.connect_room(room_id, ws)
    try:
        while True:
            text = await ws.receive_text()
            # Broadcast received message to everyone in the chat room
            await manager.send_to_room(room_id, {
                "event": "message",
                "from_id": user.id,
                "text": text,
            })
    except WebSocketDisconnect:
        await manager.disconnect_room(room_id, ws)


@router.websocket("/support")
async def support_ws(
    ws: WebSocket,
    token: str = Query(...),
):
    """
    Room WebSocket: chat with support team.
    Each user gets their own support room: support_{user_id}

    Client connects to: ws://host/api/v1/ws/support?token=<jwt>

    TODO: add support agent side — agent connects to support_{user_id}
          to respond to a specific user's ticket.
    """
    user = await _authenticate(token)
    if not user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    room_id = f"support_{user.id}"
    await manager.connect_room(room_id, ws)
    try:
        while True:
            text = await ws.receive_text()
            await manager.send_to_room(room_id, {
                "event": "support_message",
                "from_id": user.id,
                "text": text,
            })
    except WebSocketDisconnect:
        await manager.disconnect_room(room_id, ws)


# -------------------------
# Broadcast endpoint
# -------------------------

@router.websocket("/broadcast")
async def broadcast_ws(ws: WebSocket):
    """
    Public broadcast WebSocket: receives real-time announcements sent to all users.
    No authentication required — any visitor can subscribe.

    Used for: flash sales, new promotions, system maintenance notices.
    Client connects to: ws://host/api/v1/ws/broadcast

    Integration point: call from any service or admin endpoint —
        await manager.broadcast({"event": "flash_sale", "message": "...", "discount": 50})

    TODO: when scaling to multiple server instances, replace with Redis Pub/Sub.
    """
    room_id = "broadcast"
    await manager.connect_room(room_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_room(room_id, ws)
