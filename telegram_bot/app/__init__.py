import asyncio
import json
import logging
import uuid
import re
from typing import MutableMapping, Callable, Any, Coroutine

from aio_pika.abc import AbstractIncomingMessage
from telethon.events import NewMessage

from .utils import create_message, COURSE_TYPE
from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor


class Application:
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
        self.queue_name = None

    async def start(self):
        await asyncio.gather(
            self._wait_connect(self.rabbit), self._wait_connect(self.bot)
        )

        await self.bot.add_commands(
            [("test", "тестовая команда", self._test_command)]
        )  # noqa
        self.bot.update_regex_command_handler(self.create_report_regex_command())
        await self.rabbit.channel.declare_queue(exclusive=True)
        self.queue_name = await self.rabbit.consume(
            callback=self._on_response, no_ack=True
        )
        self.logger.info("Application started")

    async def stop(self):
        await self.rabbit.disconnect()
        await self.bot.disconnect()
        self.logger.info("Application stopped")

    async def _test_command(
        self,
        *_,
        **__,
    ):
        return "Тестовый запрос принят"

    async def _command(
        self,
        login: str,
        password: str,
        course_type: COURSE_TYPE,
        event: NewMessage.Event,
        *_,
        **__,
    ):
        data = {"login": login, "password": password, "course_type": course_type}
        correlation_id = await self.create_future(event.message.sender.username)

        await self.rabbit.publish(
            routing_key=self.routing_key,
            correlation_id=correlation_id,
            # reply_to=self.callback_queue.name,
            reply_to=self.queue_name,
            body=json.dumps(data).encode("utf-8"),
        )
        self.logger.debug("Incoming test command")
        return "Запрос принят, ожидается ответ"

    async def create_future(self, username: str):
        correlation_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.users[correlation_id] = username
        self.futures[correlation_id] = future
        return correlation_id

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

    # не используется
    async def _wait_connect(self, client: TgBotAccessor | RabbitAccessor):
        """A function that waits for the client to connect and logs messages.

        Parameters:
            client: TgBotAccessor | RabbitAccessor - the client to wait for connection.
        """
        while not client.is_connected():
            await asyncio.sleep(0.5)
            self.logger.debug(f"Wait connect {client.__class__.__name__}")
        self.logger.debug(f"Connected {client.__class__.__name__}")

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
