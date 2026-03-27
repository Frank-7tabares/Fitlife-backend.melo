# Plan Técnico Backend FitLife - Proyecto Final Universitario
**Arquitectura Hexagonal | Clean Architecture | Python + FastAPI**

**Versión:** 3.0 (Backend)  
**Fecha:** 2026-02-13  
**Contexto:** Trabajo Final Universitario

---

## 1. RESUMEN ARQUITECTÓNICO

### 1.1 Visión General

Backend de FitLife implementado con arquitectura hexagonal (Ports & Adapters) y Clean Architecture, utilizando FastAPI como framework principal. El sistema gestiona autenticación, evaluaciones físicas, asignación de instructores, rutinas de entrenamiento, planes de nutrición y notificaciones básicas.

### 1.2 Stack Tecnológico

- **Framework:** FastAPI (Python 3.11+)
- **Arquitectura:** Hexagonal (Ports & Adapters) + Clean Architecture
- **Base de Datos:** MySQL 8.0+ / MariaDB 10.6+
- **ORM:** SQLAlchemy 2.0+
- **Validación:** Pydantic v2
- **Autenticación:** JWT (PyJWT) + bcrypt
- **Testing:** pytest + pytest-cov + pytest-asyncio
- **Documentación API:** OpenAPI 3.1 (integrado en FastAPI)
- **Linting:** pylint, flake8, black, mypy
- **Email:** SMTP (Gmail/Outlook)

### 1.3 Principios Arquitectónicos

#### Arquitectura Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│         ADAPTADORES PRIMARIOS (Entrada)                  │
│              API REST con FastAPI                        │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   PUERTOS ENTRADA   │
          │  (Interfaces/ABC)   │
          └──────────┬──────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                CAPA DE APLICACIÓN                        │
│    (Use Cases, Application Services, DTOs)              │
│    - Orquestación de lógica de negocio                  │
│    - Validación de entrada/salida                       │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   CAPA DE DOMINIO   │
          │  (Entidades, Value  │
          │   Objects, Domain   │
          │  Services, Reglas)  │
          │  - Lógica de negocio│
          │  - Sin dependencias │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   PUERTOS SALIDA    │
          │  (Interfaces/ABC)   │
          └──────────┬──────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│       ADAPTADORES SECUNDARIOS (Salida)                  │
