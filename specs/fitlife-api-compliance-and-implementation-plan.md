# Validación de APIs frente a especificación FitLife y plan de implementación

**Documento de referencia:** Validación del backend FitLife frente a [fitlife.spec.es.md](fitlife.spec.es.md) y plan de implementación por fases para cerrar brechas. Actualizar este documento a medida que se completen fases.

---

## Resumen ejecutivo

Se comparó la implementación actual del backend (rutas en `src/adapters/api/routes/`, use cases, DTOs y modelos) con las historias de usuario y criterios de aceptación de la especificación, así como con los requisitos funcionales (RF) referenciados.

- **Cumple:** Historias 4 (progreso físico) y 6 (nutrición) en su totalidad; Historias 2 (evaluación) y 5 (rutinas) con desvíos menores; partes de Historias 1 (auth) y 10 (perfil).
- **No cumple o parcial:** Historia 1 (falta refresh, 409 en email duplicado, tokens en registro); Historia 3 (instructores no implementada); Historia 9 (contraseñas no implementada); Historia 10 (perfil incompleto, sin autorización 403 ni auditoría consultable); Historias 7 y 8 (mensajería y recordatorios no implementadas).
- **Prefijo base:** Todas las rutas bajo `/api/v1` (cumple RF-106 y CE-018).

---

## 1. Cumplimiento por historia de usuario

### Historia 1 – Registro y autenticación (P1)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /auth/register → 201 y creación de cuenta | Cumple | `auth_routes.py` devuelve 201 y RegisterResponse (id, email, role, full_name, created_at, access_token, refresh_token) |
| Espec: "proporciona tokens de acceso y actualización" en registro | Cumple | RegisterResponse devuelve tokens de acceso y actualización (RF-001, RF-005) |
| POST /auth/login → tokens JWT | Cumple | Login devuelve TokenResponse con access_token y refresh_token |
| POST /auth/refresh | Cumple | Endpoint implementado; valida refresh_token en BD, revoca anterior, emite nuevos tokens (RF-006) |
| Registro con email duplicado → 409 Conflict | Cumple | EmailAlreadyRegisteredError → HTTPException 409 Conflict en auth_routes.py |
| RF-010 (refresh tokens en Redis/almacén) | Cumple | RefreshTokenModel con tabla en MySQL; validación y revocación en RefreshTokenRepository (find_valid_user_id, revoke, save) |

**Brechas:** Ninguna. Historia 1 completamente implementada (Fase 1 - parte Auth).

---

### Historia 2 – Evaluación física inicial (P1)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /assessments → puntuación, edad corporal, categoría | Cumple | SubmitAssessment + AssessmentCalculator |
| BODY_OLDER / BODY_YOUNGER / BODY_EQUAL | Cumple | AssessmentCalculator.compare_body_age |
| GET historial de evaluaciones | Cumple | GET /assessments/user/{user_id} y GET /users/{id}/assessments (alias) |
| Ruta del historial | Cumple | GET /users/{id}/assessments implementado como alias (Fase 4) |
| RF-058 descargo edad corporal | Cumple | AssessmentResponse.body_age_disclaimer en POST e historial |

**Brechas:** Ninguna. Cerrada con alias de ruta y descargo en respuesta.

---

### Historia 3 – Instructores (P1)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| GET /instructors | Cumple | Lista con nombre, certificaciones, calificación y conteo de usuarios activos |
| GET /instructors/{id} | Cumple | Perfil completo del instructor |
| POST /users/{id}/assign-instructor | Cumple | Asigna instructor; desactiva asignación anterior (RF-046, RF-047) |
| Cambiar instructor (desactivar anterior) | Cumple | assign_instructor desactiva la activa antes de crear la nueva |
| POST /instructors/{id}/rate | Cumple | Calificación 1-5; solo si usuario asignado (RF-048, RF-049, RF-050) |

**Brechas:** Ninguna. Implementado: entidades Instructor, InstructorAssignment, InstructorRating; repositorios; use cases; rutas. POST /instructors (crear instructor) añadido para seed/admin.

---

### Historia 4 – Seguimiento de progreso físico (P2)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /users/{id}/physical-records | Cumple | Path y body correctos |
| GET /users/{id}/physical-records | Cumple | Historial ordenado por `recorded_at` DESC; respuesta con `records` y `total` |
| IMC calculado, no persistido (RF-063) | Cumple | `PhysicalRecord.bmi` como property |
| RF-061: activity_level como enum | Cumple | `ActivityLevel` enum: SEDENTARY, LIGHT, MODERATE, ACTIVE, VERY_ACTIVE |
| RF-064: campo `recordedAt` | Cumple | Campo `recorded_at` en entidad, DTO y modelo; usuario puede especificarlo; default UTC now |
| RF-066: orden por `recordedAt` DESC | Cumple | Repositorio ordena por `recorded_at` descendente |
| RF-067: validación rangos realistas | Cumple | peso 1–500 kg, altura 50–300 cm, grasa corporal 2–70%, cintura/cadera 30–300 cm |

