from fastapi import APIRouter, Depends, status, Query

from app.api.deps import get_message_service, get_current_user
from app.application.messages.schemas import (
    MessageCreate,
    MessageOut,
    MessageList,
    UnreadCount,
)
from app.application.messages.service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post(
    "/",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    data: MessageCreate,
    current_user=Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    """
    Send a new message.
    Set receiver_id=None to send to support chat.
    """
    return await service.send_message(current_user.id, data)


@router.get("/unread-count", response_model=UnreadCount)
async def get_unread_count(
    current_user=Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    """
    Return the number of unread messages received by the current user.
    Used for the notification badge in the frontend.
    """
    return await service.get_unread_count(current_user.id)


@router.get("/support", response_model=MessageList)
async def get_support_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    """
    Return paginated support chat history for the current user.
    """
    return await service.get_support_history(current_user.id, page, page_size)


@router.get("/{other_user_id}", response_model=MessageList)
async def get_conversation(
    other_user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    """
    Return paginated message history between the current user and another user.
    Messages are ordered oldest-first for natural chat display.
    """
    return await service.get_conversation(
        current_user.id, other_user_id, page, page_size
    )


@router.patch("/{message_id}/read", response_model=MessageOut)
async def mark_as_read(
    message_id: int,
    current_user=Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    """
    Mark a message as read. Only the recipient can do this.
    """
    return await service.mark_as_read(message_id, current_user.id)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user=Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    """
    Soft-delete a message. Only the sender can delete their own message.
    """
    await service.delete_message(message_id, current_user.id)
