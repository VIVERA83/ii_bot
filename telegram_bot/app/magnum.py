import re
from typing import Any, Callable, Coroutine, Literal

from app import BaseApp, bot_d
from telethon.events import NewMessage

COURSE_TYPE = Literal["cpd", "epd", "etd", "d", "m", "z", "ce", "ee"]
COURSES = ["cpd", "epd", "etd", "d", "m", "z", "ce", "ee"]


class Magnum(BaseApp):

    def init_regex_command(
        self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        return self.create_course_regex_command()

    @bot_d(routing_key="rpc_queue")
    async def _command(
        self, course_type: COURSE_TYPE, login: str, password: str, **_: NewMessage.Event
    ):
        return {"login": login, "password": password, "course_type": course_type[1:]}

    def create_course_regex_command(
        self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, Any]]]:
        """Create a report regex command.

        Returns:
            bytes: A dictionary mapping compiled regex patterns to callback functions.
        """

        command = f"(?:{'|'.join(COURSES)})"
        pattern = "[a-zA-Z0-9_]+"
        return {  # type: ignore
            re.compile(f"/{command} {pattern} {pattern}"): self._command
        }