**Brechas:** Ninguna. Historia completamente implementada (Fase 4).

**Decisiones de implementación:**
- Se añadió `PhysicalRecordRepository` (interfaz abstracta) en `src/domain/repositories/` para mantener arquitectura limpia.
- `recorded_at` es opcional en el request; si no se provee, se usa la fecha/hora actual en UTC.
- La respuesta del GET devuelve `PhysicalRecordListResponse` con `records` (lista) y `total` (conteo).

---

### Historia 5 – Rutinas y entrenamiento (P2)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /training/routines | Cumple | |
| POST /users/{id}/routines/assign | Cumple | |
| GET /users/{id}/routines/active | Cumple | |
| POST completar entrenamiento | Cumple | POST /workouts/complete con user_id y body |
| Spec: POST /workouts/{id}/complete | Desvío | Spec habla de "id" (¿workout?); impl usa user_id. Aceptable si se documenta |
| Ver demostración de ejercicio (nombre, grupo muscular, dificultad, URL YouTube) | **No implementado** | Exercise no tiene URL; ExerciseModel no tiene columna demo/youtube |

**Brechas:** (1) Biblioteca de ejercicios con URL de demostración (RF-071): modelo + posible GET /exercises/{id} o inclusión en rutina. (2) Decidir si POST /workouts/complete debe identificar sesión por id.

---

### Historia 6 – Plan de nutrición (P2)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /nutrition/plans | Cumple | user_id como parámetro (query/path según impl) |
| GET /users/{id}/nutrition/active | Cumple | |
| Plan semanal por días/comidas | Cumple | NutritionPlan con daily_plans y Meal |

**Brechas:** Ninguna crítica. Opcional: alinear creación a POST /users/{id}/nutrition/plans si la spec lo indica.

---

### Historia 7 – Mensajería (P3)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /messages | **No implementado** | |
| GET /messages/user/{id} | **No implementado** | |
| Mensajes automáticos al asignar rutina/plan | **No implementado** | |

**Brechas:** Contexto de mensajería completo (entidad Message, repositorio, use cases, rutas).

---

### Historia 8 – Recordatorios (P3)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /reminders, GET /reminders | **No implementado** | |
| Notificaciones push (Firebase) | **No implementado** | |

**Brechas:** Contexto de recordatorios y notificaciones (Reminder, programación, integración FCM).

---

### Historia 9 – Restablecimiento y cambio de contraseña (P1)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| POST /auth/password/reset-request | **No implementado** | RF-011 a RF-025 |
| POST /auth/password/reset | **No implementado** | |
| POST /auth/password/change | **No implementado** | RF-020, RF-021 |
| Token 1h, correo, complejidad, últimas 5 contraseñas, rate limiting | **No implementado** | |

**Brechas:** Flujo completo de contraseña: entidades PasswordResetToken, PasswordHistory; envío de email; validación de complejidad; historial de contraseñas; rate limiting; endpoints.

---

### Historia 10 – Actualización de perfil (P2)

| Criterio | Estado | Detalle |
|----------|--------|---------|
| GET /users/{id}/profile | Cumple | |
| PATCH /users/{id}/profile | Cumple | Con bloqueo optimista (version) |
| Campos editables (nombre, edad, género, altura, objetivos, actividad) | Parcial | UpdateProfileRequest tiene los campos; UpdateProfile solo aplica full_name |
| UserProfileResponse con todos los campos de perfil | Parcial | Falta edad, género, altura, objetivos, nivel de actividad en respuesta |
| 409 por correo ya usado (RF-032) | Cumple | user_routes devuelve 409 para conflicto |
| Cambio de correo con verificación (RF-033, RF-034) | **No implementado** | |
| 403 si perfil no es del usuario (RF-035) | **No implementado** | No se valida JWT/subject vs user_id |
| Auditoría de perfil (RF-036, RF-037) | Parcial | ProfileAuditLog y save_log existen; no hay GET de historial de auditoría |
| Objetivos fitness enum (RF-038) | Parcial | fitness_goal es string libre, no enum |
| Validación género (RF-042) | **No implementado** | Sin validación MALE/FEMALE/OTHER/PREFER_NOT_TO_SAY |

**Brechas:** (1) Aplicar en UpdateProfile todos los campos editables. (2) Ampliar UserProfileResponse y persistencia de perfil. (3) Autorización 403 (JWT vs user_id). (4) GET historial de auditoría. (5) Cambio de correo con verificación. (6) Enum de objetivos y validación de género.

