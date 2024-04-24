import logging
from typing import Any, Awaitable, Callable, MutableMapping

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)
from core.settings import RabbitMQSettings
from rabbit.backoff import before_execution


class RabbitAccessor:
    connection: AbstractConnection = None
    channel: AbstractChannel = None
    exchange: AbstractExchange = None

    def __init__(
        self,
        settings: RabbitMQSettings = RabbitMQSettings(),
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.settings = settings
        self.logger = logger
        self.queues: MutableMapping[str, AbstractQueue] = {}

    async def reply_to(self, message: AbstractIncomingMessage, response: bytes) -> None:
        await self.exchange.publish(
            Message(
                body=response,
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
        )
        self.logger.debug(f" [x] Sent {response!r}")

    async def connect(self) -> None:
        self.connection = await before_execution(
            total_timeout=20, raise_exception=True
        )(connect)(self.settings.dsn(True))
        self.channel = await self.connection.channel()
        self.exchange = self.channel.default_exchange
        self.logger.info(f"{self.__class__.__name__} connected")

    async def disconnect(self) -> None:
        if getattr(self, "connection", None):
            await self.connection.close()
        self.logger.info(f"{self.__class__.__name__} disconnected")

    async def consume(
        self,
        callback: Callable[[AbstractIncomingMessage], Awaitable[Any]],
        name: str = None,
        no_ack: bool = False,
    ) -> str:
        if name:
            assert not self.queues.get(name), f"Queue {name} already exists"
        queue = await self.channel.declare_queue(name=name, exclusive=not name)

        self.queues[queue.name] = queue
        await queue.consume(callback=callback, no_ack=no_ack)
        return queue.name

    async def publish(
        self, reply_to: str, routing_key: str, correlation_id: str, body: bytes
    ):
        return await self.channel.default_exchange.publish(
            Message(
                body=body,
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=reply_to,
            ),
            routing_key=routing_key,
        )

    def is_connected(self) -> bool:
        """Check if the object is connected and return a boolean value.

        Returns:
            bool: True if the object is connected, False otherwise.
        """
        if getattr(self, "connection", None):
            return not self.connection.is_closed
        return False
