"""
FitLife Backend — Ejemplo de consumo completo con httpx
=======================================================
Ejecutar:
    cd fitlife-backend
    source venv/bin/activate
    python docs/examples/client_example.py

Requisito: el servidor debe estar corriendo en http://localhost:8000
    python3.11 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
"""

import httpx
import json
import base64
from uuid import UUID

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_response(label: str, response: httpx.Response) -> dict:
    print(f"\n[{response.status_code}] {label}")
    if not response.content:
        print("  (respuesta vacía — error interno del servidor)")
        return {}
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
        return data
    except Exception:
        print(f"  Respuesta: {response.text[:300]}")
        return {}


# ===========================================================================
# 1. AUTENTICACIÓN
# ===========================================================================

def decode_jwt_payload(token: str) -> dict:
    """Decodifica el payload de un JWT sin verificar la firma."""
    payload_b64 = token.split(".")[1]
    # Añade padding si es necesario
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding
    return json.loads(base64.urlsafe_b64decode(payload_b64))


def demo_auth(client: httpx.Client) -> tuple[str, str]:
    """Registra un usuario, inicia sesión y devuelve (user_id, access_token)."""
    print_section("1. AUTENTICACIÓN")

    user_id = None

    # Registro
    response = client.post(f"{BASE_URL}/auth/register", json={
        "email": "carlos.perez@fitlife.com",
        "password": "MiPassword123!",
        "full_name": "Carlos Pérez"
    })
    user_data = print_response("Registro de usuario", response)

    if response.status_code == 201:
        user_id = user_data.get("id")
    elif response.status_code == 400 and "already" in response.text.lower():
        print("  → Usuario ya existe, procediendo con login...")

    # Login
    response = client.post(f"{BASE_URL}/auth/login", json={
        "email": "carlos.perez@fitlife.com",
        "password": "MiPassword123!"
    })
    token_data = print_response("Login", response)
    access_token = token_data["access_token"]

    # Si el registro falló, extraemos el user_id del JWT
    if not user_id:
        payload = decode_jwt_payload(access_token)
        user_id = payload.get("sub")

    return user_id, access_token


# ===========================================================================
# 2. PERFIL DE USUARIO
# ===========================================================================

def demo_profile(client: httpx.Client, user_id: str, token: str) -> None:
    print_section("2. PERFIL DE USUARIO")

    headers = {"Authorization": f"Bearer {token}"}

    # Obtener perfil
    response = client.get(f"{BASE_URL}/users/{user_id}/profile", headers=headers)
    profile = print_response("Obtener perfil", response)
    current_version = profile["version"]

    # Actualizar perfil — usa el version actual (optimistic locking)
    response = client.patch(
        f"{BASE_URL}/users/{user_id}/profile",
        headers=headers,
        json={
            "full_name": "Carlos A. Pérez",
            "gender": "male",
            "age": 28,
            "height": 178.0,
            "fitness_goal": "Ganar masa muscular",
            "activity_level": "MODERATE",
            "version": current_version
        }
    )
    result = print_response("Actualizar perfil", response)
    if response.status_code == 409:
        print("  → Conflicto de versión (ya fue actualizado antes). Continuando...")


# ===========================================================================
# 3. EVALUACIÓN DE CONDICIÓN FÍSICA
# ===========================================================================

def demo_assessment(client: httpx.Client, user_id: str, token: str) -> None:
    print_section("3. EVALUACIÓN DE CONDICIÓN FÍSICA")

    headers = {"Authorization": f"Bearer {token}"}

    # Enviar evaluación
    response = client.post(
        f"{BASE_URL}/assessments",
        headers=headers,
        json={
            "user_id": user_id,
            "real_age": 28,
            "responses": {
                "pushups": 20,
                "run_minutes": 8,
                "flexibility": 7,
                "sleep_hours": 7,
                "stress_level": 4
            }
        }
    )
    assessment = print_response("Evaluación enviada", response)

    if response.status_code == 201:
        print(f"\n  Puntuación de condición: {assessment['fitness_score']:.1f}")
        print(f"  Categoría: {assessment['category']}")
        print(f"  Edad corporal: {assessment['body_age']:.1f} años (real: 28 años)")
        print(f"  Comparación: {assessment['comparison']}")

    # Historial de evaluaciones
    response = client.get(
        f"{BASE_URL}/assessments/user/{user_id}",
        headers=headers
    )
    history = print_response("Historial de evaluaciones", response)
    if isinstance(history, list):
        print(f"\n  Total de evaluaciones registradas: {len(history)}")


