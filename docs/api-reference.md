# FitLife Backend — API Reference

**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api/v1`  
**Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)  
**OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 📋 Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login and get JWT tokens |
| `POST` | `/api/v1/assessments` | Submit a fitness assessment |
| `GET` | `/api/v1/assessments/user/{user_id}` | Get assessment history |
| `GET` | `/api/v1/users/{user_id}/assessments` | Get assessment history (alias, spec) |
| `POST` | `/api/v1/users/{user_id}/physical-records` | Log physical measurements |
| `GET` | `/api/v1/users/{user_id}/physical-records` | Get physical record history |
| `POST` | `/api/v1/training/routines` | Create a training routine |
| `POST` | `/api/v1/users/{user_id}/routines/assign` | Assign a routine to a user |
| `GET` | `/api/v1/users/{user_id}/routines/active` | Get user's active routine |
| `POST` | `/api/v1/workouts/complete` | Log a completed workout |
| `POST` | `/api/v1/nutrition/plans` | Create a nutrition plan |
| `GET` | `/api/v1/users/{user_id}/nutrition/active` | Get user's active nutrition plan |
| `GET` | `/api/v1/users/{user_id}/profile` | Get user profile |
| `PATCH` | `/api/v1/users/{user_id}/profile` | Update user profile |
| `POST` | `/api/v1/instructors` | Create instructor (seed/admin) |
| `GET` | `/api/v1/instructors` | List all instructors |
| `GET` | `/api/v1/instructors/{instructor_id}` | Get instructor by ID |
| `POST` | `/api/v1/users/{user_id}/assign-instructor` | Assign instructor to user |
| `POST` | `/api/v1/instructors/{instructor_id}/rate` | Rate instructor (1-5, requires assignment) |

---

## 👤 Instructors (Historia 3)

### `GET /api/v1/instructors`
List all instructors with name, certifications, rating average and active users count.

**Response `200`:** Array of:
```json
{
  "id": "uuid",
  "name": "Coach Name",
  "certifications": ["ACE", "NASM"],
  "specializations": "Strength & Conditioning",
  "rating_avg": 4.5,
  "active_users_count": 12
}
```

### `GET /api/v1/instructors/{instructor_id}`
Get instructor profile by ID. Returns 404 if not found.

### `POST /api/v1/users/{user_id}/assign-instructor`
Assign an instructor to a user. Any previous active assignment is deactivated (history preserved).

**Request Body:** `{ "instructor_id": "uuid" }`

**Response `200`:** `{ "message": "Instructor assigned successfully" }`

### `POST /api/v1/instructors/{instructor_id}/rate`
Rate the instructor (1-5). Only allowed if the user is currently assigned to this instructor (RF-050). In production, `user_id` should come from JWT; for testing it can be passed as query param `user_id`.

**Request Body:** `{ "rating": 4, "comment": "Optional comment" }`  
**Query:** `user_id` (UUID, required until JWT is used)

**Response `200`:** `{ "message": "Rating submitted successfully" }`  
**Response `403`:** User is not assigned to this instructor.

---

## 🔐 Authentication

### `POST /api/v1/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123",
  "full_name": "John Doe"
}
```

**Response `201`:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "USER",
  "full_name": "John Doe",
  "created_at": "2026-02-28T10:00:00"
}
```

---

### `POST /api/v1/auth/login`
Authenticate and receive JWT access + refresh tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

**Response `200`:**
```json
{
  "access_token": "<jwt_access_token>",
  "refresh_token": "<jwt_refresh_token>",
  "token_type": "bearer"
}
```

---

## 🏋️ Fitness Assessment

### `POST /api/v1/assessments`
Submit a fitness assessment and receive a score, category, and body age.

**Request Body:**
```json
{
  "user_id": "uuid",
  "real_age": 30,
  "responses": {
    "pushups": 8,
    "run_minutes": 6,
    "flexibility": 5,
    "sleep_hours": 7,
    "stress_level": 3
  }
}
```

**Response `201`:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "fitness_score": 72.5,
  "category": "GOOD",
  "body_age": 28.25,
  "comparison": "BODY_YOUNGER",
  "responses": { "...": "..." },
  "created_at": "2026-02-28T10:00:00",
  "body_age_disclaimer": "La edad corporal es una estimación orientativa y no constituye un diagnóstico médico."
}
```

**Assessment Categories:** `POOR` | `FAIR` | `GOOD` | `EXCELLENT`  
**Body Age Comparison:** `BODY_OLDER` | `BODY_YOUNGER` | `BODY_EQUAL`  
**body_age_disclaimer:** Texto de descargo (RF-058); la edad corporal es estimación, no diagnóstico médico.

---

### `GET /api/v1/assessments/user/{user_id}`
Get full assessment history for a user.

**Path Params:** `user_id` (UUID)

**Response `200`:** Array of assessment objects (same schema as above, including `body_age_disclaimer`).

---

### `GET /api/v1/users/{user_id}/assessments`
Get assessment history for a user (alias per spec: *Historia 2 – Ver historial de evaluaciones*). Same behaviour and response as `GET /api/v1/assessments/user/{user_id}`.

---

## 📊 Physical Progress

### `POST /api/v1/users/{user_id}/physical-records`
Log a new physical measurement record. BMI is calculated automatically.

**Path Params:** `user_id` (UUID)

**Request Body:**
```json
{
  "weight": 75.5,
  "height": 175.0,
  "body_fat_percentage": 18.5,
  "waist": 82.0,
  "hip": 96.0,
  "activity_level": "MODERATE"
}
```

**Response `201`:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "weight": 75.5,
  "height": 175.0,
  "bmi": 24.65,
  "body_fat_percentage": 18.5,
  "waist": 82.0,
  "hip": 96.0,
  "activity_level": "MODERATE",
  "created_at": "2026-02-28T10:00:00"
}
```