│    MySQL/MariaDB + SMTP (Email) + File System           │
└─────────────────────────────────────────────────────────┘
```

#### Separación de Responsabilidades (Clean Architecture)

1. **Dominio (Domain):** Lógica de negocio pura, independiente de frameworks
2. **Aplicación (Application):** Orquestación de casos de uso
3. **Infraestructura (Infrastructure):** Implementaciones técnicas (DB, email)
4. **Adaptadores (Adapters):** Traducción entre mundo exterior (HTTP) y dominio

### 1.4 Decisiones Arquitectónicas Clave

| Decisión | Justificación Académica | Riesgo/Mitigación |
|----------|-------------------------|-------------------|
| Arquitectura Hexagonal | - Demostración de desacoplamiento<br>- Testabilidad superior<br>- Principios SOLID | Riesgo: Mayor complejidad inicial<br>Mitigación: Documentación clara |
| MySQL/MariaDB | - Base de datos relacional estándar<br>- ACID completo<br>- Amplia documentación | Riesgo: Configuración inicial<br>Mitigación: Instrucciones detalladas |
| FastAPI | - Moderno y educativo<br>- Validación automática (Pydantic)<br>- Documentación OpenAPI integrada | Riesgo: Menos ejemplos que Django<br>Mitigación: Documentación oficial |
| JWT sin servidor externo | - Tokens almacenados en MySQL<br>- No requiere infraestructura adicional | Riesgo: Invalidación manual<br>Mitigación: Tabla de tokens revocados |
| Sin cache externo | - Simplifica arquitectura<br>- MySQL suficiente para escala académica | Riesgo: Menor performance<br>Mitigación: Índices optimizados |
| SMTP simple | - Email básico sin dependencias<br>- Configurable con Gmail/Outlook | Riesgo: Rate limits<br>Mitigación: Documentar alternativas |

---

## 2. ESTRUCTURA DEL PROYECTO

```
fitlife-backend/
├── src/
│   ├── __init__.py
│   ├── main.py                          # Entry point FastAPI
│   │
│   ├── domain/                          # CAPA DE DOMINIO
│   │   ├── __init__.py
│   │   ├── entities/                    # Entidades de negocio
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── instructor.py
│   │   │   ├── assessment.py
│   │   │   ├── physical_record.py
│   │   │   ├── training.py
│   │   │   ├── nutrition.py
│   │   │   └── message.py
│   │   ├── value_objects/               # Value Objects inmutables
│   │   │   ├── __init__.py
│   │   │   ├── email.py
│   │   │   ├── password.py
│   │   │   ├── fitness_score.py
│   │   │   ├── body_age.py
│   │   │   └── bmi.py
│   │   ├── enums/
│   │   │   ├── __init__.py
│   │   │   ├── user_role.py
│   │   │   ├── fitness_level.py
│   │   │   └── fitness_goal.py
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user_exceptions.py
│   │   │   └── validation_exceptions.py
│   │   ├── services/                    # Servicios de dominio
│   │   │   ├── __init__.py
│   │   │   ├── assessment_calculator.py
│   │   │   ├── password_validator.py
│   │   │   └── bmi_calculator.py
│   │   └── repositories/                # PUERTOS (Interfaces ABC)
│   │       ├── __init__.py
│   │       ├── user_repository.py
│   │       ├── instructor_repository.py
│   │       ├── assessment_repository.py
│   │       ├── training_repository.py
│   │       └── nutrition_repository.py
│   │
│   ├── application/                     # CAPA DE APLICACIÓN
│   │   ├── __init__.py
│   │   ├── dtos/
│   │   │   ├── __init__.py
│   │   │   ├── auth_dtos.py
│   │   │   ├── user_dtos.py
│   │   │   ├── assessment_dtos.py
│   │   │   ├── training_dtos.py
│   │   │   └── nutrition_dtos.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── auth/
│   │   │   │   ├── register_user.py
│   │   │   │   ├── login_user.py
│   │   │   │   ├── refresh_token.py
│   │   │   │   ├── reset_password_request.py
│   │   │   │   ├── reset_password.py
│   │   │   │   └── change_password.py
│   │   │   ├── users/
│   │   │   ├── assessments/
│   │   │   ├── instructors/
│   │   │   ├── training/
│   │   │   └── nutrition/
│   │   ├── ports/
│   │   │   ├── __init__.py
│   │   │   └── email_service.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── jwt_service.py
│   │       ├── audit_service.py
│   │       └── notification_service.py
│   │
│   ├── infrastructure/                  # CAPA DE INFRAESTRUCTURA
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── base.py
│   │   │   └── models/
│   │   │       ├── user_model.py
│   │   │       ├── instructor_model.py
│   │   │       └── ...
│   │   ├── repositories/
│   │   │   ├── sqlalchemy_user_repository.py
│   │   │   └── ...
│   │   ├── email/
│   │   │   ├── smtp_email_service.py
│   │   │   └── templates/
│   │   ├── security/
│   │   │   ├── password_hasher.py
│   │   │   └── token_manager.py
│   │   └── mappers/
│   │       ├── user_mapper.py
│   │       └── ...
│   │
│   ├── adapters/                        # ADAPTADORES PRIMARIOS
│   │   ├── __init__.py
│   │   └── api/
│   │       ├── main.py
│   │       ├── dependencies.py
│   │       ├── middleware/
│   │       │   ├── auth_middleware.py
│   │       │   ├── error_handler.py
│   │       │   ├── cors_middleware.py
│   │       │   └── logging_middleware.py
│   │       ├── routes/
│   │       │   ├── auth_routes.py
│   │       │   ├── user_routes.py
│   │       │   ├── instructor_routes.py
│   │       │   ├── assessment_routes.py
│   │       │   ├── training_routes.py
│   │       │   ├── nutrition_routes.py
│   │       │   └── message_routes.py
│   │       └── schemas/
│   │           ├── auth_schemas.py
│   │           └── ...
│   │
│   └── config/
│       ├── __init__.py
│       ├── settings.py
│       └── logging_config.py
│
├── tests/                               # PRUEBAS (>= 80%)
│   ├── __init__.py
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   │   ├── test_database.py
│   │   └── test_api_endpoints.py
│   ├── fixtures/
│   │   ├── database_fixtures.py
│   │   └── mock_fixtures.py
│   └── conftest.py
│
├── scripts/
│   ├── seed_database.py
│   └── generate_test_data.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── pyproject.toml
└── README.md
```

---

## 3. FASES DEL PROYECTO

### FASE 0: Configuración del Entorno

#### Objetivo
Preparar el entorno de desarrollo local con todas las herramientas necesarias.

#### Entregables

1. **Entorno Python:**
   - Entorno virtual configurado
   - `requirements.txt` y `requirements-dev.txt`
   - Estructura de carpetas según arquitectura hexagonal

2. **Base de Datos:**
   - MySQL instalado y configurado
   - Base de datos `fitlife_db` creada
   - Usuario con permisos configurado

3. **Herramientas de Desarrollo:**
   - Configuración de pytest con cobertura
   - Linters (black, flake8, mypy)
   - VSCode/PyCharm configurado

#### Actividades Detalladas

**1. Inicializar Backend:**

```bash
# Crear directorio y entorno virtual
mkdir -p fitlife-backend && cd fitlife-backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias básicas
pip install fastapi uvicorn sqlalchemy pymysql pydantic
```

**2. Crear `requirements.txt`:**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pymysql==1.1.0
aiomysql==0.2.0
cryptography==42.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
```

