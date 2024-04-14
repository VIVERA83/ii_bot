"""The location of the final assembly of the application."""
import asyncio

from bot.accessor import TgBotAccessor
from core.logger import setup_logging


async def task():
    while True:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("cancelled")
            break
        print("task")


async def run_app():
    bot = TgBotAccessor(logger=setup_logging())
    try:
        await asyncio.gather(bot.connect(), task())
    except asyncio.CancelledError:
        await bot.stop()
