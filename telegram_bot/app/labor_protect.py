import re
from typing import Callable, Any, Coroutine

from app import BaseApp, bot_d

from telethon.events import NewMessage
from icecream import ic

ic.includeContext = True


class LaborProtect(BaseApp):
    def init_commands(self):
        return [
            ("help_labor_protect", "Справочник по командам ОТ", self.hello),
        ]

    def init_regex_command(self,) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        pattern = "[a-zA-Z0-9_]+"
        return {re.compile(f"/lp {pattern} {pattern}"): self._command}  # type: ignore

    @bot_d(routing_key="labor_protect_rpc_queue")
    async def _command(
        self, command: str, login: str, password: str, **_: NewMessage.Event
    ):
        return {"login": login, "password": password}

    @staticmethod
    async def hello(*_, **__):
        return """
        **Справочник по командам**
        Пока нет реализации удобной навигации, используется ручной ввод команд.
        1️⃣ **__Озрана труда и оказание первой медицинской помощи:__**
        **/lp**   
        Пример: 
        /lp user_name token       
        """
