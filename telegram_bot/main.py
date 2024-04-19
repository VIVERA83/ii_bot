"""The application launcher."""

import asyncio

from core.setup import run_app

if __name__ == "__main__":
    asyncio.run(run_app())
