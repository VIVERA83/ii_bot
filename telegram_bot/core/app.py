"""The location of the final assembly of the application."""

import asyncio

from app import Application
from app.utils import wait_connect
from bot.accessor import TgBotAccessor
from core.logger import setup_logging
from core.settings import RabbitMQSettings
from rabbit.accessor import RabbitAccessor


async def task(logger):
    while True:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.debug("cancelled")
            break
        logger.debug("task")


async def run_app():
    logger = setup_logging()
    bot = TgBotAccessor(logger=logger)
    rabbit = RabbitAccessor(settings=RabbitMQSettings(), logger=logger)
    app = Application(bot, rabbit, logger)
    try:
        await asyncio.gather(bot.connect(), rabbit.connect())
        await app.start()
    except asyncio.CancelledError:
        ...
    finally:
        await rabbit.disconnect()
        await bot.disconnect()
        await app.stop()