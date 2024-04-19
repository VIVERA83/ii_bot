"""The location of the final assembly of the application."""

import asyncio

from app.app import MainApp
from bot.accessor import TgBotAccessor
from core.logger import setup_logging
from rabbit.accessor import RabbitAccessor


async def run_app():
    logger = setup_logging()
    bot = TgBotAccessor(logger=logger)
    rabbit = RabbitAccessor(logger=logger)
    app = MainApp(bot, rabbit, logger)
    try:
        await asyncio.gather(bot.connect(), rabbit.connect())
        await asyncio.gather(app.start())
    except asyncio.CancelledError:
        ...
    finally:
        await rabbit.disconnect()
        await bot.disconnect()
        await app.stop()
