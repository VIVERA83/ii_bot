import asyncio
import logging

from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor


async def app(bot: TgBotAccessor, rabbit: RabbitAccessor, logger: logging.Logger):
    async def wait_connect(client: TgBotAccessor | RabbitAccessor):
        while not client.is_connected():
            await asyncio.sleep(0.5)
            logger.debug(f"Wait connect {client.__class__.__name__}")
        logger.debug(f"Connected {client.__class__.__name__}")





    await asyncio.gather(wait_connect(rabbit), wait_connect(bot))
    user_id = 1895968253  # "vivera83" оба варианта работают

    # while True:
    #     print(await bot.send_message(user_id, "Hello World!"))
    #     await asyncio.sleep(3)
