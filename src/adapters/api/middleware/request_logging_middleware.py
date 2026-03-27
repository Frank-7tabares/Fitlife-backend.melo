"""
Registra cada petición HTTP en consola (método, ruta, código, ms).
Usa ASGI puro + print(flush=True) porque en Windows/uvicorn a veces logging no se ve.
"""
import logging
import time

logger = logging.getLogger("fitlife.http")


class RequestLoggingMiddleware:
    """Middleware ASGI (no BaseHTTPMiddleware) para no perder logs."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        method = scope.get("method", "?")
        path = scope.get("path", "?")
        status_holder = {"code": None}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_holder["code"] = message.get("status")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            line = f"[HTTP] {method} {path} -> ERROR ({elapsed:.1f}ms)"
            print(line, flush=True)
            logger.exception("%s", line)
            raise

        elapsed = (time.perf_counter() - start) * 1000
        code = status_holder["code"] if status_holder["code"] is not None else "?"
        line = f"[HTTP] {method} {path} -> {code} ({elapsed:.1f}ms)"
        print(line, flush=True)
        logger.info("%s", line)
