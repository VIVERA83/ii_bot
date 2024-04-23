"""All application settings."""

import os
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))

LOG_LEVEL = Literal[
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
]


class Base(BaseSettings):
    class Config:
        """Settings for reading environment variables from a file.

        env_file - The path to the environment, to run locally
        """

        env_nested_delimiter = "__"
        env_file = os.path.join(BASE_DIR, ".env_tg_bot")
        enf_file_encoding = "utf-8"
        extra = "ignore"


class LogSettings(Base):
    """Setting logging.

    level (str, optional): The level of logging. Defaults to "INFO".
    guru (bool, optional): Whether to enable guru mode. Defaults to True.
    traceback (bool, optional): Whether to include tracebacks in logs. Defaults to True.
    """

    level: LOG_LEVEL
    guru: bool
    traceback: bool


class TgSettings(Base):
    tg_api_id: int
    tg_api_hash: str
    tg_bot_token: str
    tg_admin_id: int


class RabbitMQSettings(Base):
    rabbit_user: str
    rabbit_password: SecretStr
    rabbit_host: str
    rabbit_port: int

    def dsn(self, show_secret: bool = False) -> str:
        """Returns the connection URL as a string.

        Args:
            show_secret (bool, optional): Whether to show the secret. Defaults to False.

        Returns:
            str: The connection URL.
        """
        return "amqp://{user}:{password}@{host}:{port}/".format(
            user=self.rabbit_user,
            password=(
                self.rabbit_password.get_secret_value()
                if show_secret
                else self.rabbit_password
            ),
            host=self.rabbit_host,
            port=self.rabbit_port,
        )
