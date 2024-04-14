import asyncio
import json
import logging
import uuid
from typing import MutableMapping

from aio_pika.abc import AbstractIncomingMessage
from aio_pika import Message
from telethon.events import NewMessage

from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor


class Application:
    def __init__(self, bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger):
        self.bot = bot
        self.rabbit = rabbit
        self.logger = logger
        self.callback_queue = None
        self.in_queue = None
        self.futures: MutableMapping[str, asyncio.Future] = {}

    async def start(self):
        await asyncio.gather(self._wait_connect(self.rabbit), self._wait_connect(self.bot))
        await self.bot.add_commands([("test", "тестовая команда", self._command)])  # noqa
        self.logger.info("Application started")
        await self.rabbit.channel.declare_queue(exclusive=True)
        self.callback_queue = await self.rabbit.create_queue()
        await asyncio.gather(self.callback_queue.consume(callback=self._on_response, no_ack=True))

    async def stop(self):
        await self.rabbit.disconnect()
        await self.bot.disconnect()
        self.logger.info("Application stopped")

    async def _command(self, event: NewMessage.Event):
        data = {"login": "sergievskiy_an", "password": "QQQQqqqq5555", "course_type": "z"}

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future
        await self.rabbit.publish(routing_key="rpc_queue",
                                  correlation_id=correlation_id,
                                  reply_to=self.callback_queue.name,
                                  body=json.dumps(data).encode("utf-8"), )
        self.logger.debug("Incoming test command")
        return "Запрос принят, ожидается ответ"

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)
        result = await future
        response = await self.bot.send_message("vivera83", json.dumps(result.decode("utf-8")))
        self.logger.warning(f"Got response: {result!r}")
        # return "Yes"
        # print(f"Got response: {message!r}")

    # не используется
    async def _wait_connect(self, client: TgBotAccessor | RabbitAccessor):
        while not client.is_connected():
            await asyncio.sleep(0.5)
            self.logger.debug(f"Wait connect {client.__class__.__name__}")
        self.logger.debug(f"Connected {client.__class__.__name__}")
