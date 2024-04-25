import re
from typing import Any, Callable, Coroutine, Literal

from app import BaseApp, bot_d
from telethon.events import NewMessage

COURSE_TYPE = Literal["cpd", "epd", "etd", "d", "m", "z", "ce", "ee"]
COURSES = ["cpd", "epd", "etd", "d", "m", "z", "ce", "ee"]


class Magnum(BaseApp):

    def init_commands(self):
        return [
            ("help_magnum", "Справочник по командам магнум", self.hello),
        ]

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
        pattern = "[a-zA-Z0-9_!*$%#@()?]+"
        return {  # type: ignore
            re.compile(f"/{command} {pattern} {pattern}"): self._command
        }

    @staticmethod
    async def hello(*_, **__):
        return """
        **Справочник по командам**
        Пока нет реализации удобной навигации, используется ручной ввод команд.
        1️⃣ **__Прямая доставка категория С:__**
        **/cpd**
        2️⃣ **__Прямая доставка категория Е:__**
        **/epd**
        3️⃣ **__Транзитная доставка категория:__**         
        **/etd**
        4️⃣ **__Защитное вождение:__**
        **/z**   
        5️⃣ **__Водитель диспетчер:__**
        **/d**
        6️⃣ **__Наставник:__**
        **/m**
        
        Пример: 
        /z user_name token       
        """
