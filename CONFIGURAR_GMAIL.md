# Cómo configurar Gmail para enviar correos (FitLife)

FitLife usa Gmail para enviar correos de **bienvenida** y **restablecer contraseña**. Para que funcione necesitas una **App Password** (contraseña de aplicación).

---

## 1. Crear cuenta Gmail (o usar una existente)

Usa una cuenta nueva o existente. Ejemplo: `mitienda@gmail.com`

---

## 2. Activar verificación en dos pasos (2FA)

1. Entra a [Google Account → Seguridad](https://myaccount.google.com/security)
2. Busca **"Verificación en dos pasos"**
3. Actívala y sigue los pasos (SMS o app Google Authenticator)

> **Importante:** Gmail exige 2FA para crear App Passwords.

---

## 3. Crear App Password

1. Entra a [Google Account → App Passwords](https://myaccount.google.com/apppasswords)  
   (si no ves el enlace, confirma que 2FA está activa)
2. En **"Seleccionar app"** elige **"Correo"**
3. En **"Seleccionar dispositivo"** elige **"Otro (nombre personalizado)"** y escribe `FitLife`
4. Pulsa **"Generar"**
5. Google muestra una contraseña de **16 caracteres**, por ejemplo: `abcd efgh ijkl mnop`
6. **Cópiala** (la usarás en el `.env`)

---

## 4. Configurar el archivo .env

Abre `fitlife-backend-melo/.env` y ajusta estas líneas con tu cuenta y contraseña de aplicación:

```env
# Email (Gmail)
EMAIL_FROM=mitienda@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=mitienda@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
```

- `EMAIL_USER` y `EMAIL_FROM`: **tu email de Gmail**
- `EMAIL_PASSWORD`: **la App Password** (puedes pegarla con espacios; el backend la normaliza)

---

## 5. Reiniciar el backend

Guarda el `.env`, detén el servidor (Ctrl+C) y vuelve a arrancar:

```bash
python run.py
```

---

## Comprobar que funciona

1. Regístrate con un email tuyo en FitLife.
2. Revisa la bandeja (y spam) para el correo de bienvenida.
3. Prueba "Olvidé contraseña" con ese email: debe llegar un correo con el enlace.

Si `DEBUG=True` en `.env`, en la pantalla de "Olvidé contraseña" también verás el enlace directo cuando el correo se envía correctamente.
