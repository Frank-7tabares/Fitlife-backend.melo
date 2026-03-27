"""
Pruebas de integración — Perfil de usuario (casos borde)
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
    email = f"profile_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    r = client.post("/auth/register", json={"email": email, "password": password, "full_name": "Test Profile"})
    assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"
    user_id = r.json()["id"]
    login_r = client.post("/auth/login", json={"email": email, "password": password})
    assert login_r.status_code == 200, f"Login failed: {login_r.status_code} body={login_r.text!r}"
    assert login_r.text, "Login response body is empty"
    token = login_r.json()["access_token"]
    return {
        "user_id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


# ---------------------------------------------------------------------------
# GET /profile — casos borde
# ---------------------------------------------------------------------------

class TestGetProfileEdgeCases:

    def test_nonexistent_user_returns_404(self, client, auth):
        fake_id = str(uuid.uuid4())
        response = client.get(f"/users/{fake_id}/profile", headers=auth["headers"])
        assert response.status_code == 404

    def test_invalid_uuid_format_returns_422(self, client, auth):
        response = client.get("/users/no-es-uuid/profile", headers=auth["headers"])
        assert response.status_code == 422

    def test_profile_contains_version_field(self, client, auth):
        response = client.get(f"/users/{auth['user_id']}/profile", headers=auth["headers"])
        assert response.status_code == 200
        assert "version" in response.json()

    def test_profile_does_not_expose_password(self, client, auth):
        response = client.get(f"/users/{auth['user_id']}/profile", headers=auth["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data


# ---------------------------------------------------------------------------
# PATCH /profile — casos borde
# ---------------------------------------------------------------------------

class TestUpdateProfileEdgeCases:

    def _get_version(self, client, user_id, headers) -> int:
        r = client.get(f"/users/{user_id}/profile", headers=headers)
        return r.json()["version"]

    def test_wrong_version_returns_409(self, client, auth):
        """Enviar una versión incorrecta debe retornar conflicto."""
        current_version = self._get_version(client, auth["user_id"], auth["headers"])
        wrong_version = current_version + 99

        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "full_name": "Nombre Conflicto",
            "version": wrong_version
        })
        assert response.status_code == 409

    def test_correct_version_increments_on_update(self, client, auth):
        """Una actualización exitosa debe incrementar la versión en 1."""
        version_before = self._get_version(client, auth["user_id"], auth["headers"])

        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "full_name": f"Nombre Actualizado {uuid.uuid4().hex[:4]}",
            "version": version_before
        })
        assert response.status_code == 200
        assert response.json()["version"] == version_before + 1

    def test_no_changes_does_not_increment_version(self, client, auth):
        """Si no hay campos que cambiar, la versión no debe incrementar."""
        version_before = self._get_version(client, auth["user_id"], auth["headers"])
        current_name = client.get(f"/users/{auth['user_id']}/profile",
                                  headers=auth["headers"]).json()["full_name"]

        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "full_name": current_name,  # mismo valor → no hay cambio real
            "version": version_before
        })
        assert response.status_code == 200
        # La versión no debe cambiar si no hubo modificación
        assert response.json()["version"] == version_before

    def test_age_below_minimum_returns_422(self, client, auth):
        """Edad < 13 viola la regla ge=13."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "age": 12,
            "version": version
        })
        assert response.status_code == 422

    def test_age_at_minimum_boundary_is_valid(self, client, auth):
        """Edad exactamente 13 es el límite inferior permitido."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "age": 13,
            "version": version
        })
        assert response.status_code == 200

    def test_age_above_maximum_returns_422(self, client, auth):
        """Edad > 120 viola la regla le=120."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "age": 121,
            "version": version
        })
        assert response.status_code == 422

    def test_age_at_maximum_boundary_is_valid(self, client, auth):
        """Edad exactamente 120 es el límite superior permitido."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "age": 120,
            "version": version
        })
        assert response.status_code == 200

    def test_height_below_minimum_returns_422(self, client, auth):
        """Altura < 100 cm viola la regla ge=100."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "height": 99.9,
            "version": version
        })
        assert response.status_code == 422

    def test_height_above_maximum_returns_422(self, client, auth):
        """Altura > 250 cm viola la regla le=250."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "height": 251.0,
            "version": version
        })
        assert response.status_code == 422

    def test_missing_version_returns_422(self, client, auth):
        """El campo version es obligatorio para el optimistic locking."""
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "full_name": "Sin Version"
        })
        assert response.status_code == 422

    def test_nonexistent_user_returns_404(self, client, auth):
        fake_id = str(uuid.uuid4())
        response = client.patch(f"/users/{fake_id}/profile",
                                headers=auth["headers"], json={
            "full_name": "No Existe",
            "version": 1
        })
        assert response.status_code in (404, 400)

    def test_all_optional_fields_can_be_null(self, client, auth):
        """Enviar solo version (sin otros campos) no debe causar error."""
        version = self._get_version(client, auth["user_id"], auth["headers"])
        response = client.patch(f"/users/{auth['user_id']}/profile",
                                headers=auth["headers"], json={
            "version": version
        })
        assert response.status_code == 200

    def test_concurrent_updates_second_fails_with_409(self, client, auth):
        """Simula dos clientes actualizando con la misma versión (solo el primero gana)."""
        version = self._get_version(client, auth["user_id"], auth["headers"])

        # Primera actualización — debe tener éxito
        r1 = client.patch(f"/users/{auth['user_id']}/profile",
                          headers=auth["headers"], json={
            "full_name": "Primera Actualización",
            "version": version
        })
        assert r1.status_code == 200

        # Segunda actualización con la misma versión — debe fallar
        r2 = client.patch(f"/users/{auth['user_id']}/profile",
                          headers=auth["headers"], json={
            "full_name": "Segunda Actualización",
            "version": version
        })
        assert r2.status_code == 409
