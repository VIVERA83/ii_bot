import logging
from typing import Callable, Any, Awaitable

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)

from core.settings import RabbitMQSettings


class RabbitAccessor:
    connection: AbstractConnection
    channel: AbstractChannel
    exchange: AbstractExchange
    queue: AbstractQueue

    def __init__(self, settings: RabbitMQSettings = RabbitMQSettings(),
                 logger: logging.Logger = logging.getLogger(__name__),
                 ) -> None:
        self.settings = settings
        self.queue_name = "rpc_queue"
        self.logger = logger

    async def reply_to(self, message: AbstractIncomingMessage, response: bytes) -> None:
        await self.exchange.publish(Message(body=response, correlation_id=message.correlation_id, ),
                                    routing_key=message.reply_to, )
        self.logger.debug(f" [x] Sent {response!r}")

    async def connect(self) -> None:
        self.connection = await connect(self.settings.dsn(True))
        self.channel = await self.connection.channel()
        self.exchange = self.channel.default_exchange
        self.queue = await self.channel.declare_queue(self.queue_name)
        self.logger.info(f"{self.__class__.__name__} connected")

    async def disconnect(self) -> None:
        if getattr(self, "connection", None):
            await self.connection.close()
        self.logger.info(f"{self.__class__.__name__} disconnected")

    async def consume(self, queue_name: str = "rpc_queue",
                      callback: Callable[[AbstractIncomingMessage], Awaitable[Any]] = None):
        queue = await self.channel.declare_queue(exclusive=True, name=queue_name)
        await queue.consume(callback, no_ack=True)

    def is_connected(self) -> bool:
        if getattr(self, "connection", None):
            return not self.connection.is_closed
        return False
