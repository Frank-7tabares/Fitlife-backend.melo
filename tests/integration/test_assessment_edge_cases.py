import pytest
import uuid
import httpx
BASE_URL = 'http://localhost:8000/api/v1'

@pytest.fixture(scope='module')
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c

@pytest.fixture(scope='module')
def auth(client):
    email = f'assess_{uuid.uuid4().hex[:8]}@example.com'
    password = 'Password123!'
    r = client.post('/auth/register', json={'email': email, 'password': password, 'full_name': 'Test Assess'})
    assert r.status_code == 201, f'Register failed: {r.status_code} {r.text}'
    user_id = r.json()['id']
    login_r = client.post('/auth/login', json={'email': email, 'password': password})
    assert login_r.status_code == 200, f'Login failed: {login_r.status_code} {login_r.text}'
    assert login_r.text, 'Login response body is empty (is the server running?)'
    token = login_r.json()['access_token']
    return {'user_id': user_id, 'headers': {'Authorization': f'Bearer {token}'}}

class TestAssessmentEdgeCases:

    def test_empty_responses_returns_score_zero(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': auth['user_id'], 'real_age': 30, 'responses': {}})
        assert response.status_code == 201
        data = response.json()
        assert data['fitness_score'] == 0.0
        assert data['category'] == 'POOR'

    def test_all_max_responses_returns_excellent(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': auth['user_id'], 'real_age': 25, 'responses': {f'q{i}': 10 for i in range(10)}})
        assert response.status_code == 201
        data = response.json()
        assert data['category'] == 'EXCELLENT'
        assert data['fitness_score'] == 100.0

    def test_body_age_younger_with_high_score(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': auth['user_id'], 'real_age': 30, 'responses': {f'q{i}': 10 for i in range(10)}})
        assert response.status_code == 201
        data = response.json()
        assert data['comparison'] == 'BODY_YOUNGER'
        assert data['body_age'] < 30

    def test_body_age_older_with_low_score(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': auth['user_id'], 'real_age': 30, 'responses': {'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0, 'q5': 0}})
        assert response.status_code == 201
        data = response.json()
        assert data['comparison'] == 'BODY_OLDER'
        assert data['body_age'] > 30

    def test_missing_user_id_returns_422(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'real_age': 30, 'responses': {'pushups': 5}})
        assert response.status_code == 422

    def test_missing_real_age_returns_422(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': auth['user_id'], 'responses': {'pushups': 5}})
        assert response.status_code == 422

    def test_invalid_user_id_format_returns_422(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': 'no-es-un-uuid', 'real_age': 30, 'responses': {'pushups': 5}})
        assert response.status_code == 422

    def test_assessment_history_empty_initially(self, client):
        import pytest
        email = f'noassess_{uuid.uuid4().hex[:8]}@example.com'
        password = 'Password123!'
        r = client.post('/auth/register', json={'email': email, 'password': password, 'full_name': 'Sin Eval'})
        if r.status_code != 201:
            pytest.skip(f'Registro falló: {r.status_code}')
        new_user_id = r.json()['id']
        login_r = client.post('/auth/login', json={'email': email, 'password': password})
        if login_r.status_code != 200:
            pytest.skip(f'Login falló (estado del servidor): {login_r.status_code}')
        token = login_r.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get(f'/assessments/user/{new_user_id}', headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_assessment_response_contains_required_fields(self, client, auth):
        response = client.post('/assessments', headers=auth['headers'], json={'user_id': auth['user_id'], 'real_age': 28, 'responses': {'pushups': 8, 'flexibility': 6}})
        assert response.status_code == 201
        data = response.json()
        for field in ['id', 'user_id', 'fitness_score', 'category', 'body_age', 'comparison', 'responses', 'created_at']:
            assert field in data, f"Campo '{field}' faltante en la respuesta"

class TestPhysicalRecordEdgeCases:

    def test_weight_zero_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 0, 'height': 170.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_negative_weight_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': -10.0, 'height': 170.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_height_zero_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_body_fat_above_100_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'body_fat_percentage': 101.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_body_fat_negative_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'body_fat_percentage': -1.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_body_fat_exactly_70_is_valid(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'body_fat_percentage': 70.0, 'activity_level': 'SEDENTARY'})
        assert response.status_code == 201

    def test_body_fat_above_70_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'body_fat_percentage': 71.0, 'activity_level': 'SEDENTARY'})
        assert response.status_code == 422

    def test_body_fat_exactly_2_is_valid(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'body_fat_percentage': 2.0, 'activity_level': 'ACTIVE'})
        assert response.status_code == 201

    def test_body_fat_below_2_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'body_fat_percentage': 1.0, 'activity_level': 'ACTIVE'})
        assert response.status_code == 422

    def test_bmi_is_calculated_automatically(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 175.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 201
        bmi = response.json()['bmi']
        expected_bmi = 70.0 / 1.75 ** 2
        assert bmi == pytest.approx(expected_bmi, abs=0.1)

    def test_optional_fields_can_be_omitted(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 75.0, 'height': 180.0, 'activity_level': 'LIGHT'})
        assert response.status_code == 201
        data = response.json()
        assert data['body_fat_percentage'] is None
        assert data['waist'] is None
        assert data['hip'] is None

    def test_missing_weight_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'height': 170.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_missing_height_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_history_returns_paginated_response(self, client, auth):
        response = client.get(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'records' in data
        assert 'total' in data
        assert isinstance(data['records'], list)

    def test_invalid_user_id_in_path_returns_422(self, client, auth):
        response = client.post('/users/no-es-uuid/physical-records', headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_weight_above_500_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 501.0, 'height': 170.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_height_below_50_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 49.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_height_above_300_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 301.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 422

    def test_invalid_activity_level_returns_422(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'activity_level': 'INVALID_LEVEL'})
        assert response.status_code == 422

    def test_all_activity_levels_are_valid(self, client, auth):
        valid_levels = ['SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE', 'VERY_ACTIVE']
        for level in valid_levels:
            response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'activity_level': level})
            assert response.status_code == 201, f"activity_level='{level}' debería ser válido"

    def test_recorded_at_can_be_provided(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'activity_level': 'MODERATE', 'recorded_at': '2026-01-15T10:00:00Z'})
        assert response.status_code == 201
        data = response.json()
        assert 'recorded_at' in data

    def test_recorded_at_defaults_to_now_when_omitted(self, client, auth):
        response = client.post(f"/users/{auth['user_id']}/physical-records", headers=auth['headers'], json={'weight': 70.0, 'height': 170.0, 'activity_level': 'MODERATE'})
        assert response.status_code == 201
        data = response.json()
        assert 'recorded_at' in data
        assert data['recorded_at'] is not None
