import asyncio
import logging
from asyncio import Future
from typing import Literal

from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor

COURSE_TYPE = Literal["cpd", "epd", "etd", "d", "m", "z", "ce", "ee"]


def create_message(data: dict[str, str]) -> str:
    """Create message using the given data dictionary and return the constructed message as a string.

    Parameters:
        data (dict[str, str]): The dictionary containing key-value pairs to construct the message.

    Returns:
        str: The constructed message as a string.
    """
    message = ""
    for key, value in data.items():
        message += f"{key}: {value}\n"
    return message


async def wait_connect(client: TgBotAccessor | RabbitAccessor, logger: logging.Logger = logging.getLogger(__name__)):
    """A function that waits for the client to connect and logs messages.

    Parameters:
        client: TgBotAccessor | RabbitAccessor - the client to wait for connection.
        logger: logging.Logger - the logger to use.
    """
    while not client.is_connected():
        await asyncio.sleep(0.5)
        logger.debug(f"Wait connect {client.__class__.__name__}")
    logger.debug(f"Connected {client.__class__.__name__}")


def create_future() -> Future:
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    return future