---

## 2. Requisitos funcionales no cubiertos (resumen)

- **Identidad:** RF-006 (refresh token endpoint), RF-007 (logout/revocación), RF-009 (HTTPS responsabilidad despliegue), RF-010 (almacén/validación refresh).
- **Contraseña:** RF-011 a RF-025 (restablecimiento, cambio, complejidad, historial 5 contraseñas, rate limiting, correo).
- **Perfil:** RF-026 a RF-042 (campos completos, auditoría consultable, autorización, cambio de correo, enums).
- **Instructores:** RF-043 a RF-050 implementados (listar, perfil, asignar, desactivar anterior, calificar 1-5, promedio, solo asignados).
- **Evaluación:** RF-051, RF-052, RF-059 (preguntas progresivas, tipos, validación por pregunta). RF-058 (descargo edad corporal) implementado en AssessmentResponse.
- **Progreso:** RF-064, RF-066, RF-067 implementados (Historia 4 completa).
- **Entrenamiento:** RF-071 (URL demostración ejercicio), RF-072, RF-073 (grupos musculares y dificultad como catálogo).
- **Nutrición:** RF-084 (notas generales en plan) — menor.
- **Mensajería:** RF-088 a RF-094.
- **Recordatorios:** RF-095 a RF-100.
- **Calidad:** RF-107 (spec pide PostgreSQL; proyecto usa MySQL — decisión en fitlife-backend-implementation.md), RF-108 (Redis/caché) — opcionales.

---

## 3. Enfoque del plan por fases

El plan se ordena por prioridad de la spec (P1 primero) y dependencias entre historias. Cada fase debe incluir: cambios en dominio, aplicación, infraestructura y rutas; pruebas; y actualización de documentación de API.

---

## 4. Plan de implementación por fases

### Fase 1 – Auth y contraseñas (Historias 1 y 9 – P1)

**Objetivo:** Cumplir Historia 1 (refresh, 409, tokens en registro si se confirma) e Historia 9 completa.

**Tareas:**

1. **Auth**
   - Añadir POST /api/v1/auth/refresh: body con refresh_token; validar token, opcionalmente contra RefreshTokenModel; emitir nuevo access_token; mantener o rotar refresh_token según política.
   - En registro: devolver 409 Conflict cuando el email ya exista (y mensaje claro).
   - Opcional: que POST /auth/register devuelva también tokens (spec dice "proporciona tokens") o documentar que el flujo es registro + login.
   - Usar/ampliar RefreshTokenModel para validar y revocar refresh tokens (y opcionalmente RF-007 logout).

2. **Contraseña**
   - Entidades/dominio: PasswordResetToken (valor, user_id, expires_at, estado), PasswordHistory (user_id, password_hash, created_at); reglas de negocio (expiración 1h, no reutilizar últimas 5).
   - Infra: tablas y repositorios; envío de correo (SMTP/adaptador) para enlace de restablecimiento; validación de complejidad (8 chars, mayúscula, minúscula, número, especial).
   - Endpoints: POST /auth/password/reset-request (email), POST /auth/password/reset (token + new_password), POST /auth/password/change (current_password + new_password, requiere JWT).
   - Rate limiting para reset-request (ej. 3/hora por email, RF-023).
   - Respuestas genéricas para email no registrado (RF-024).

**Entregables:** Rutas auth actualizadas + 3 endpoints de contraseña; tests unitarios e integración; migraciones DB.

---

### Fase 2 – Instructores (Historia 3 – P1)

**Objetivo:** Listar instructores, ver detalle, asignar y cambiar instructor, calificar.

**Tareas:**

1. Dominio: entidades Instructor, InstructorAssignment, InstructorRating; interfaces de repositorio.
2. Infra: modelos SQLAlchemy y repositorios; migraciones.
3. Casos de uso: ListInstructors, GetInstructorById, AssignInstructor (y desactivar asignación anterior), RateInstructor (solo si asignado; actualizar promedio).
4. Rutas: GET /instructors, GET /instructors/{id}, POST /users/{id}/assign-instructor, POST /instructors/{id}/rate.
5. Reglas: un usuario solo un instructor activo; preservar historial; calificación 1–5; no permitir calificar si no ha sido asignado.

**Entregables:** Módulo instructores completo; tests; documentación API.

---

### Fase 3 – Perfil completo y autorización (Historia 10 – P2)

**Objetivo:** Perfil completo, auditoría consultable, autorización y validaciones.

**Tareas:**

