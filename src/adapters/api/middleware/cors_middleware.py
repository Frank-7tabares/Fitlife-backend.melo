import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
_cors_raw = (os.getenv('CORS_ORIGINS') or '').strip().strip('[]').replace('"', '').replace("'", '')
_cors_list = [o.strip() for o in _cors_raw.split(',') if o.strip()]
CORS_ORIGINS = tuple(_cors_list) if _cors_list else ('http://localhost:5173', 'http://localhost:5174', 'http://localhost:4200', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174', 'http://127.0.0.1:4200')

def _add_cors_headers(response: Response, origin: str | None) -> None:
    if origin and origin in CORS_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = CORS_ORIGINS[0]
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, Accept, Origin, X-Requested-With'

class CustomCORSMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get('origin')
        if request.method == 'OPTIONS':
            response = Response(status_code=200)
            _add_cors_headers(response, origin)
            return response
        response = await call_next(request)
        _add_cors_headers(response, origin)
        return response
