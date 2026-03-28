from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
_log_level = (os.getenv('LOG_LEVEL') or 'INFO').upper()
logging.basicConfig(level=getattr(logging, _log_level, logging.INFO), format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S', stream=sys.stdout, force=True)
from .adapters.api.routes.auth_routes import router as auth_router
from .adapters.api.routes.assessment_routes import router as assessment_router
from .adapters.api.routes.physical_record_routes import router as physical_record_router
from .adapters.api.routes.training_routes import router as training_router
from .adapters.api.routes.nutrition_routes import router as nutrition_router
from .adapters.api.routes.user_routes import router as user_router
from .adapters.api.routes.instructor_routes import router as instructor_router
from .adapters.api.routes.message_routes import router as message_router
from .adapters.api.routes.reminder_routes import router as reminder_router
from .adapters.api.routes.admin_routes import router as admin_router
app = FastAPI(title='FitLife Backend API', description='Hexagonal Architecture Backend for FitLife App', version='0.1.0')
_default_origins = ['http://localhost:5173', 'http://127.0.0.1:5173']
_cors_raw = (os.getenv('CORS_ORIGINS') or '').strip()
_cors_origins = [o.strip() for o in _cors_raw.split(',') if o.strip()] or _default_origins.copy()
app.add_middleware(CORSMiddleware, allow_origins=_cors_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def _log_to_file(msg: str):
    try:
        log_path = Path(__file__).resolve().parent.parent / 'backend_requests.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'{datetime.now().isoformat()} | {msg}\n')
    except Exception:
        pass

@app.on_event('startup')
def _log_cors():
    msg = f'FitLife API iniciada. CORS origins: {_cors_origins}'
    print(msg, flush=True)
    logging.getLogger('fitlife').info(msg)
    _log_to_file('=== BACKEND INICIADO ===')

@app.middleware('http')
async def log_requests(request, call_next):
    import time
    start = time.time()
    method = request.method
    path = request.url.path
    try:
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        msg = f'[API] {method} {path} -> {response.status_code} ({elapsed:.0f}ms)'
        print(msg, flush=True)
        _log_to_file(msg)
        return response
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        err_msg = f'[API] {method} {path} -> ERROR: {e} ({elapsed:.0f}ms)'
        print(err_msg, flush=True)
        _log_to_file(err_msg)
        raise
app.include_router(auth_router, prefix='/api/v1')
app.include_router(assessment_router, prefix='/api/v1')
app.include_router(physical_record_router, prefix='/api/v1')
app.include_router(training_router, prefix='/api/v1')
app.include_router(nutrition_router, prefix='/api/v1')
app.include_router(user_router, prefix='/api/v1')
app.include_router(instructor_router, prefix='/api/v1')
app.include_router(message_router, prefix='/api/v1')
app.include_router(reminder_router, prefix='/api/v1')
app.include_router(admin_router, prefix='/api/v1')
uploads_dir = Path('uploads')
uploads_dir.mkdir(exist_ok=True)
app.mount('/api/v1/static', StaticFiles(directory=str(uploads_dir)), name='static')

@app.get('/')
async def root():
    _log_to_file('GET /')
    return {'message': 'FitLife Backend API is running', 'version': 'v1'}

@app.get('/api/v1/test-email')
@app.get('/test-email')
async def test_email(email: str=''):
    _log_to_file(f'GET test-email email={email}')
    if not os.getenv('DEBUG', '').lower() in ('true', '1', 'yes'):
        return {'ok': False, 'error': 'Indica DEBUG=True en .env'}
    if not email or '@' not in email:
        return {'ok': False, 'error': 'Indica ?email=tu@email.com'}
    try:
        from .infrastructure.email.email_service_smtp import SmtpEmailService
        sent = await SmtpEmailService.send_password_reset_email(to_email=email, reset_token='test-token-123', user_name='Test')
        _log_to_file(f'Email enviado={sent}')
        return {'ok': sent, 'message': 'Email enviado. Revisa bandeja y spam.' if sent else 'No se envio'}
    except Exception as e:
        _log_to_file(f'Email error: {e}')
        return {'ok': False, 'error': str(e)}
