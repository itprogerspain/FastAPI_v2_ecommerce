from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.message import Message as MessageModel


class MessageRepository:
    """
    Repository layer for message database operations (Asynchronous).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> MessageModel:
        """
        Persist a new message in the database.
        """
        message = MessageModel(**data)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation(
        self, user_id: int, other_user_id: int, page: int, page_size: int
    ) -> list[MessageModel]:
        """
        Retrieve paginated message history between two users.
        Returns messages in ascending order (oldest first) for chat display.
        Excludes soft-deleted messages (is_active=False).
        """
        stmt = (
            select(MessageModel)
            .where(
                MessageModel.is_active.is_(True),
                # Both directions: A→B and B→A
                or_(
                    and_(
                        MessageModel.sender_id == user_id,
                        MessageModel.receiver_id == other_user_id,
                    ),
                    and_(
                        MessageModel.sender_id == other_user_id,
                        MessageModel.receiver_id == user_id,
                    ),
                ),
            )
            .order_by(MessageModel.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def count_conversation(self, user_id: int, other_user_id: int) -> int:
        """
        Count total messages in a conversation (for pagination).
        """
        stmt = select(func.count(MessageModel.id)).where(
            MessageModel.is_active.is_(True),
            or_(
                and_(
                    MessageModel.sender_id == user_id,
                    MessageModel.receiver_id == other_user_id,
                ),
                and_(
                    MessageModel.sender_id == other_user_id,
                    MessageModel.receiver_id == user_id,
                ),
            ),
        )
        return await self.db.scalar(stmt) or 0

    async def get_support_history(
        self, user_id: int, page: int, page_size: int
    ) -> list[MessageModel]:
        """
        Retrieve support chat history for a user (receiver_id IS NULL).
        Returns messages in ascending order. Excludes soft-deleted messages.
        """
        stmt = (
            select(MessageModel)
            .where(
                MessageModel.is_active.is_(True),
                MessageModel.sender_id == user_id,
                MessageModel.receiver_id.is_(None),
            )
            .order_by(MessageModel.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def count_support_history(self, user_id: int) -> int:
        """
        Count total support messages for a user (for pagination).
        """
        stmt = select(func.count(MessageModel.id)).where(
            MessageModel.is_active.is_(True),
            MessageModel.sender_id == user_id,
            MessageModel.receiver_id.is_(None),
        )
        return await self.db.scalar(stmt) or 0

    async def get_unread_count(self, user_id: int) -> int:
        """
        Count unread messages received by the user.
        Used for notification badge in the frontend.
        """
        stmt = select(func.count(MessageModel.id)).where(
            MessageModel.receiver_id == user_id,
            MessageModel.is_read.is_(False),
            MessageModel.is_active.is_(True),
        )
        return await self.db.scalar(stmt) or 0

    async def get_by_id(self, message_id: int) -> MessageModel | None:
        """
        Retrieve a single message by ID. Returns None if not found.
        """
        stmt = select(MessageModel).where(MessageModel.id == message_id).limit(1)
        result = await self.db.scalars(stmt)
        return result.first()

    async def mark_as_read(self, message: MessageModel) -> MessageModel:
        """
        Mark a message as read. Caller is responsible for ownership check.
        """
        message.is_read = True
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def soft_delete(self, message: MessageModel) -> None:
        """
        Soft-delete a message by setting is_active=False.
        Preserves history for auditing and dispute resolution.
        """
        message.is_active = False
        await self.db.commit()
