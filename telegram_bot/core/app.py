"""The location of the final assembly of the application."""
import asyncio

from bot.accessor import TgBotAccessor
from core.logger import setup_logging


def run_app():
    loop = asyncio.get_event_loop()
    bot = TgBotAccessor(logger=setup_logging())
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.stop())