**3. Crear `requirements-dev.txt`:**

```
-r requirements.txt
pytest==7.4.4
pytest-cov==4.1.0
pytest-asyncio==0.23.3
black==24.1.1
flake8==7.0.0
mypy==1.8.0
httpx==0.26.0
```

**4. Configurar MySQL:**

```sql
-- Crear base de datos y usuario
CREATE DATABASE fitlife_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fitlife_user'@'localhost' IDENTIFIED BY 'fitlife_pass';
GRANT ALL PRIVILEGES ON fitlife_db.* TO 'fitlife_user'@'localhost';
FLUSH PRIVILEGES;
```

**5. Crear `.env.example`:**

```
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=fitlife_user
DB_PASSWORD=fitlife_pass
DB_NAME=fitlife_db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@fitlife.com

# App
DEBUG=True
API_VERSION=v1
CORS_ORIGINS=http://localhost:4200
```

**6. Configurar pytest (`pytest.ini`):**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
asyncio_mode = auto
```

#### Criterios de Aceptación
- [ ] Entorno virtual Python 3.11+ configurado
- [ ] MySQL levantado y accesible
- [ ] Backend responde en `http://localhost:8000` con mensaje básico
- [ ] `pytest` ejecuta sin errores (sin tests aún)
- [ ] Linters (black, flake8) pasan sin errores
- [ ] Estructura de carpetas creada

---

### FASE 1: Capa de Dominio (Lógica de Negocio Pura)

#### Objetivo
Implementar entidades de dominio, value objects, servicios de dominio y puertos (interfaces) sin dependencias de frameworks.

#### Entregables

1. **Entidades de Dominio:**
   - `User`, `UserProfile`
   - `Instructor`, `InstructorAssignment`
   - `Assessment`, `AssessmentQuestion`
   - `PhysicalRecord`
   - `Exercise`, `Routine`
   - `NutritionPlan`, `DailyMeal`
   - `Message`

2. **Value Objects:**
   - `Email` (con validación)
   - `FitnessScore` (0-100)
   - `BodyAge`
   - `BMI`
   - `HashedPassword`

3. **Servicios de Dominio:**
   - `AssessmentCalculator`: Cálculo de fitness score y body age
   - `PasswordValidator`: Validación de contraseñas
   - `BMICalculator`: Cálculo de IMC

4. **Puertos (Interfaces ABC):**
   - `UserRepository`
   - `InstructorRepository`
   - `AssessmentRepository`
   - `TrainingRepository`
   - `NutritionRepository`

5. **Excepciones de Dominio:**
   - `DomainException` (base)
   - `InvalidEmailException`
   - `WeakPasswordException`
   - `UserNotFoundException`

#### Ejemplo de Implementación

**Value Object `Email`:**

```python
# src/domain/value_objects/email.py
import re
from dataclasses import dataclass
from ..exceptions.validation_exceptions import InvalidEmailException

@dataclass(frozen=True)
class Email:
    """Value Object para email con validación."""
    
    value: str
    
    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidEmailException(f"Formato de email inválido: {self.value}")
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value
```

