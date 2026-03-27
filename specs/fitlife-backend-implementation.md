# FitLife Backend Implementation Plan (Python + MySQL)

## 1. Technical Architecture: Hexagonal (Local Server)
Designed for a local MySQL installation without caching or Docker.

### Core Structure
- **Domain Layer:** Entities (`User`, `Assessment`, `PhysicalRecord`) and Repository Interfaces (ABC). Zero external dependencies.
- **Application Layer:** Use Cases (Interactors) like `RegisterUser`, `LoginUser`, `ProcessAssessment`. Orchestrates logic.
- **Infrastructure Layer:** Adapters for MySQL (SQLAlchemy), Security (Bcrypt/JWT), and SMTP.
- **Adapters (Primary):** FastAPI REST API routes.

---

## 2. Development Phases

### Phase 1: Environment & Project Layout
- Initialize project: `mkdir fitlife-backend && cd fitlife-backend`.
- Package Management: `pip install fastapi uvicorn sqlalchemy pymysql pydantic python-jose[cryptography] passlib[bcrypt] python-dotenv`.
- Structure:
  - `/src/domain`: Entities and Repository Interfaces.
  - `/src/application`: Use Cases and DTOs.
  - `/src/infrastructure`: MySQL implementations and Security adapters.
  - `/src/adapters/api`: FastAPI routes and dependencies.

### Phase 2: User Story 1 & 9 (Auth & Security)
- **Domain:** `User` entity, `Role` enum. `UserRepository` ABC.
- **Infrastructure:** 
  - `SQLAlchemyUserRepository` for MySQL.
  - `MySQLRefreshTokenRepository` (Stores JWT refresh tokens in a database table since Redis is excluded).
  - `PasswordHasher` (Bcrypt adapter).
- **Application:** `RegisterUser`, `LoginUser`, `RefreshToken` use cases.
- **API:** `/auth/register`, `/auth/login`, `/auth/refresh` endpoints.

### Phase 3: User Story 2 (Fitness Assessment)
- **Domain:** `Assessment` entity. `AssessmentCalculator` domain service (weighted scoring 0-100).
- **Application:** `SubmitAssessment` use case.
- **Infrastructure:** `SQLAlchemyAssessmentRepository` for history persistence.
- **API:** `POST /assessments` and `GET /assessments/history`.

### Phase 4: User Story 4, 5, 6 (Progress, Training, Nutrition)
- **Domain:** `PhysicalRecord`, `Routine`, `NutritionPlan` entities.
- **Infrastructure:** Implement corresponding MySQL adapters.
- **Note:** Optimize MySQL indexes for these tables to maintain performance without caching.
- **API:** `POST /physical-records`, `POST /training/routines`, `POST /nutrition/plans`.

### Phase 5: User Story 10 (Profile Management)
- **Application:** `UpdateProfile` use case with optimistic locking (version column in MySQL).
- **Audit:** Implementation of `ProfileAuditLog` as a MySQL adapter.

---

## 3. Deployment & AI Clarity
- **Local DB:** Configure `.env` with `localhost` credentials.
- **Migrations:** Use `Alembic` for version-controlled MySQL schema updates.
- **AI Guidance:** Maintain strict separation. Domain depends on nothing. Infrastructure depends on Application. This ensures testability and clean code.
