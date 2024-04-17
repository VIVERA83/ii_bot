import re
from typing import Callable, Any, Coroutine

from telethon.events import NewMessage

from app import BaseApp, COURSE_TYPE, bot_d


class Magnum(BaseApp):

    async def setup_bot_commands(self):
        await self.bot.add_commands([("test", "тестовая команда", self._test_command)])  # noqa
        self.bot.update_regex_command_handler(self.create_report_regex_command())

    @bot_d(routing_key="rpc_queue")
    async def _command(self, login: str, password: str, course_type: COURSE_TYPE, *_, event: NewMessage.Event):
        data = {"login": login, "password": password, "course_type": course_type}
        return data

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