**Servicio de Dominio `AssessmentCalculator`:**

```python
# src/domain/services/assessment_calculator.py
from typing import Dict, Any
from decimal import Decimal

class AssessmentCalculator:
    """Servicio de dominio para cálculos de evaluación física."""
    
    def calculate_fitness_score(
        self,
        responses: Dict[str, Any],
        questions: Dict[str, Any]
    ) -> Decimal:
        """Calcula el fitness score (0-100) basado en respuestas ponderadas."""
        total_weight = Decimal('0')
        weighted_sum = Decimal('0')
        
        for question_id, answer in responses.items():
            question = questions.get(question_id)
            if not question:
                continue
            
            weight = Decimal(str(question['weight']))
            normalized_score = self._normalize_answer(answer, question)
            
            weighted_sum += normalized_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return Decimal('0')
        
        return (weighted_sum / total_weight).quantize(Decimal('0.01'))
    
    def calculate_body_age(
        self,
        real_age: int,
        bmi: Decimal,
        body_fat_percentage: Decimal,
        functional_score: Decimal,
        habits_score: Decimal
    ) -> Decimal:
        """Calcula edad corporal estimada."""
        bmi_adj = self._calculate_bmi_adjustment(bmi)
        fat_adj = self._calculate_body_fat_adjustment(body_fat_percentage)
        func_adj = self._calculate_functional_adjustment(functional_score)
        habits_adj = self._calculate_habits_adjustment(habits_score)
        
        body_age = Decimal(str(real_age)) + bmi_adj + fat_adj + func_adj + habits_adj
        
        return max(Decimal('18'), min(body_age, Decimal('120')))
```

**Puerto (Interfaz) `UserRepository`:**

```python
# src/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ..entities.user import User
from ..value_objects.email import Email

class UserRepository(ABC):
    """Puerto de salida para persistencia de usuarios."""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Persiste un usuario nuevo."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca usuario por ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Busca usuario por email."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza usuario existente."""
        pass
```

#### Tests Unitarios de Dominio

```python
# tests/unit/domain/value_objects/test_email.py
import pytest
from src.domain.value_objects.email import Email
from src.domain.exceptions.validation_exceptions import InvalidEmailException

def test_email_valid():
    email = Email("user@example.com")
    assert str(email) == "user@example.com"

def test_email_invalid_format():
    with pytest.raises(InvalidEmailException):
        Email("invalid-email")
```

#### Criterios de Aceptación
- [ ] Todas las entidades de dominio implementadas
- [ ] Todos los value objects validan correctamente
- [ ] Servicios de dominio con lógica completa
- [ ] Todos los puertos (ABC) definidos
- [ ] **Cobertura >= 90% en capa de dominio**
- [ ] No hay dependencias de frameworks externos
- [ ] Todas las excepciones heredan de `DomainException`

---

### FASE 2: Capa de Infraestructura

#### Objetivo
Implementar los adaptadores secundarios: repositorios con SQLAlchemy, servicio de email SMTP, y seguridad (hashing, JWT).

#### Entregables

1. **Configuración de Base de Datos:**
   - SQLAlchemy engine y session factory
   - Modelos ORM para todas las tablas
   - Script de creación de esquema

2. **Repositorios (Implementaciones):**
   - `SQLAlchemyUserRepository`
   - `SQLAlchemyInstructorRepository`
   - `SQLAlchemyAssessmentRepository`
   - `SQLAlchemyTrainingRepository`
   - `SQLAlchemyNutritionRepository`

3. **Servicios de Infraestructura:**
   - `SMTPEmailService`
   - `BCryptPasswordHasher`
   - `JWTTokenManager`

4. **Mappers:**
   - Conversión entre modelos ORM y entidades de dominio

#### Ejemplo de Implementación

**Configuración SQLAlchemy:**

```python
# src/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ...config.settings import settings

DATABASE_URL = f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

**Repositorio SQLAlchemy:**

```python
# src/infrastructure/repositories/sqlalchemy_user_repository.py
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.repositories.user_repository import UserRepository
from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ..database.models.user_model import UserModel
from ..mappers.user_mapper import UserMapper

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = UserMapper()
    
    async def save(self, user: User) -> User:
        user_model = self.mapper.to_model(user)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        return self.mapper.to_entity(user_model)
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self.mapper.to_entity(user_model) if user_model else None
```

**Servicio de Email SMTP:**

```python
# src/infrastructure/email/smtp_email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ...application.ports.email_service import EmailService
from ...config.settings import settings

