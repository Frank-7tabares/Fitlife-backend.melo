"""
Prueba SMTP o envío desde la API.
Uso: python test_smtp.py EMAIL [TOKEN] [NOMBRE]
Ej: python test_smtp.py user@email.com
    python test_smtp.py user@email.com abc123token "Juan"
"""
import asyncio
import sys
import os

from pathlib import Path
# Asegurar que estamos en el directorio del backend
os.chdir(Path(__file__).resolve().parent)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

async def main():
    email = sys.argv[1] if len(sys.argv) > 1 else os.getenv("EMAIL_FROM", "")
    token = sys.argv[2] if len(sys.argv) > 2 else "test-token-123"
    name = sys.argv[3] if len(sys.argv) > 3 else "Usuario"

    if not email or "@" not in email:
        print("Uso: python test_smtp.py EMAIL [TOKEN] [NOMBRE]")
        sys.exit(1)

    from src.infrastructure.email.email_service_smtp import SmtpEmailService

    try:
        sent = await SmtpEmailService.send_password_reset_email(
            to_email=email, reset_token=token, user_name=name
        )
        if sent:
            print("OK")
        else:
            print("FAIL")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
