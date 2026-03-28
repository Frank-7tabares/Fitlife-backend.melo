import pytest
import httpx
import uuid
BASE_URL = 'http://localhost:8000/api/v1'

@pytest.fixture(scope='session')
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c

@pytest.fixture(scope='session')
def registered_user(client):
    unique_email = f'test_{uuid.uuid4().hex[:8]}@example.com'
    password = 'TestPassword123!'
    response = client.post('/auth/register', json={'email': unique_email, 'password': password, 'full_name': 'Usuario Test'})
    assert response.status_code == 201, f'No se pudo registrar usuario: {response.text}'
    user_data = response.json()
    response = client.post('/auth/login', json={'email': unique_email, 'password': password})
    assert response.status_code == 200
    tokens = response.json()
    return {'id': user_data['id'], 'email': unique_email, 'password': password, 'access_token': tokens['access_token'], 'headers': {'Authorization': f"Bearer {tokens['access_token']}"}}
