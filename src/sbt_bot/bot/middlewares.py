from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sbt_bot.config import Settings
from sbt_bot.db.repositories import UserRepository


class DbSessionMiddleware(BaseMiddleware):
    """Provide an AsyncSession and Settings to every handler."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        settings: Settings,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["settings"] = self.settings
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class BanCheckMiddleware(BaseMiddleware):
    """Reject updates from banned users."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        session: AsyncSession | None = data.get("session")
        if user is not None and session is not None:
            repo = UserRepository(session)
            if await repo.is_banned(user.id):
                if isinstance(event, CallbackQuery):
                    await event.answer("Доступ ограничен.", show_alert=True)
                elif isinstance(event, Message):
                    await event.answer("Ваш доступ к боту ограничен.")
                return None
        return await handler(event, data)
