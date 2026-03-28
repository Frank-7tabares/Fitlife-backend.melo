"""En Windows, aiomysql + SSL falla con ProactorEventLoop (WinError 87). Usar Selector."""
import asyncio
import sys


def apply_windows_ssl_asyncio_fix() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
