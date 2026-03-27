# FitLife Backend

Backend REST API para el sistema de gestión de fitness FitLife, construido con **FastAPI** y **Arquitectura Hexagonal (Ports & Adapters)**.

---

## Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Framework | FastAPI 0.109.0 |
| ORM | SQLAlchemy 2.0 (async) |
| Base de datos | MySQL 8.0+ / MariaDB 10.6+ |
| Autenticación | JWT (python-jose) + bcrypt |
| Validación | Pydantic v2 |
| Testing | pytest + pytest-cov + pytest-asyncio |
| Migraciones | Alembic |

---

## Estructura del Proyecto

```
src/
├── domain/              # Lógica de negocio pura (entidades, value objects, puertos)
│   ├── entities/        # Entidades de dominio
│   ├── value_objects/   # Value Objects inmutables (Email, BMI, FitnessScore...)
│   ├── enums/           # Enumeraciones de dominio
│   ├── exceptions/      # Excepciones de dominio
│   ├── services/        # Servicios de dominio (AssessmentCalculator, BMICalculator...)
│   └── repositories/    # Puertos (interfaces ABC)
├── application/         # Casos de uso y orquestación
│   ├── dtos/            # Data Transfer Objects (Pydantic)
│   ├── use_cases/       # Lógica de aplicación
│   ├── ports/           # Interfaces de servicios externos (EmailService)
│   └── services/        # Servicios de aplicación (JWTService, AuditService...)
├── infrastructure/      # Implementaciones técnicas
│   ├── database/        # Modelos ORM, conexión, migraciones
│   ├── repositories/    # Implementaciones SQLAlchemy de los puertos
│   ├── email/           # Servicio SMTP
│   ├── security/        # Hashing de contraseñas, validación
│   └── mappers/         # Conversión ORM ↔ Dominio
├── adapters/            # Adaptadores primarios (HTTP)
│   └── api/
│       ├── routes/      # Endpoints FastAPI
│       ├── middleware/  # Logging, manejo de errores
│       └── dependencies.py  # Inyección de dependencias compartidas
└── config/              # Settings y logging
tests/
├── unit/                # Tests unitarios (mocks)
├── integration/         # Tests de integración (requieren servidor activo)
└── fixtures/            # Fixtures reutilizables
```

---

## Instalación y Configuración

### 1. Clonar y configurar entorno virtual

```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales de MySQL y JWT
```

### 3. Configurar MySQL

```sql
CREATE DATABASE fitlife_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fitlife_user'@'localhost' IDENTIFIED BY 'fitlife_pass';
GRANT ALL PRIVILEGES ON fitlife_db.* TO 'fitlife_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Inicializar base de datos

```bash
python -m src.infrastructure.database.init_db
```

---

## Ejecución

```bash
# Servidor de desarrollo (recomendado: usa run.py para ver logs de peticiones)
python run.py

# O con uvicorn directo (añade --access-log para ver cada petición)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --access-log --log-level info
```

En consola verás líneas como **`[HTTP] POST /api/v1/auth/login -> 401 (12.3ms)`** (código de estado y tiempo).

Variables opcionales en `.env`:

| Variable | Ejemplo | Efecto |
|----------|---------|--------|
| `LOG_LEVEL` | `INFO` | Nivel de logging (`DEBUG`, `INFO`, `WARNING`). |
| `LOG_RESET_LINK` | `true` | Si `DEBUG` es `false`, igual imprime el enlace de restablecer contraseña en consola (solo desarrollo). |

**Olvidé contraseña:** si ves `usuario_en_bd=NO`, ese email no está registrado → no se envía correo (la API responde 200 igual). Si ves `SMTP OK` y no llega el mail, revisa spam o copia el **enlace directo** que sale en consola cuando `DEBUG=true`.

- Documentación API: http://localhost:8000/docs (Swagger) · http://localhost:8000/redoc (ReDoc)

---

## Testing

```bash
# Todos los tests con cobertura
pytest

# Solo tests unitarios (sin servidor)
pytest tests/unit/

# Con reporte HTML
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

**Cobertura mínima requerida: 85%**

---

## Scripts de Utilidad

```bash
# Poblar DB con datos iniciales
python scripts/seed_database.py

# Generar datos de prueba masivos
python scripts/generate_test_data.py
```

---

## Endpoints Principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Registro de usuario |
| POST | `/api/v1/auth/login` | Inicio de sesión |
| POST | `/api/v1/auth/refresh` | Renovar token |
| POST | `/api/v1/auth/password/reset-request` | Solicitar reset de contraseña |
| GET | `/api/v1/users/{id}/profile` | Perfil de usuario |
| PUT | `/api/v1/users/{id}/profile` | Actualizar perfil |
| POST | `/api/v1/assessments/submit` | Enviar evaluación física |
| GET | `/api/v1/assessments/{user_id}/history` | Historial de evaluaciones |
| GET | `/api/v1/instructors` | Listar instructores |
| POST | `/api/v1/instructors/{id}/assign` | Asignar instructor |
| POST | `/api/v1/training/routines` | Crear rutina |
| POST | `/api/v1/nutrition/plans` | Crear plan nutricional |

---

## Arquitectura

El proyecto implementa **Arquitectura Hexagonal (Ports & Adapters)**:

- **Dominio**: Lógica de negocio pura, sin dependencias de frameworks
- **Aplicación**: Casos de uso que orquestan el dominio
- **Infraestructura**: Implementaciones técnicas (MySQL, SMTP, JWT)
- **Adaptadores**: API REST que traduce HTTP ↔ Dominio

---

## Seguridad

- Contraseñas hasheadas con bcrypt
- JWT con expiración configurable (acceso: 30 min, refresco: 30 días)
- CORS configurado para frontend Angular (`http://localhost:4200`)
- Autorización por roles (USER, INSTRUCTOR, ADMIN)
- Historial de contraseñas (no reutilizar últimas 5)
