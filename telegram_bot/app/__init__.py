import asyncio
import json
import logging
import re
import uuid
from typing import Any, Callable, Coroutine, MutableMapping

from aio_pika.abc import AbstractIncomingMessage
from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor
from telethon.events import NewMessage

from .utils import create_future, create_message


def bot_d(routing_key: str, message: str = "Запрос принят, ожидается ответ"):
    def bot_decorator(func: Callable):
        async def wrapper(cls: "BaseApp", *args, event: NewMessage.Event, **kwargs):
            correlation_id = uuid.uuid4().hex
            # TODO: некоторые пользователи не дают username
            cls.users[correlation_id] = (
                event.message.sender.username or event.message.sender.id
            )
            cls.futures[correlation_id] = create_future()
            result = await func(cls, *args, event=event, **kwargs)
            # TODO: сделать проверку на то что канал отрыт и если нет то на возврат ошибку
            if not cls.queue_names.get(routing_key, None):
                cls.queue_names[routing_key] = await cls.rabbit.consume(
                    callback=cls._on_response, no_ack=True
                )
            await cls.rabbit.publish(
                routing_key=routing_key,
                correlation_id=correlation_id,
                reply_to=cls.queue_names[routing_key],
                body=json.dumps(result).encode("utf-8"),
            )
            return message

        return wrapper

    return bot_decorator


class BaseApp:
    def __init__(
        self, bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger
    ):
        self.bot = bot
        self.rabbit = rabbit
        self.logger = logger
        self.callback_queue = None

        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.users: MutableMapping[str, str] = {}
        self.queue_names: MutableMapping[str, str] = {}

    def init_commands(self) -> list[tuple[str, str, Callable[[], Coroutine]]]:
        """
        For example:
          return[("test", "тестовая команда", self._test_command)]
        """
        return []

    def init_regex_command(
        self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        """Create a report regex command.

        For example:
            return {
                re.compile("/report [a-zA-Z0-9_]+ [a-zA-Z0-9_]+ [a-zA-Z0-9_]+"): self._command
            }

        Returns:
            bytes: A dictionary mapping compiled regex patterns to callback functions.
        """
        return {}

    async def _setup_bot_commands(self):
        self.bot.update_regex_command_handler(self.init_regex_command())
        await self.bot.add_commands(self.init_commands())

    async def start(self):
        await self._setup_bot_commands()
        await self.__worker()

    async def stop(self):
        self.logger.info(f"{self.__class__.__name__} stopped.")

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            self.logger.warning(f"Bad message {message!r}")
            return
        username = self.users.pop(message.correlation_id)
        result = await self._wait_future(message.correlation_id, message.body)
        # TODO: сделать обработку некорректных данных в ответе
        message = create_message(json.loads(result.decode("utf-8")))
        await self.bot.send_message(username, message)
        self.logger.debug(f"Got response: {message}")

    async def _wait_future(self, correlation_id: str, body: bytes) -> bytes:
        """Awaits for a future to be set with a result and returns the result.

        Parameters:
            correlation_id (str): The unique identifier for the future.
            body (bytes): The body of the future.
        Returns:
            bytes: The result of the future.
        """
        future: asyncio.Future = self.futures.pop(correlation_id)
        future.set_result(body)
        result = await future
        return result

    async def __worker(self):
        """Worker function that listens for tasks in a queue."""

        queue = asyncio.Queue(1)
        self.logger.info(f"{self.__class__.__name__} started.")
        while True:
            try:
                await queue.get()
            except asyncio.CancelledError:
                self.logger.warning("Application cancelled")
                break
