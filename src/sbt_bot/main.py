import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis

from sbt_bot.bot.handlers import menu_router, report_router, start_router
from sbt_bot.bot.middlewares import BanCheckMiddleware, DbSessionMiddleware
from sbt_bot.config import Settings, load_settings
from sbt_bot.db import create_engine_and_sessionmaker
from sbt_bot.logging_setup import setup_logging
from sbt_bot.parser import BsacPdfScheduleSource, ScheduleSyncService

logger = logging.getLogger(__name__)


async def run_bot(settings: Settings) -> None:
    """Initialize dependencies, start background sync, and run polling."""
    engine, session_factory = create_engine_and_sessionmaker(settings.database_url)
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    dp.update.middleware(DbSessionMiddleware(session_factory, settings))
    dp.update.middleware(BanCheckMiddleware())

    pdf_source = BsacPdfScheduleSource(
        stage_urls={
            "ВО": settings.bsac_vo_url,
            "ССО": settings.bsac_sso_url,
        }
    )
    sync_service = ScheduleSyncService(
        sources=[pdf_source],
        session_factory=session_factory,
    )
    dp["sync_service"] = sync_service

    dp.include_routers(start_router, menu_router, report_router)

    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    scheduler.add_job(
        sync_service.sync_all,
        trigger="interval",
        minutes=settings.parse_interval_minutes,
        id="schedule_sync",
        replace_existing=True,
    )
    scheduler.start()

    # Initial sync in background so bot starts responding immediately
    asyncio.create_task(sync_service.sync_all())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await redis.aclose()
        await engine.dispose()


def run() -> None:
    """CLI entrypoint."""
    settings = load_settings()
    setup_logging(level=settings.log_level, log_file=settings.log_file)
    try:
        asyncio.run(run_bot(settings))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")


if __name__ == "__main__":
    run()
