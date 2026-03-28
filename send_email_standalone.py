import os
import sys
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
DIR = Path(__file__).resolve().parent
os.chdir(DIR)
env_file = DIR / '.env'
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        pass

def main():
    if len(sys.argv) < 3:
        print('Uso: python send_email_standalone.py EMAIL TOKEN [NOMBRE]', file=sys.stderr)
        sys.exit(1)
    to_email = sys.argv[1].strip()
    token = sys.argv[2].strip()
    name = sys.argv[3].strip() if len(sys.argv) > 3 else 'Usuario'
    if '@' not in to_email:
        print('Email invalido', file=sys.stderr)
        sys.exit(1)
    host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    port = int(os.getenv('EMAIL_PORT', '587'))
    user = (os.getenv('EMAIL_USER') or '').strip()
    pwd = ''.join((os.getenv('EMAIL_PASSWORD') or '').split())
    frontend = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    from_addr = user or os.getenv('EMAIL_FROM', '')
    if not user or not pwd or 'your-' in user.lower():
        print('SMTP no configurado en .env', file=sys.stderr)
        sys.exit(1)
    reset_url = f"{frontend.rstrip('/')}/auth/reset-password?token={token}"
    html = f'<html><body>\n<h2>Hola {name},</h2>\n<p>Recibimos una solicitud para restablecer tu contraseña.</p>\n<p><a href="{reset_url}" style="background:#4CAF50;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Restablecer contraseña</a></p>\n<p>Este enlace expira en 1 hora.</p>\n<p>Saludos, FitLife</p>\n</body></html>'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Restablece tu contraseña - FitLife'
    msg['From'] = formataddr(('FitLife', from_addr))
    msg['To'] = to_email
    msg.attach(MIMEText(html, 'html'))
    try:
        if port == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=25) as s:
                s.login(user, pwd)
                s.sendmail(from_addr, [to_email], msg.as_string())
        else:
            s = smtplib.SMTP(host, port, timeout=25)
            s.ehlo()
            s.starttls(context=ssl.create_default_context())
            s.ehlo()
            s.login(user, pwd)
            s.sendmail(from_addr, [to_email], msg.as_string())
            s.quit()
        print('OK')
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
if __name__ == '__main__':
    main()