# ===========================================================================
# 4. REGISTROS FÍSICOS
# ===========================================================================

def demo_physical_records(client: httpx.Client, user_id: str, token: str) -> None:
    print_section("4. REGISTROS FÍSICOS (Peso y Medidas)")

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/users/{user_id}/physical-records"

    # Primer registro
    response = client.post(url, headers=headers, json={
        "weight": 75.5,
        "height": 178.0,
        "body_fat_percentage": 17.0,
        "waist": 82.0,
        "hip": 95.0,
        "activity_level": "MODERATE"
    })
    record = print_response("Registro inicial", response)
    if response.status_code == 201:
        print(f"\n  IMC calculado automáticamente: {record.get('bmi', 'N/A'):.2f}")

    # Segundo registro (simulando progreso)
    response = client.post(url, headers=headers, json={
        "weight": 74.8,
        "height": 178.0,
        "body_fat_percentage": 16.5,
        "waist": 81.0,
        "hip": 94.5,
        "activity_level": "ACTIVE"
    })
    print_response("Registro de progreso (4 semanas después)", response)

    # Historial completo
    response = client.get(url, headers=headers)
    records = print_response("Historial de registros", response)
    if isinstance(records, list) and len(records) >= 2:
        delta_peso = records[0]["weight"] - records[-1]["weight"]
        print(f"\n  Cambio de peso: {delta_peso:+.1f} kg")


# ===========================================================================
# 5. RUTINAS DE ENTRENAMIENTO
# ===========================================================================

def demo_training(client: httpx.Client, user_id: str, token: str) -> None:
    print_section("5. RUTINAS DE ENTRENAMIENTO")

    headers = {"Authorization": f"Bearer {token}"}

    # Crear rutina (normalmente lo hace un instructor; usamos el mismo user_id como creator)
    import uuid
    fake_exercise_id = str(uuid.uuid4())

    response = client.post(
        f"{BASE_URL}/training/routines",
        headers=headers,
        json={
            "name": "Rutina Fuerza Principiante",
            "description": "3 días de entrenamiento de cuerpo completo para construir fuerza base",
            "goal": "Desarrollar fuerza y masa muscular inicial",
            "level": "BEGINNER",
            "creator_id": user_id,
            "exercises": [
                {
                    "exercise_id": fake_exercise_id,
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 60
                },
                {
                    "exercise_id": fake_exercise_id,
                    "sets": 4,
                    "reps": 8,
                    "rest_seconds": 90
                }
            ]
        }
    )
    routine = print_response("Crear rutina", response)

    if response.status_code != 201:
        print("  → No se pudo crear la rutina, saltando pasos de entrenamiento.")
        return

    routine_id = routine["id"]

    # Asignar rutina al usuario
    response = client.post(
        f"{BASE_URL}/users/{user_id}/routines/assign",
        headers=headers,
        json={"routine_id": routine_id}
    )
    print_response("Asignar rutina al usuario", response)

    # Ver rutina activa
    response = client.get(
        f"{BASE_URL}/users/{user_id}/routines/active",
        headers=headers
    )
    print_response("Rutina activa del usuario", response)

    # Registrar entrenamiento completado
    response = client.post(
        f"{BASE_URL}/workouts/complete",
        headers=headers,
        params={"user_id": user_id},
        json={
            "effort_level": 7,
            "notes": "Aumenté el peso en press banca. Me sentí muy bien con la rutina."
        }
    )
    print_response("Entrenamiento completado", response)


# ===========================================================================
# 6. PLANES DE NUTRICIÓN
# ===========================================================================

