import re
from typing import Any, Callable, Coroutine

from app import BaseApp, bot_d
from telethon.events import NewMessage

REPORTS = [
    "date_range",
    "week",
    "last_week",
    "month",
    "last_month",
    "day",
    "test",
]


class Speed(BaseApp):
    def init_commands(self):
        return [
            ("help_speed", "Справочник по командам отчета по скорости", self.hello),
        ]

    def init_regex_command(
        self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        pattern = f"(?:{'|'.join(REPORTS)})"
        date_pattern = "[0-9]{4}-(0[1-9]|1[012])-(0[1-9]|1[0-9]|2[0-9]|3[01])"
        return {  # type: ignore
            re.compile(f"/{pattern}"): self._command,
            re.compile(
                f"/date_range {date_pattern} {date_pattern}"
            ): self._get_report_date_range,
        }

    @bot_d(routing_key="speed_rpc_queue")
    async def _command(self, command: str, **_: NewMessage.Event):
        return {"report_type": command[1:]}

    @bot_d(routing_key="speed_rpc_queue")
    async def _get_report_date_range(
        self, command: str, start_date: str, end_date: str, **_: NewMessage.Event
    ):
        return {
            "report_type": command[1:],
            "start_date": start_date,
            "end_date": end_date,
        }

    @staticmethod
    async def hello(*_, **__):
        return """
        **Справочник по командам**
        Пока нет реализации удобной навигации, используется ручной ввод команд.
        1️⃣ **__Отчет за прошлую неделю:__**
        **/last_week**   
        2️⃣⃣ **__Отчет за период:__**
        **/date_range 2024-01-01 2024-01-31**       
        """
