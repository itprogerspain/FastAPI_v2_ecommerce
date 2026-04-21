from fastapi import HTTPException, status

from app.application.messages.schemas import MessageCreate, MessageOut, MessageList, UnreadCount
from app.infrastructure.repositories.message import MessageRepository


class MessageService:
    """
    Business logic layer for chat messages (Asynchronous).
    Delegates database operations to MessageRepository.
    """

    def __init__(self, repository: MessageRepository):
        self.repository = repository

    async def send_message(self, sender_id: int, data: MessageCreate) -> MessageOut:
        """
        Persist a new message sent by the current user.
        A user cannot send a message to themselves.
        """
        if data.receiver_id is not None and data.receiver_id == sender_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send a message to yourself",
            )

        message_data = {
            "sender_id": sender_id,
            "receiver_id": data.receiver_id,
            "product_id": data.product_id,
            "text": data.text,
        }
        return await self.repository.create(message_data)

    async def get_conversation(
        self, user_id: int, other_user_id: int, page: int, page_size: int
    ) -> MessageList:
        """
        Return paginated message history between the current user and another user.
        """
        total = await self.repository.count_conversation(user_id, other_user_id)
        items = await self.repository.get_conversation(
            user_id, other_user_id, page, page_size
        )
        return MessageList(items=items, total=total, page=page, page_size=page_size)

    async def get_support_history(
        self, user_id: int, page: int, page_size: int
    ) -> MessageList:
        """
        Return paginated support chat history for the current user.
        """
        total = await self.repository.count_support_history(user_id)
        items = await self.repository.get_support_history(user_id, page, page_size)
        return MessageList(items=items, total=total, page=page, page_size=page_size)

    async def get_unread_count(self, user_id: int) -> UnreadCount:
        """
        Return the number of unread messages received by the current user.
        """
        count = await self.repository.get_unread_count(user_id)
        return UnreadCount(unread_count=count)

    async def mark_as_read(self, message_id: int, user_id: int) -> MessageOut:
        """
        Mark a message as read.
        Only the recipient (receiver_id) can mark a message as read.
        """
        message = await self.repository.get_by_id(message_id)

        if message is None or not message.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        # Only the intended recipient can mark the message as read
        if message.receiver_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to mark this message as read",
            )

        return await self.repository.mark_as_read(message)

    async def delete_message(self, message_id: int, user_id: int) -> None:
        """
        Soft-delete a message.
        Only the sender can delete their own message.
        """
        message = await self.repository.get_by_id(message_id)

        if message is None or not message.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        # Only the sender can delete the message
        if message.sender_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to delete this message",
            )

        await self.repository.soft_delete(message)