def demo_nutrition(client: httpx.Client, user_id: str, token: str) -> None:
    print_section("6. PLANES DE NUTRICIÓN")

    headers = {"Authorization": f"Bearer {token}"}

    # Crear plan nutricional semanal
    response = client.post(
        f"{BASE_URL}/nutrition/plans",
        headers=headers,
        params={"user_id": user_id},
        json={
            "name": "Plan Hiperproteico - Semana 9",
            "description": "Plan con superávit calórico para ganancia muscular limpia",
            "week_number": 9,
            "year": 2026,
            "is_active": True,
            "daily_plans": [
                {
                    "day_of_week": 0,
                    "meals": [
                        {
                            "name": "Desayuno",
                            "description": "Avena con plátano y proteína en polvo",
                            "calories": 550,
                            "protein": 38.0,
                            "carbs": 72.0,
                            "fats": 10.0
                        },
                        {
                            "name": "Almuerzo",
                            "description": "Pechuga de pollo con arroz integral y brócoli",
                            "calories": 620,
                            "protein": 52.0,
                            "carbs": 65.0,
                            "fats": 12.0
                        },
                        {
                            "name": "Cena",
                            "description": "Salmón al horno con batata y espinacas",
                            "calories": 580,
                            "protein": 45.0,
                            "carbs": 50.0,
                            "fats": 18.0
                        }
                    ]
                },
                {
                    "day_of_week": 1,
                    "meals": [
                        {
                            "name": "Desayuno",
                            "description": "Huevos revueltos con aguacate y pan integral",
                            "calories": 480,
                            "protein": 28.0,
                            "carbs": 38.0,
                            "fats": 22.0
                        },
                        {
                            "name": "Almuerzo",
                            "description": "Atún con pasta integral y tomates cherry",
                            "calories": 590,
                            "protein": 48.0,
                            "carbs": 62.0,
                            "fats": 10.0
                        },
                        {
                            "name": "Cena",
                            "description": "Carne magra con ensalada verde y quinoa",
                            "calories": 560,
                            "protein": 42.0,
                            "carbs": 45.0,
                            "fats": 15.0
                        }
                    ]
                }
            ]
        }
    )
    plan = print_response("Crear plan de nutrición", response)

    if response.status_code == 201:
        total_calories = sum(
            meal["calories"]
            for day in plan["daily_plans"]
            for meal in day["meals"]
            if meal.get("calories")
        )
        print(f"\n  Calorías totales planificadas (2 días): {total_calories} kcal")
        print(f"  Promedio diario: {total_calories / 2:.0f} kcal/día")

    # Ver plan activo
    response = client.get(
        f"{BASE_URL}/users/{user_id}/nutrition/active",
        headers=headers
    )
    print_response("Plan de nutrición activo", response)


# ===========================================================================
# MAIN — Flujo completo de demostración
# ===========================================================================

def main() -> None:
    print("\nFitLife Backend — Demo de consumo de APIs")
    print("Conectando a:", BASE_URL)

    with httpx.Client(timeout=10.0) as client:

        # Verificar que el servidor está activo
        try:
            response = client.get("http://localhost:8000/")
            print(f"\nServidor: OK ({response.json()['message']})")
        except httpx.ConnectError:
            print("\nERROR: No se puede conectar al servidor.")
            print("Asegúrate de que el servidor esté corriendo:")
            print("  python3.11 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
            return

        # Flujo completo
        user_id, token = demo_auth(client)

        if not user_id or not token:
            print("\nERROR: No se pudo completar la autenticación.")
            return

        print(f"\n  user_id  : {user_id}")
        print(f"  token    : {token[:40]}...")

        demo_profile(client, user_id, token)
        demo_assessment(client, user_id, token)
        demo_physical_records(client, user_id, token)
        demo_training(client, user_id, token)
        demo_nutrition(client, user_id, token)

        print_section("DEMO COMPLETADA")
        print("\nTodos los endpoints fueron consumidos exitosamente.")
        print("Revisa http://localhost:8000/docs para la documentación interactiva.")


if __name__ == "__main__":
    main()