---

### `GET /api/v1/users/{user_id}/physical-records`
Get physical record history (most recent first).

**Path Params:** `user_id` (UUID)

**Response `200`:** Array of physical record objects.

---

## 🏃 Training Routines

### `POST /api/v1/training/routines`
Create a new training routine (typically by an instructor).

**Request Body:**
```json
{
  "name": "Beginner Full Body",
  "description": "3-day full body workout for beginners",
  "goal": "Build base fitness",
  "level": "BEGINNER",
  "creator_id": "uuid",
  "exercises": [
    {
      "exercise_id": "uuid",
      "sets": 3,
      "reps": 12,
      "rest_seconds": 60
    }
  ]
}
```

**Fitness Levels:** `BEGINNER` | `INTERMEDIATE` | `ADVANCED`

**Response `201`:** Full routine object including all exercises.

---

### `POST /api/v1/users/{user_id}/routines/assign`
Assign an existing routine to a user. Deactivates any previously active routine.

**Path Params:** `user_id` (UUID)

**Request Body:**
```json
{
  "routine_id": "uuid"
}
```

**Response `200`:**
```json
{ "message": "Routine assigned successfully" }
```

---

### `GET /api/v1/users/{user_id}/routines/active`
Get the user's currently active training routine.

**Path Params:** `user_id` (UUID)

**Response `200`:** Full routine object.  
**Response `404`:** `{ "detail": "No active routine found" }`

---

### `POST /api/v1/workouts/complete`
Log a completed workout for the user's active routine.

**Query Params:** `user_id` (UUID)

**Request Body:**
```json
{
  "effort_level": 8,
  "notes": "Felt great, increased weight on squats"
}
```
> **`effort_level`**: Integer from 1 (easy) to 10 (maximum effort).

**Response `200`:**
```json
{ "message": "Workout completed successfully" }
```

---

## 🥗 Nutrition Plans

### `POST /api/v1/nutrition/plans`
Create a weekly nutrition plan for a user. Activating a new plan deactivates the previous one.

**Query Params:** `user_id` (UUID)

**Request Body:**
```json
{
  "name": "High Protein Week",
  "description": "Caloric surplus plan for muscle gain",
  "week_number": 9,
  "year": 2026,
  "is_active": true,
  "daily_plans": [
    {
      "day_of_week": 0,
      "meals": [
        {
          "name": "Breakfast",
          "description": "Oats with banana and protein shake",
          "calories": 550,
          "protein": 35.0,
          "carbs": 70.0,
          "fats": 12.0
        }
      ]
    }
  ]
}
```
> **`day_of_week`**: 0=Monday, 1=Tuesday, ..., 6=Sunday

**Response `201`:** Full nutrition plan object.

---

### `GET /api/v1/users/{user_id}/nutrition/active`
Get the user's currently active nutrition plan.

**Path Params:** `user_id` (UUID)

**Response `200`:** Full nutrition plan object.  
**Response `404`:** `{ "detail": "No active nutrition plan found" }`

---

## 👤 User Profiles

### `GET /api/v1/users/{user_id}/profile`
Get a user's profile information including current version for optimistic locking.

**Path Params:** `user_id` (UUID)

**Response `200`:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "USER",
  "version": 1,
  "created_at": "2026-02-28T10:00:00"
}
```

---

### `PATCH /api/v1/users/{user_id}/profile`
Update a user's profile. Requires the current `version` for **optimistic locking** — prevents lost updates when multiple clients modify the same profile.

**Path Params:** `user_id` (UUID)

**Request Body:**
```json
{
  "full_name": "John Updated",
  "gender": "male",
  "age": 31,
  "height": 175.5,
  "fitness_goal": "Lose weight",
  "activity_level": "MODERATE",
  "version": 1
}
```
> ⚠️ All fields except `version` are optional. Include only the fields you want to update.

**Response `200`:** Updated profile object with incremented `version`.  
**Response `409`:** `{ "detail": "Concurrency conflict: ..." }` — The profile was modified by another process. Fetch the latest version and retry.

---

## 📦 Data Schemas

### UserRole
```
USER | INSTRUCTOR | ADMIN
```

### FitnessLevel
```
BEGINNER | INTERMEDIATE | ADVANCED
```

### AssessmentCategory
```
POOR | FAIR | GOOD | EXCELLENT
```

### BodyAgeComparison
```
BODY_YOUNGER | BODY_EQUAL | BODY_OLDER
```

---

## 🛠️ Error Responses

All endpoints return standard HTTP error responses:

| Status | Meaning |
|--------|---------|
| `400` | Bad Request — invalid input |
| `404` | Not Found — resource doesn't exist |
| `409` | Conflict — optimistic locking failure |
| `422` | Unprocessable Entity — validation error |
| `500` | Internal Server Error |

**Validation Error Format (`422`):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