1. Perfil: ampliar UpdateProfile para persistir y devolver age, gender, height, fitness_goal, activity_level; UserProfileResponse y modelo de perfil con todos los campos; objetivos como enum (WEIGHT_LOSS, MUSCLE_GAIN, GENERAL_FITNESS, ATHLETIC_PERFORMANCE, HEALTH_MAINTENANCE); género con validación (MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY).
2. Autorización: en GET/PATCH /users/{id}/profile validar que sub del JWT == user_id (o rol ADMIN); si no, 403 Forbidden.
3. Auditoría: endpoint GET /users/{id}/profile/audit (o similar) que devuelva historial de ProfileAuditLog (timestamp, campos, valores antiguos/nuevos); solo propietario o ADMIN.
4. Cambio de correo (opcional en esta fase): flujo con token de verificación y estado "pendiente de verificación" (RF-033, RF-034).

**Entregables:** Perfil completo, 403 en no autorizado, GET auditoría; tests.

---

### Fase 4 – Evaluación y ejercicios (Historias 2 y 5 – ajustes)

**Objetivo:** Alinear evaluación con spec y añadir demostración de ejercicios.

**Tareas:**

1. Evaluación: opcionalmente añadir GET /users/{id}/assessments como alias de GET /assessments/user/{user_id}; considerar RF-058 (descargo de edad corporal en respuesta o documentación); validación de respuestas por tipo de pregunta (RF-059) si hay catálogo de preguntas.
2. Ejercicios: añadir campo demo_url (YouTube) a Exercise entity y ExerciseModel; migración; si no existe, GET /exercises/{id} (o incluir en rutina) para nombre, grupo muscular, dificultad y URL de demostración (Story 5, RF-071).

**Entregables:** Path alternativo/alias si se elige; modelo y API de ejercicio con URL; tests.

---

### Fase 5 – Mensajería (Historia 7 – P3)

**Objetivo:** Mensajes instructor–usuario y notificaciones automáticas.

**Tareas:**

1. Dominio: entidad Message (remitente, destinatario, contenido, tipo INSTRUCTOR_MESSAGE | SYSTEM_NOTIFICATION, timestamp, leído).
2. Infra: modelo y repositorio; regla: instructor solo a sus usuarios asignados.
3. Casos de uso: SendMessage, GetMessagesByUser; opcionalmente generar SYSTEM_NOTIFICATION al asignar rutina o plan.
4. Rutas: POST /messages, GET /messages/user/{id} (ordenado por tiempo).

**Entregables:** API de mensajes; tests.

---

### Fase 6 – Recordatorios y notificaciones (Historia 8 – P3)

**Objetivo:** Recordatorios y envío vía FCM.

**Tareas:**

1. Dominio: entidad Reminder (user_id, tipo TRAINING | PHYSICAL_RECORD | INSTRUCTOR_FOLLOWUP, horario, activo).
2. Infra: modelo, repositorio; worker o cron que evalúe recordatorios y dispare notificaciones; integración Firebase Cloud Messaging (tokens de dispositivo en usuario o tabla aparte).
3. Rutas: POST /reminders, GET /reminders; opcional PATCH/DELETE.
4. Zona horaria (RF-100): almacenar o interpretar horarios según zona del usuario.

**Entregables:** CRUD recordatorios; envío push; tests y documentación.

---

## 5. Orden de fases y mantenimiento del documento

**Orden de fases:** 1 → 2 → 3 → 4 → 5 → 6 (P1 primero, luego P2, luego P3).

Al completar cada fase, actualizar en este documento:
- La tabla de cumplimiento de la historia correspondiente (marcar criterios como Cumple).
- La sección de RF no cubiertos (eliminar o marcar los implementados).
- Opcionalmente, una breve nota en "Notas de decisiones" si se tomó alguna decisión de diseño relevante.

---

## 6. Notas de decisiones

- **Base de datos:** La especificación menciona PostgreSQL (RF-107); el proyecto utiliza MySQL por decisión documentada en [fitlife-backend-implementation.md](fitlife-backend-implementation.md). No se prevé cambio a PostgreSQL en el plan actual.
- **Refresh tokens:** Se usa tabla en MySQL (RefreshTokenModel) en lugar de Redis (RF-010); la validación y revocación se implementarán en Fase 1 contra ese almacén.
- **Paths de API:** El historial de evaluaciones está expuesto como GET /assessments/user/{user_id} en lugar de GET /users/{id}/assessments. Se puede añadir un alias en Fase 4 o mantener la ruta actual documentada.
- **Registro y tokens:** La spec indica que el registro "proporciona tokens de acceso y actualización". Opciones: (a) que POST /auth/register devuelva tokens además de datos de usuario, o (b) mantener flujo registro + login y documentarlo como cumplimiento funcional.
- **POST /workouts/complete:** La implementación usa `user_id` para identificar al usuario que completa el entrenamiento; la spec menciona "workouts/{id}". Se considera aceptable el diseño actual (completar por usuario y rutina activa) siempre que se documente en la API.
