import asyncio
import json
import logging
# import uuid
import re
import uuid

from typing import MutableMapping, Callable, Any, Coroutine

from aio_pika.abc import AbstractIncomingMessage
from icecream import ic
from telethon.events import NewMessage

# from telethon.events import NewMessage

from .utils import create_message, COURSE_TYPE, create_future
from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor


def bot_d(routing_key: str):
    def bot_decorator(func: Callable):
        async def wrapper(cls: "BaseApp", *args, event: NewMessage.Event, **kwargs):
            correlation_id = uuid.uuid4().hex
            cls.users[correlation_id] = event.message.sender.username
            cls.futures[correlation_id] = create_future()
            result = await func(cls, *args, event=event, **kwargs)
            if not cls.queue_names.get(cls.routing_key, None):
                cls.queue_names[routing_key] = await cls.rabbit.consume(callback=cls._on_response, no_ack=True)
            await cls.rabbit.publish(
                routing_key=routing_key,
                correlation_id=correlation_id,
                reply_to=cls.queue_names[routing_key],
                body=json.dumps(result).encode("utf-8"),
            )
            return "Запрос принят, ожидается ответ"

        return wrapper

    return bot_decorator


class BaseApp:
    def __init__(
            self, bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger
    ):
        self.routing_key = "rpc_queue"
        self.bot = bot
        self.rabbit = rabbit
        self.logger = logger
        self.callback_queue = None
        self.in_queue = None

        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.users: MutableMapping[str, str] = {}
        self.queue_names: MutableMapping[str, str] = {}

        # self.queue_name = None

    # def bot_decorator(self: Callable):
    #     async def wrapper(cls: "BaseApp", *args, event: NewMessage.Event, **kwargs):
    #         correlation_id = uuid.uuid4().hex
    #         cls.users[correlation_id] = event.message.sender.username
    #         cls.futures[correlation_id] = create_future()
    #         result = await self(cls, *args, event=event, **kwargs)
    #         await cls.rabbit.publish(
    #             routing_key=cls.routing_key,
    #             correlation_id=correlation_id,
    #             reply_to=cls.queue_name,
    #             body=json.dumps(result).encode("utf-8"),
    #         )
    #         return "Запрос принят, ожидается ответ"
    #
    #     return wrapper

    async def setup_bot_commands(self):
        """
        For example:
        await self.bot.add_commands([("test", "тестовая команда", self._test_command)])  # noqa
        self.bot.update_regex_command_handler(self.create_report_regex_command())

        """
        NotImplementedError()

    async def start(self):
        await self.setup_bot_commands()
        # добавляем команды для бота
        # await self.bot.add_commands([("test", "тестовая команда", self._test_command)])  # noqa
        # self.bot.update_regex_command_handler(self.create_report_regex_command())

        # подписываемся на получение ответов, и назначаем функцию обратного вызова
        # self.queue_names[self.routing_key] = await self.rabbit.consume(callback=self._on_response, no_ack=True)

        self.logger.info("Application started")
        queue = asyncio.Queue(1)
        while True:
            try:
                await queue.get()
            except asyncio.CancelledError:
                self.logger.warning("Application cancelled")
                break

    async def stop(self):
        self.logger.info("Application stopped")

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            self.logger.warning(f"Bad message {message!r}")
            return
        username = self.users.pop(message.correlation_id)
        result = await self._wait_future(message.correlation_id, message.body)
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

    def create_report_regex_command(
            self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        """Create a report regex command.

        Returns:
            bytes: A dictionary mapping compiled regex patterns to callback functions.
        """
        pattern = "[a-zA-Z0-9_]+"
        return {  # noqa
            re.compile(f"/report {pattern} {pattern} {pattern}"): self._command
        }

    async def _test_command(
            self,
            *_,
            **__,
    ):
        return "Тестовый запрос принят"

    # @bot_decorator  # noqa
    # async def _command(
    #         self,
    #         login: str,
    #         password: str,
    #         course_type: COURSE_TYPE,
    #         event: NewMessage.Event,
    #         *_,
    #         **__,
    # ) -> Any:
    #
    #     data = {"login": login, "password": password, "course_type": course_type}
    #     # сохраняем идентификатор запроса
    #     # correlation_id = uuid.uuid4().hex
    #     # self.users[correlation_id] = event.message.sender.username
    #     # self.futures[correlation_id] = create_future()
    #
    #     # отправляем запрос
    #     # await self.rabbit.publish(
    #     #     routing_key=self.routing_key,
    #     #     correlation_id=correlation_id,
    #     #     reply_to=self.queue_name,
    #     #     body=json.dumps(data).encode("utf-8"),
    #     # )
    #     self.logger.debug("Incoming test command")
    #     return data
    #     # return "Запрос принят, ожидается ответ"
