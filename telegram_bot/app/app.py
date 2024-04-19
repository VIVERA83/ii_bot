import logging
import re
from typing import Any, Callable, Coroutine

from app import BaseApp
from app.magnum import Magnum
from app.test_app import LaborProtect
from bot.accessor import TgBotAccessor
from rabbit.accessor import RabbitAccessor


class MainApp(BaseApp):
    def __init__(
        self,
        bot: TgBotAccessor,
        rabbit: RabbitAccessor,
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        super().__init__(bot, rabbit, logger)
        self.children = [app(bot, rabbit, logger) for app in [Magnum, LaborProtect]]

    #
    def init_commands(self) -> list[tuple[str, str, Callable[[], Coroutine]]]:
        result = []
        for child in self.children:
            result.append(*child.init_commands())
        return result

    def init_regex_command(
        self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        result = {}
        for child in self.children:
            result.update(child.init_regex_command())
        return result
