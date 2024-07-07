import json
import re
from typing import Any, Callable, Coroutine

from aio_pika.abc import AbstractIncomingMessage
from icecream import ic

from app import BaseApp, bot_d
from telethon.events import NewMessage


class LaborProtect(BaseApp):
    def init_commands(self):
        return [
            ("help_labor_protect", "Справочник по командам ОТ", self.help),
        ]

    def init_regex_command(
            self,
    ) -> dict[re.Pattern, Callable[[Any], Coroutine[None, None, None]]]:
        pattern = "[a-zA-Z0-9а-яА-Я_]+"
        return {re.compile(f"/lp {pattern} {pattern}"): self._command}  # type: ignore

    @bot_d(routing_key="labor_protect_rpc_queue")
    async def _command(
            self, command: str, login: str, password: str, **_: NewMessage.Event
    ):
        return {"login": login, "password": password}

    @staticmethod
    async def help(*_, **__):
        return """
        **Справочник по командам**
        Пока нет реализации удобной навигации, используется ручной ввод команд.
        1️⃣ **__Озрана труда и оказание первой медицинской помощи:__**
        **/lp**   
        Пример: 
        /lp user_name token       
        """

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            self.logger.warning(f"Bad message {message!r}")
            return
        username = self.users.pop(message.correlation_id)
        result = await self._wait_future(message.correlation_id, message.body)
        # TODO: сделать обработку некорректных данных в ответе
        # message = json.loads(result.decode("utf-8"))
        # ic(message)
        # message = f"hello, {username}!"
        message = self._create_response_message(result)
        await self.bot.send_message(username, message)
        self.logger.debug(f"сообщение отправлено {message}")

    def _create_response_message(self, message: bytes) -> str:
        json_data = json.loads(message.decode("utf-8"))
        ic(json_data)
        return (f"**результат запроса:**\n"
                f"\n"
                f"Пользователь:  {json_data['user']}\n"
                f"Статус:  {json_data['status']}\n"
                f"Сообщение:  {json_data['message']}\n"
                f"Пройденный курс: {json_data['course']}\n"
                f"Результат:  {json_data['result']}\n"
                )
