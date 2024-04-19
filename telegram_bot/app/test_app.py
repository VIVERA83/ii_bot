from app import BaseApp


class LaborProtect(BaseApp):
    def init_commands(self):
        return [
            ("help_labor_protect", "Справочник по командам ОТ", self.hello),
        ]

    async def hello(self, *_, **__):
        return """
        **Справочник по командам ОТ**       
        """