class SMTPEmailService(EmailService):
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: str
    ) -> bool:
        try:
            reset_url = f"http://localhost:4200/reset-password?token={reset_token}"
            
            html_content = f"""
            <html>
            <body>
                <h2>Restablecimiento de Contraseña - FitLife</h2>
                <p>Hola {user_name},</p>
                <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
                <p><a href="{reset_url}">Restablecer Contraseña</a></p>
                <p>Este enlace expirará en 1 hora.</p>
            </body>
            </html>
            """
            
            return await self._send_email(to_email, "Restablecimiento de Contraseña", html_content)
        except Exception as e:
            print(f"Error sending reset email: {e}")
            return False
```

#### Criterios de Aceptación
- [ ] Todas las tablas se crean correctamente
- [ ] Todos los repositorios implementan sus puertos
- [ ] **Cobertura >= 80% en repositorios**
- [ ] Conexión a MySQL funciona
- [ ] Email SMTP envía correctamente
- [ ] Mappers convierten correctamente entre ORM y dominio

---

### FASE 3: Capa de Aplicación (Casos de Uso)

#### Objetivo
Implementar los casos de uso que orquestan la lógica de negocio.

#### Entregables

1. **DTOs:** Request/Response para cada caso de uso

2. **Casos de Uso - Autenticación:**
   - `RegisterUser`
   - `LoginUser`
   - `RefreshToken`
   - `ResetPasswordRequest`
   - `ResetPassword`
   - `ChangePassword`

3. **Casos de Uso - Usuarios:**
   - `GetUserProfile`
   - `UpdateUserProfile`
   - `GetProfileAuditLog`

4. **Casos de Uso - Evaluación:**
   - `SubmitAssessment`
   - `GetAssessmentHistory`

5. **Casos de Uso - Instructores:**
   - `ListInstructors`
   - `AssignInstructor`
   - `RateInstructor`

6. **Casos de Uso - Entrenamiento:**
   - `CreateRoutine`
   - `AssignRoutine`
   - `CompleteWorkout`

7. **Casos de Uso - Nutrición:**
   - `CreateNutritionPlan`
   - `GetActiveNutritionPlan`

8. **Servicios de Aplicación:**
   - `JWTService`
   - `AuditService`
   - `NotificationService`

#### Ejemplo de Implementación

```python
# src/application/use_cases/auth/register_user.py
from uuid import uuid4
from datetime import datetime
from ....domain.entities.user import User
from ....domain.value_objects.email import Email
from ....domain.repositories.user_repository import UserRepository
from ...dtos.auth_dtos import RegisterUserRequest, RegisterUserResponse

