"""
Arranca el servidor backend. Mantén esta ventana abierta mientras usas el frontend.
"""
import sys
import os
import uvicorn

if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True,
        log_level="info",
    )
