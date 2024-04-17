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