class RegisterUser:
    """Caso de uso: Registro de nuevo usuario."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher,
        jwt_service
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.jwt_service = jwt_service
    
    async def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        # 1. Verificar email único
        email = Email(request.email)
        if await self.user_repository.exists_by_email(email):
            raise EmailAlreadyExistsException(f"Email {request.email} ya registrado")
        
        # 2. Hashear contraseña
        password_hash = self.password_hasher.hash(request.password)
        
        # 3. Crear entidad User
        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # 4. Persistir
        saved_user = await self.user_repository.save(user)
        
        # 5. Generar tokens JWT
        access_token, expires_in = self.jwt_service.create_access_token(
            user_id=str(saved_user.id),
            role=saved_user.role.value
        )
        
        return RegisterUserResponse(
            user_id=str(saved_user.id),
            email=str(saved_user.email),
            access_token=access_token,
            expires_in=expires_in
        )
```

#### Criterios de Aceptación
- [ ] Todos los casos de uso implementados
- [ ] DTOs validan correctamente con Pydantic
- [ ] **Cobertura >= 85% en capa de aplicación**
- [ ] JWTService genera y valida tokens
- [ ] Tests unitarios usan mocks

---

### FASE 4: Adaptadores Primarios (API REST)

#### Objetivo
Implementar los endpoints REST con FastAPI.

#### Entregables

1. **Rutas FastAPI:**
   - `/api/auth/*` - Autenticación
   - `/api/users/*` - Usuarios
   - `/api/instructors/*` - Instructores
   - `/api/assessments/*` - Evaluaciones
   - `/api/training/*` - Entrenamiento
   - `/api/nutrition/*` - Nutrición
   - `/api/messages/*` - Mensajes

2. **Middleware:**
   - Autenticación JWT
   - Manejo de errores
   - CORS
   - Logging

3. **Schemas Pydantic:** Request/Response para cada endpoint

#### Ejemplo de Implementación

```python
# src/adapters/api/routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException
from ....application.use_cases.auth.register_user import RegisterUser
from ....application.dtos.auth_dtos import RegisterUserRequest, RegisterUserResponse
from ..dependencies import get_register_user_use_case

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=RegisterUserResponse, status_code=201)
async def register(
    request: RegisterUserRequest,
    use_case: RegisterUser = Depends(get_register_user_use_case)
):
    """Registra un nuevo usuario."""
    try:
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Criterios de Aceptación
- [ ] Todos los endpoints REST funcionan
- [ ] Documentación OpenAPI en `/docs`
- [ ] Middleware de JWT valida tokens
- [ ] CORS configurado para Angular
- [ ] **Tests de integración >= 80%**
- [ ] Manejo de errores consistente

---

### FASE 5: Integración y Testing

#### Objetivo
Asegurar que todas las capas funcionan correctamente juntas con cobertura >= 80%.

#### Actividades

1. **Tests de Integración:**
   - Backend + MySQL
   - Endpoints completos
   - Flujos end-to-end

2. **Verificación de Cobertura:**
   - Ejecutar `pytest --cov=src --cov-report=html`
   - Verificar >= 80% global
   - Identificar gaps de cobertura

3. **Tests de Flujos Principales:**
   - Registro → Login → Evaluación → Asignación de instructor
   - Creación de rutina → Asignación → Completación
   - Restablecimiento de contraseña completo

4. **Validaciones de Seguridad:**
   - Tokens JWT válidos/inválidos
   - Autorización por roles
   - Validación de contraseñas

#### Ejemplo de Test de Integración

```python
# tests/integration/test_api_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # Registrar usuario
    register_response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    })
    assert register_response.status_code == 201
    data = register_response.json()
    assert "access_token" in data
    
    # Login con credenciales
    login_response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
```

#### Criterios de Aceptación
- [ ] Cobertura global >= 80%
- [ ] Todos los tests de integración pasan
- [ ] No hay errores de linter
- [ ] Documentación completa
- [ ] Script de seed funciona
- [ ] Logs de aplicación funcionan

---

## 4. ESTRATEGIA DE PRUEBAS

### 4.1 Cobertura Mínima: 80% Global

| Capa | Tipo de Test | Cobertura Objetivo |
|------|--------------|-------------------|
| Dominio | Unitarios | >= 90% |
| Aplicación | Unitarios + Integración | >= 85% |
| Infraestructura | Integración | >= 80% |
| API | Integración | >= 80% |

### 4.2 Herramientas

- **pytest:** Framework de testing
- **pytest-cov:** Medición de cobertura
- **pytest-asyncio:** Tests asíncronos
- **httpx:** Cliente HTTP para tests
- **faker:** Generación de datos de prueba

### 4.3 Ejecución de Tests

```bash
# Ejecutar todos los tests con cobertura
pytest --cov=src --cov-report=html --cov-report=term-missing

# Ejecutar solo tests unitarios
pytest tests/unit/

# Ejecutar con verbosidad
pytest -v --cov=src
```

---

## 5. NOTIFICACIONES BÁSICAS

### 5.1 Funcionalidad Básica

El sistema implementa notificaciones básicas mediante:
- **Email SMTP:** Notificaciones críticas (restablecimiento, bienvenida)
- **Mensajes del Sistema:** Almacenados en base de datos

### 5.2 Tipos de Notificaciones

**Notificaciones por Email:**
- Bienvenida al registrarse
- Restablecimiento de contraseña
- Cambio de contraseña exitoso

**Mensajes del Sistema:**
- Asignación de nueva rutina
- Asignación de plan de nutrición
- Mensajes de instructor

### 5.3 Implementación

```python
# src/application/services/notification_service.py
class NotificationService:
    async def send_assignment_notification(
        self,
        user_id: UUID,
        assignment_type: str,
        details: Dict
    ) -> None:
        message = Message(
            id=uuid4(),
            sender_id=None,  # Sistema
            recipient_id=user_id,
            content=f"Se te ha asignado un nuevo {assignment_type}",
            message_type="SYSTEM_NOTIFICATION",
            created_at=datetime.utcnow()
        )
        await self.message_repository.save(message)
```

---

## 6. SEGURIDAD

### 6.1 Autenticación JWT

- Token de acceso: Expiración 30 minutos
- Token de refresco: Expiración 30 días
- Algoritmo: HS256
- Almacenamiento: Tokens revocados en MySQL

### 6.2 Autorización RBAC

- USER: Acceso a su propio perfil
- INSTRUCTOR: Crear rutinas y planes
- ADMIN: Acceso completo

### 6.3 Validación de Contraseñas

- Mínimo 8 caracteres
- 1 mayúscula, 1 minúscula, 1 número, 1 especial
- No reutilizar últimas 5 contraseñas

### 6.4 Protección contra Ataques

- Rate limiting en endpoints sensibles
- SQLAlchemy ORM (previene SQL injection)
- Sanitización de entrada
- CORS configurado

---

## 7. CRITERIOS DE ACEPTACIÓN

### 7.1 Funcionalidad
- [ ] Todas las historias de usuario implementadas
- [ ] Endpoints REST funcionan
- [ ] Autenticación JWT funciona
- [ ] Notificaciones básicas funcionan

### 7.2 Calidad
- [ ] Cobertura >= 80%
- [ ] Linters pasan sin errores
- [ ] Arquitectura hexagonal respetada
- [ ] Documentación completa

### 7.3 Seguridad
- [ ] Contraseñas hasheadas
- [ ] Tokens JWT validados
- [ ] Rate limiting implementado
- [ ] CORS configurado

---

## 8. ESQUEMA DE BASE DE DATOS

### 8.1 Contexto de Identidad

```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'INSTRUCTOR', 'ADMIN') NOT NULL DEFAULT 'USER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_profiles (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY') NULL,
    height_cm DECIMAL(5,2) NULL,
    fitness_goal ENUM('WEIGHT_LOSS', 'MUSCLE_GAIN', 'GENERAL_FITNESS', 'ATHLETIC_PERFORMANCE') NULL,
    activity_level ENUM('SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE', 'VERY_ACTIVE') NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE password_history (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE revoked_tokens (
    id CHAR(36) PRIMARY KEY,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    user_id CHAR(36) NOT NULL,
    revoked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 8.2 Contexto de Instructores

```sql
CREATE TABLE instructors (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) UNIQUE NOT NULL,
    certifications JSON NOT NULL,
    specializations JSON NULL,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    active_users_count INT DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE instructor_assignments (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    instructor_id CHAR(36) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE,
    INDEX idx_user_active (user_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 8.3 Contexto de Evaluación

```sql
CREATE TABLE assessment_questions (
    id CHAR(36) PRIMARY KEY,
    question_type ENUM('NUMERIC', 'SINGLE_CHOICE', 'MULTIPLE_CHOICE', 'YES_NO') NOT NULL,
    category ENUM('PHYSICAL', 'FUNCTIONAL', 'HABITS', 'ALERTS') NOT NULL,
    label VARCHAR(500) NOT NULL,
    weight DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    constraints JSON NULL,
    display_order INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE assessments (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    responses JSON NOT NULL,
    fitness_score DECIMAL(5,2) NOT NULL,
    fitness_category ENUM('EXCELLENT', 'GOOD', 'FAIR', 'POOR') NOT NULL,
    real_age INT NOT NULL,
    body_age DECIMAL(5,2) NOT NULL,
    age_difference DECIMAL(5,2) NOT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_submitted (user_id, submitted_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 8.4 Demás Contextos

**Physical Records, Training, Nutrition, Messages:** Seguir estructura similar con claves foráneas, índices y tipos de datos apropiados.

---

## FIN DEL PLAN TÉCNICO BACKEND

Este plan está estructurado por fases de implementación, desde la configuración inicial hasta la integración y testing, con cobertura mínima de 80%, notificaciones básicas y arquitectura hexagonal.
