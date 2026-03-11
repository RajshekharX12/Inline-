import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from admin import admin_router
from browse import browse_router
from create_ad import create_router
from start import start_router
from config import BOT_TOKEN
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
log = logging.getLogger(__name__)


async def main():
    log.info("Initialising database …")
    await init_db()
from aiogram.client.default import DefaultBotProperties
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Register routers (order matters — more specific first)
    dp.include_router(admin_router)
    dp.include_router(create_router)
    dp.include_router(browse_router)
    dp.include_router(start_router)

    log.info("Starting GiftTrader Pro bot …")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
