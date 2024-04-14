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

from icecream import ic

ic.includeContext = True


class Application:
    def __init__(
        self, bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger
    ):
        self.bot = bot
        self.rabbit = rabbit
        self.logger = logger
        self.callback_queue = None
        self.in_queue = None
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.users: MutableMapping[str, str] = {}

    async def start(self):
        await asyncio.gather(
            self._wait_connect(self.rabbit), self._wait_connect(self.bot)
        )

        await self.bot.add_commands(
            [("test", "тестовая команда", self._command)]
        )  # noqa
        self.bot.update_regex_command_handler(self.create_report_regex_command())

        self.logger.info("Application started")
        await self.rabbit.channel.declare_queue(exclusive=True)
        self.callback_queue = await self.rabbit.create_queue()
        await asyncio.gather(
            self.callback_queue.consume(callback=self._on_response, no_ack=True)
        )

    async def stop(self):
        await self.rabbit.disconnect()
        await self.bot.disconnect()
        self.logger.info("Application stopped")

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
        correlation_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.users[correlation_id] = event.message.sender.username
        self.futures[correlation_id] = future

        await self.rabbit.publish(
            routing_key="rpc_queue",
            correlation_id=correlation_id,
            reply_to=self.callback_queue.name,
            body=json.dumps(data).encode("utf-8"),
        )
        self.logger.debug("Incoming test command")
        return "Запрос принят, ожидается ответ"

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            self.logger.warning(f"Bad message {message!r}")
            return
        username = self.users.pop(message.correlation_id)
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)
        result = await future
        message = create_message(json.loads(result.decode("utf-8")))
        await self.bot.send_message(username, message)
        self.logger.debug(f"Got response: {message}")

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
        pattern = "[a-zA-Z0-9_]+"
        return {  # noqa
            re.compile(f"/report {pattern} {pattern} {pattern}"): self._command
        }
