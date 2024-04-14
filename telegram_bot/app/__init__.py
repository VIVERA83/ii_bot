import asyncio
import logging

from aio_pika.abc import AbstractIncomingMessage

from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor


class Application:
    def __init__(self, bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger):
        self.bot = bot
        self.rabbit = rabbit
        self.logger = logger

    async def start(self):
        await asyncio.gather(self._wait_connect(self.rabbit), self._wait_connect(self.bot))
        await self.bot.add_commands([("test", "тестовая команда", self._command)])
        self.logger.info("Application started")
        # await self.rabbit.consume("rpc_queue", callback=self._on_response)

    async def stop(self):
        await self.rabbit.disconnect()
        await self.bot.disconnect()
        self.logger.info("Application stopped")

    async def _command(self, *_, **__):
        self.logger.debug("Incoming test command")
        await asyncio.sleep(5)
        self.logger.debug("Success test command and outgoing message")
        return "Test command successfully executed"

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return
        print(f"Got response: {message!r}")

    # не используется
    async def _wait_connect(self, client: TgBotAccessor | RabbitAccessor):
        while not client.is_connected():
            await asyncio.sleep(0.5)
            self.logger.debug(f"Wait connect {client.__class__.__name__}")
        self.logger.debug(f"Connected {client.__class__.__name__}")
#
# async def app(bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger):
#     ...
#     # async def wait_connect(client: TgBotAccessor | RabbitAccessor):
#     #     while not client.is_connected():
#     #         await asyncio.sleep(0.5)
#     #         logger.debug(f"Wait connect {client.__class__.__name__}")
#     #     logger.debug(f"Connected {client.__class__.__name__}")
#     #
#     # async def command(*_, **__):
#     #     logger.debug("Incoming test command")
#     #     await asyncio.sleep(5)
#     #     logger.debug("Success test command and outgoing message")
#     #     return "Test command successfully executed"
#     #
#     # async def on_response(message: AbstractIncomingMessage) -> None:
#     #     if message.correlation_id is None:
#     #         print(f"Bad message {message!r}")
#     #         return
#     #     print(f"Got response: {message!r}")
#
#     # await asyncio.gather(wait_connect(rabbit), wait_connect(bot))
#     # await bot.add_commands([("test", "тестовая команда", command), ])
#
#     data = {"login": "sergievskiy_an", "password": "QQQQqqqq5555", "course_type": "z1"}
#
#     # await rabbit.consume("rpc_queue", callback=on_response)
#     # channel.default_exchange.publish(
#     #     Message(
#     #         json.dumps(data).encode(),
#     #         content_type="text/plain",
#     correlation_id = correlation_id,
#     # reply_to=callback_queue.name,
#
#
# # ),
# # routing_key="rpc_queue",
# # )
# user_id = 1895968253  # "vivera83" оба варианта работают
#
# # while True:
# #     print(await bot.send_message(user_id, "Hello World!"))
# #     await asyncio.sleep(3)
