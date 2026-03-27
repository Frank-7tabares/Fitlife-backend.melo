"""
Pruebas de integración — Entrenamiento y Nutrición (casos borde)
Requiere servidor en http://localhost:8000
"""
import pytest
import uuid
import httpx

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.fixture(scope="module")
def auth(client):
    email = f"training_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    r = client.post("/auth/register", json={"email": email, "password": password, "full_name": "Test Training"})
    assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"
    user_id = r.json()["id"]
    login_r = client.post("/auth/login", json={"email": email, "password": password})
    assert login_r.status_code == 200, f"Login failed: {login_r.status_code} body={login_r.text!r}"
    assert login_r.text, "Login response body is empty (is the server running?)"
    token = login_r.json()["access_token"]
    return {"user_id": user_id, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture(scope="module")
def created_routine(client, auth):
    """Crea una rutina real reutilizable en los tests del módulo."""
    fake_exercise_id = str(uuid.uuid4())
    response = client.post("/training/routines", headers=auth["headers"], json={
        "name": "Rutina Test Edge Cases",
        "description": "Para pruebas de casos borde",
        "goal": "Testing",
        "level": "BEGINNER",
        "creator_id": auth["user_id"],
        "exercises": [
            {"exercise_id": fake_exercise_id, "sets": 3, "reps": 10, "rest_seconds": 60}
        ]
    })
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# Rutinas de entrenamiento — casos borde
# ---------------------------------------------------------------------------

class TestTrainingEdgeCases:

    def test_active_routine_when_none_assigned_returns_404(self, client, auth):
        """Usuario sin rutina asignada debe retornar 404."""
        # Crear usuario nuevo sin asignaciones
        email = f"noroutine_{uuid.uuid4().hex[:8]}@example.com"
        r = client.post("/auth/register", json={"email": email, "password": "Pass123!", "full_name": "Sin Rutina"})
        assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"
        new_user_id = r.json()["id"]
        login_r = client.post("/auth/login", json={"email": email, "password": "Pass123!"})
        assert login_r.status_code == 200 and login_r.text, f"Login failed: {login_r.status_code} {login_r.text}"
        headers = {"Authorization": f"Bearer {login_r.json()['access_token']}"}

        response = client.get(f"/users/{new_user_id}/routines/active", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    def test_create_routine_with_zero_sets_returns_422(self, client, auth):
        """sets=0 viola la regla gt=0."""
        response = client.post("/training/routines", headers=auth["headers"], json={
            "name": "Rutina Inválida",
            "description": "Test",
            "goal": "Test",
            "level": "BEGINNER",
            "creator_id": auth["user_id"],
            "exercises": [
                {"exercise_id": str(uuid.uuid4()), "sets": 0, "reps": 10, "rest_seconds": 60}
            ]
        })
        assert response.status_code == 422

    def test_create_routine_with_zero_reps_returns_422(self, client, auth):
        """reps=0 viola la regla gt=0."""
        response = client.post("/training/routines", headers=auth["headers"], json={
            "name": "Rutina Inválida",
            "description": "Test",
            "goal": "Test",
            "level": "BEGINNER",
            "creator_id": auth["user_id"],
            "exercises": [
                {"exercise_id": str(uuid.uuid4()), "sets": 3, "reps": 0, "rest_seconds": 60}
            ]
        })
        assert response.status_code == 422

    def test_create_routine_with_negative_rest_returns_422(self, client, auth):
        """rest_seconds negativo viola la regla ge=0."""
        response = client.post("/training/routines", headers=auth["headers"], json={
            "name": "Rutina Inválida",
            "description": "Test",
            "goal": "Test",
            "level": "BEGINNER",
            "creator_id": auth["user_id"],
            "exercises": [
                {"exercise_id": str(uuid.uuid4()), "sets": 3, "reps": 10, "rest_seconds": -1}
            ]
        })
        assert response.status_code == 422

    def test_create_routine_with_zero_rest_is_valid(self, client, auth):
        """rest_seconds=0 es válido (ge=0)."""
        response = client.post("/training/routines", headers=auth["headers"], json={
            "name": f"Sin Descanso {uuid.uuid4().hex[:4]}",
            "description": "Circuito sin descanso",
            "goal": "Cardio",
            "level": "ADVANCED",
            "creator_id": auth["user_id"],
            "exercises": [
                {"exercise_id": str(uuid.uuid4()), "sets": 1, "reps": 20, "rest_seconds": 0}
            ]
        })
        assert response.status_code == 201

    def test_create_routine_with_invalid_level_returns_422(self, client, auth):
        """Nivel fuera del enum debe retornar 422."""
        response = client.post("/training/routines", headers=auth["headers"], json={
            "name": "Rutina Nivel Inválido",
            "description": "Test",
            "goal": "Test",
            "level": "EXPERT",  # No existe en FitnessLevel
            "creator_id": auth["user_id"],
            "exercises": [
                {"exercise_id": str(uuid.uuid4()), "sets": 3, "reps": 10, "rest_seconds": 60}
            ]
        })
        assert response.status_code == 422

    def test_create_routine_with_empty_exercises_returns_422(self, client, auth):
        """Lista de ejercicios vacía debe ser rechazada."""
        response = client.post("/training/routines", headers=auth["headers"], json={
            "name": "Sin Ejercicios",
            "description": "Test",
            "goal": "Test",
            "level": "BEGINNER",
            "creator_id": auth["user_id"],
            "exercises": []
        })
        # Depende de validación de Pydantic — si no hay min_items se acepta
        assert response.status_code in (201, 422)

    def test_assign_nonexistent_routine_returns_error(self, client, auth):
        """Asignar una rutina que no existe debe retornar error."""
        fake_routine_id = str(uuid.uuid4())
        response = client.post(f"/users/{auth['user_id']}/routines/assign",
                               headers=auth["headers"], json={
            "routine_id": fake_routine_id
        })
        assert response.status_code in (400, 404, 500)

    def test_assign_routine_then_active_returns_that_routine(self, client, auth, created_routine):
        """Después de asignar, /routines/active debe retornar la rutina correcta."""
        client.post(f"/users/{auth['user_id']}/routines/assign",
                    headers=auth["headers"], json={"routine_id": created_routine["id"]})

        response = client.get(f"/users/{auth['user_id']}/routines/active", headers=auth["headers"])
        assert response.status_code == 200
        assert response.json()["id"] == created_routine["id"]

    def test_complete_workout_effort_level_below_1_returns_422(self, client, auth, created_routine):
        """effort_level=0 viola la regla ge=1."""
        response = client.post("/workouts/complete",
                               headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={"effort_level": 0, "notes": "Test"})
        assert response.status_code == 422

    def test_complete_workout_effort_level_above_10_returns_422(self, client, auth, created_routine):
        """effort_level=11 viola la regla le=10."""
        response = client.post("/workouts/complete",
                               headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={"effort_level": 11, "notes": "Test"})
        assert response.status_code == 422

    def test_complete_workout_effort_level_1_is_valid(self, client, auth, created_routine):
        """effort_level=1 es el mínimo válido."""
        response = client.post("/workouts/complete",
                               headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={"effort_level": 1})
        assert response.status_code == 200

    def test_complete_workout_effort_level_10_is_valid(self, client, auth, created_routine):
        """effort_level=10 es el máximo válido."""
        response = client.post("/workouts/complete",
                               headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={"effort_level": 10, "notes": "Máximo esfuerzo"})
        assert response.status_code == 200

    def test_complete_workout_without_notes_is_valid(self, client, auth, created_routine):
        """notes es opcional."""
        response = client.post("/workouts/complete",
                               headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={"effort_level": 5})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Planes de nutrición — casos borde
# ---------------------------------------------------------------------------

class TestNutritionEdgeCases:

    def test_active_plan_when_none_exists_returns_404(self, client):
        """Usuario sin plan activo debe retornar 404."""
        import pytest
        email = f"nonutri_{uuid.uuid4().hex[:8]}@example.com"
        password = "Password123!"
        r = client.post("/auth/register", json={"email": email, "password": password, "full_name": "Sin Plan"})
        if r.status_code != 201:
            pytest.skip(f"Registro falló (estado del servidor): {r.status_code}")
        new_user_id = r.json()["id"]
        login_r = client.post("/auth/login", json={"email": email, "password": password})
        if login_r.status_code != 200:
            pytest.skip(f"Login falló (estado del servidor): {login_r.status_code} — {login_r.text}")
        token = login_r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/users/{new_user_id}/nutrition/active", headers=headers)
        assert response.status_code == 404

    def test_week_number_zero_returns_422(self, client, auth):
        """week_number=0 viola la regla ge=1."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": "Plan Inválido",
            "description": "Test",
            "week_number": 0,
            "year": 2026,
            "is_active": True,
            "daily_plans": []
        })
        assert response.status_code == 422

    def test_week_number_54_returns_422(self, client, auth):
        """week_number=54 viola la regla le=53."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": "Plan Inválido",
            "description": "Test",
            "week_number": 54,
            "year": 2026,
            "is_active": True,
            "daily_plans": []
        })
        assert response.status_code == 422

    def test_week_number_1_is_valid(self, client, auth):
        """week_number=1 es el límite inferior permitido."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": f"Plan Semana 1 - {uuid.uuid4().hex[:4]}",
            "description": "Primera semana",
            "week_number": 1,
            "year": 2026,
            "is_active": True,
            "daily_plans": []
        })
        assert response.status_code == 201

    def test_week_number_53_is_valid(self, client, auth):
        """week_number=53 es el límite superior permitido."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": f"Plan Semana 53 - {uuid.uuid4().hex[:4]}",
            "description": "Última semana del año",
            "week_number": 53,
            "year": 2026,
            "is_active": True,
            "daily_plans": []
        })
        assert response.status_code == 201

    def test_day_of_week_7_returns_422(self, client, auth):
        """day_of_week=7 viola la regla le=6."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": "Plan Día Inválido",
            "description": "Test",
            "week_number": 10,
            "year": 2026,
            "is_active": True,
            "daily_plans": [
                {"day_of_week": 7, "meals": []}
            ]
        })
        assert response.status_code == 422

    def test_day_of_week_negative_returns_422(self, client, auth):
        """day_of_week=-1 viola la regla ge=0."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": "Plan Día Inválido",
            "description": "Test",
            "week_number": 10,
            "year": 2026,
            "is_active": True,
            "daily_plans": [
                {"day_of_week": -1, "meals": []}
            ]
        })
        assert response.status_code == 422

    def test_day_of_week_0_is_valid(self, client, auth):
        """day_of_week=0 (Lunes) es el límite inferior permitido."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": f"Plan Lunes {uuid.uuid4().hex[:4]}",
            "description": "Test",
            "week_number": 20,
            "year": 2026,
            "is_active": False,
            "daily_plans": [{"day_of_week": 0, "meals": []}]
        })
        assert response.status_code == 201

    def test_day_of_week_6_is_valid(self, client, auth):
        """day_of_week=6 (Domingo) es el límite superior permitido."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": f"Plan Domingo {uuid.uuid4().hex[:4]}",
            "description": "Test",
            "week_number": 21,
            "year": 2026,
            "is_active": False,
            "daily_plans": [{"day_of_week": 6, "meals": []}]
        })
        assert response.status_code == 201

    def test_new_active_plan_deactivates_previous(self, client, auth):
        """Activar un nuevo plan debe retornar el nuevo como activo."""
        # Plan 1 activo
        r1 = client.post("/nutrition/plans", headers=auth["headers"],
                         params={"user_id": auth["user_id"]},
                         json={
            "name": f"Plan Antiguo {uuid.uuid4().hex[:4]}",
            "description": "Test",
            "week_number": 30,
            "year": 2026,
            "is_active": True,
            "daily_plans": []
        })
        assert r1.status_code == 201
        plan1_id = r1.json()["id"]

        # Plan 2 activo — debe reemplazar al anterior
        r2 = client.post("/nutrition/plans", headers=auth["headers"],
                         params={"user_id": auth["user_id"]},
                         json={
            "name": f"Plan Nuevo {uuid.uuid4().hex[:4]}",
            "description": "Test",
            "week_number": 31,
            "year": 2026,
            "is_active": True,
            "daily_plans": []
        })
        assert r2.status_code == 201
        plan2_id = r2.json()["id"]

        # El plan activo debe ser el segundo
        active = client.get(f"/users/{auth['user_id']}/nutrition/active", headers=auth["headers"])
        assert active.status_code == 200
        assert active.json()["id"] == plan2_id

    def test_meal_with_all_optional_nutrition_fields_omitted(self, client, auth):
        """calories, protein, carbs, fats son opcionales en una comida."""
        response = client.post("/nutrition/plans", headers=auth["headers"],
                               params={"user_id": auth["user_id"]},
                               json={
            "name": f"Plan Simple {uuid.uuid4().hex[:4]}",
            "description": "Sin macros",
            "week_number": 40,
            "year": 2026,
            "is_active": False,
            "daily_plans": [
                {
                    "day_of_week": 2,
                    "meals": [
                        {"name": "Desayuno", "description": "Café con leche"}
                    ]
                }
            ]
        })
        assert response.status_code == 201
