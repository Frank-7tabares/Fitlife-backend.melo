import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
logger = logging.getLogger('fitlife.api')

class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info('%s %s → %s (%.2fms)', request.method, request.url.path, response.status_code, elapsed_ms)
        return response
