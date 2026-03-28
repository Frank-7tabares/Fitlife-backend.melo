import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from fastapi.testclient import TestClient
from tests.unit.helpers import make_user_entity, make_assessment_entity, make_physical_record_entity, make_routine_entity, make_nutrition_plan_entity

def _auth_overrides(app, user_repo, refresh_repo, get_user_repo_dep, get_refresh_dep):

    async def ovr_user(db=None):
        return user_repo

    async def ovr_refresh(db=None):
        return refresh_repo
    app.dependency_overrides[get_user_repo_dep] = ovr_user
    app.dependency_overrides[get_refresh_dep] = ovr_refresh

class TestAuthRoutes:

    @pytest.mark.parametrize('exists_email,payload,expected_status,check_detail', [(False, {'email': 'new@test.com', 'password': 'StrongPass1!', 'full_name': 'New User'}, 201, 'email'), (True, {'email': 'dup@test.com', 'password': 'StrongPass1!'}, 409, 'already')])
    def test_register(self, app_with_mock_db, exists_email, payload, expected_status, check_detail):
        app, _ = app_with_mock_db
        from src.adapters.api.routes.auth_routes import get_user_repository, get_refresh_token_repository
        mock_user = AsyncMock()
        mock_user.exists_by_email.return_value = exists_email
        mock_user.save.return_value = None
        mock_refresh = AsyncMock()
        mock_refresh.save.return_value = None
        _auth_overrides(app, mock_user, mock_refresh, get_user_repository, get_refresh_token_repository)
        with TestClient(app) as client:
            resp = client.post('/api/v1/auth/register', json=payload)
        assert resp.status_code == expected_status
        if expected_status == 201:
            data = resp.json()
            assert data['email'] == payload['email'] and data['access_token'] and data['refresh_token'] and (data.get('token_type') == 'bearer')
        else:
            assert check_detail in resp.json().get('detail', '').lower()

    @pytest.mark.parametrize('valid_password,expected_status', [(True, 200), (False, 401)])
    def test_login(self, app_with_mock_db, valid_password, expected_status):
        app, _ = app_with_mock_db
        from src.adapters.api.routes.auth_routes import get_user_repository, get_refresh_token_repository
        from src.infrastructure.security.password_hasher import PasswordHasher
        user = make_user_entity(email='login@test.com')
        user.password_hash = PasswordHasher.hash('MyPass123!')
        mock_user = AsyncMock()
        mock_user.find_by_email.return_value = user
        mock_refresh = AsyncMock()
        mock_refresh.save.return_value = None
        _auth_overrides(app, mock_user, mock_refresh, get_user_repository, get_refresh_token_repository)
        with TestClient(app) as client:
            resp = client.post('/api/v1/auth/login', json={'email': 'login@test.com', 'password': 'MyPass123!' if valid_password else 'Wrong1!'})
        assert resp.status_code == expected_status
        if expected_status == 200:
            assert 'access_token' in resp.json() and 'refresh_token' in resp.json()

    @pytest.mark.parametrize('valid_token,expected_status', [(True, 200), (False, 401)])
    def test_refresh(self, app_with_mock_db, valid_token, expected_status):
        app, _ = app_with_mock_db
        from src.adapters.api.routes.auth_routes import get_user_repository, get_refresh_token_repository
        user = make_user_entity(email='r@test.com')
        mock_user = AsyncMock()
        mock_user.find_by_id.return_value = user
        mock_refresh = AsyncMock()
        mock_refresh.find_valid_user_id.return_value = user.id if valid_token else None
        mock_refresh.revoke.return_value = None
        mock_refresh.save.return_value = None
        _auth_overrides(app, mock_user, mock_refresh, get_user_repository, get_refresh_token_repository)
        with TestClient(app) as client:
            resp = client.post('/api/v1/auth/refresh', json={'refresh_token': 'valid.jwt' if valid_token else 'invalid'})
        assert resp.status_code == expected_status
        if expected_status == 200:
            assert resp.json().get('access_token') and resp.json().get('refresh_token')

class TestUserRoutes:

    def test_get_profile_found(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.user_routes import get_repos
        uid = uuid4()
        user = make_user_entity(user_id=uid)

        async def override_repos(db=None):
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = user
            mock_audit_repo = AsyncMock()
            return (mock_user_repo, mock_audit_repo)
        app.dependency_overrides[get_repos] = override_repos
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/profile')
        assert resp.status_code == 200
        data = resp.json()
        assert data['email'] == 'u@e.com'

    def test_get_profile_not_found(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.user_routes import get_repos

        async def override_repos(db=None):
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = None
            mock_audit_repo = AsyncMock()
            return (mock_user_repo, mock_audit_repo)
        app.dependency_overrides[get_repos] = override_repos
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uuid4()}/profile')
        assert resp.status_code == 404

    def test_update_profile_success(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.user_routes import get_repos
        uid = uuid4()
        user = make_user_entity(user_id=uid, full_name='Old Name')
        updated = make_user_entity(user_id=uid, full_name='New Name', version=2)

        async def override_repos(db=None):
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = user
            mock_user_repo.update.return_value = updated
            mock_audit_repo = AsyncMock()
            mock_audit_repo.save_log.return_value = None
            return (mock_user_repo, mock_audit_repo)
        app.dependency_overrides[get_repos] = override_repos
        with TestClient(app) as client:
            resp = client.patch(f'/api/v1/users/{uid}/profile', json={'full_name': 'New Name', 'version': 1})
        assert resp.status_code == 200
        data = resp.json()
        assert data['full_name'] == 'New Name'

    def test_update_profile_conflict_returns_409(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.user_routes import get_repos
        uid = uuid4()
        user = make_user_entity(user_id=uid, full_name='Name A')

        async def override_repos(db=None):
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = user
            mock_user_repo.update.side_effect = ValueError('Concurrency conflict: version mismatch')
            mock_audit_repo = AsyncMock()
            return (mock_user_repo, mock_audit_repo)
        app.dependency_overrides[get_repos] = override_repos
        with TestClient(app) as client:
            resp = client.patch(f'/api/v1/users/{uid}/profile', json={'full_name': 'Name B', 'version': 1})
        assert resp.status_code == 409

    def test_update_profile_not_found_returns_400(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.user_routes import get_repos

        async def override_repos(db=None):
            mock_user_repo = AsyncMock()
            mock_user_repo.find_by_id.return_value = None
            mock_audit_repo = AsyncMock()
            return (mock_user_repo, mock_audit_repo)
        app.dependency_overrides[get_repos] = override_repos
        with TestClient(app) as client:
            resp = client.patch(f'/api/v1/users/{uuid4()}/profile', json={'full_name': 'Name', 'version': 1})
        assert resp.status_code == 400

class TestAssessmentRoutes:

    def test_submit_assessment_success(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.assessment_routes import get_assessment_repository, get_user_repository
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.save.return_value = None
        mock_user_repo = AsyncMock()
        mock_user_repo.find_by_id.return_value = make_user_entity(user_id=uid)

        async def override_repo(db=None):
            return mock_repo

        async def override_user_repo(db=None):
            return mock_user_repo
        app.dependency_overrides[get_assessment_repository] = override_repo
        app.dependency_overrides[get_user_repository] = override_user_repo
        with TestClient(app) as client:
            resp = client.post('/api/v1/assessments', json={'user_id': str(uid), 'real_age': 30, 'responses': {'q1': 8, 'q2': 7}})
        assert resp.status_code == 201
        data = resp.json()
        assert 'fitness_score' in data
        assert 'category' in data

    @pytest.mark.parametrize('has_data,expected_len,check_disclaimer', [(False, 0, False), (True, 1, True)])
    def test_get_assessment_history(self, app_with_mock_db, has_data, expected_len, check_disclaimer):
        app, _ = app_with_mock_db
        from src.adapters.api.routes.assessment_routes import get_assessment_repository
        from src.application.dtos.assessment_dtos import BODY_AGE_DISCLAIMER
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.find_by_user_id.return_value = [make_assessment_entity(uid)] if has_data else []

        async def override_repo(db=None):
            return mock_repo
        app.dependency_overrides[get_assessment_repository] = override_repo
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/assessments/user/{uid}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == expected_len
        if check_disclaimer:
            assert data[0]['body_age_disclaimer'] == BODY_AGE_DISCLAIMER

    def test_post_assessment_response_includes_body_age_disclaimer(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.assessment_routes import get_assessment_repository, get_user_repository
        from src.application.dtos.assessment_dtos import BODY_AGE_DISCLAIMER
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.save.return_value = None
        mock_user_repo = AsyncMock()
        mock_user_repo.find_by_id.return_value = make_user_entity(user_id=uid)

        async def override_repo(db=None):
            return mock_repo

        async def override_user_repo(db=None):
            return mock_user_repo
        app.dependency_overrides[get_assessment_repository] = override_repo
        app.dependency_overrides[get_user_repository] = override_user_repo
        with TestClient(app) as client:
            resp = client.post('/api/v1/assessments', json={'user_id': str(uid), 'real_age': 30, 'responses': {'q1': 8, 'q2': 7}})
        assert resp.status_code == 201
        assert resp.json()['body_age_disclaimer'] == BODY_AGE_DISCLAIMER

    @pytest.mark.parametrize('has_data', [False, True])
    def test_get_user_assessments_alias(self, app_with_mock_db, has_data):
        app, _ = app_with_mock_db
        from src.adapters.api.routes.assessment_routes import get_assessment_repository
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.find_by_user_id.return_value = [make_assessment_entity(uid)] if has_data else []

        async def override_repo(db=None):
            return mock_repo
        app.dependency_overrides[get_assessment_repository] = override_repo
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/assessments')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == (1 if has_data else 0)
        if has_data:
            assert data[0]['user_id'] == str(uid) and 'body_age_disclaimer' in data[0]

class TestInstructorRoutes:

    def test_list_instructors_empty(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        mock_uc = AsyncMock()
        mock_uc.list_instructors.return_value = []

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.get('/api/v1/instructors')
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_instructors_returns_items(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        from src.application.dtos.instructor_dtos import InstructorResponse
        iid = uuid4()
        mock_uc = AsyncMock()
        mock_uc.list_instructors.return_value = [InstructorResponse(id=iid, name='Coach', certifications=['ACE'], specializations='Fuerza', rating_avg=4.5, active_users_count=2)]

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.get('/api/v1/instructors')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Coach'
        assert data[0]['rating_avg'] == 4.5
        assert data[0]['active_users_count'] == 2

    def test_get_instructor_by_id_found(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        from src.application.dtos.instructor_dtos import InstructorResponse
        iid = uuid4()
        mock_uc = AsyncMock()
        mock_uc.get_instructor_by_id.return_value = InstructorResponse(id=iid, name='Ana', certifications=['NASM'], specializations='', rating_avg=4.0, active_users_count=1, certificate_status='verified')

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/instructors/{iid}')
        assert resp.status_code == 200
        assert resp.json()['name'] == 'Ana'

    def test_get_instructor_by_id_not_found(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        mock_uc = AsyncMock()
        mock_uc.get_instructor_by_id.return_value = None

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/instructors/{uuid4()}')
        assert resp.status_code == 404

    def test_assign_instructor_success(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        uid, iid = (uuid4(), uuid4())
        mock_uc = AsyncMock()
        mock_uc.assign_instructor.return_value = None

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post(f'/api/v1/users/{uid}/assign-instructor', json={'instructor_id': str(iid)})
        assert resp.status_code == 200
        assert 'message' in resp.json()

    def test_assign_instructor_not_found_returns_404(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        mock_uc = AsyncMock()
        mock_uc.assign_instructor.side_effect = ValueError('Instructor not found')

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post(f'/api/v1/users/{uuid4()}/assign-instructor', json={'instructor_id': str(uuid4())})
        assert resp.status_code == 404

    def test_rate_instructor_without_user_id_returns_401(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        mock_uc = AsyncMock()

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post(f'/api/v1/instructors/{uuid4()}/rate', json={'rating': 5})
        assert resp.status_code == 401

    def test_create_instructor_returns_201(self, app_with_mock_db):
        from src.adapters.api.routes.instructor_routes import get_instructor_use_cases
        from src.application.dtos.instructor_dtos import InstructorResponse
        iid = uuid4()
        mock_uc = AsyncMock()
        mock_uc.create_instructor.return_value = InstructorResponse(id=iid, name='New Coach', certifications=['ACE'], specializations='Cardio', rating_avg=0.0, active_users_count=0)

        async def override_uc(db=None):
            return mock_uc
        app, _ = app_with_mock_db
        app.dependency_overrides[get_instructor_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post('/api/v1/instructors', json={'name': 'New Coach', 'certifications': ['ACE'], 'specializations': 'Cardio'})
        assert resp.status_code == 201
        assert resp.json()['name'] == 'New Coach'

class TestPhysicalRecordRoutes:

    def test_create_record_success(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.physical_record_routes import get_use_cases
        from src.application.use_cases.physical_record_use_cases import PhysicalRecordUseCases
        from src.application.dtos.physical_record_dtos import PhysicalRecordResponse
        from src.domain.entities.physical_record import ActivityLevel
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.save.return_value = None

        async def override_use_cases(db=None):
            return PhysicalRecordUseCases(mock_repo)
        app.dependency_overrides[get_use_cases] = override_use_cases
        with TestClient(app) as client:
            resp = client.post(f'/api/v1/users/{uid}/physical-records', json={'weight': 75.0, 'height': 175.0, 'activity_level': 'MODERATE'})
        assert resp.status_code == 201
        data = resp.json()
        assert data['weight'] == 75.0
        assert 'bmi' in data

    def test_get_physical_records_history(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.physical_record_routes import get_use_cases
        from src.application.use_cases.physical_record_use_cases import PhysicalRecordUseCases
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.find_by_user_id.return_value = [make_physical_record_entity(uid)]

        async def override_use_cases(db=None):
            return PhysicalRecordUseCases(mock_repo)
        app.dependency_overrides[get_use_cases] = override_use_cases
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/physical-records')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1
        assert len(data['records']) == 1

class TestTrainingRoutes:

    def test_create_routine_success(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.training_routes import get_use_cases
        from src.application.dtos.training_dtos import RoutineResponse, RoutineExerciseDTO
        exercise_id = uuid4()
        creator_id = uuid4()
        routine = make_routine_entity()
        routine_response = RoutineResponse(id=routine.id, name=routine.name, description=routine.description, goal=routine.goal, level=routine.level, exercises=[RoutineExerciseDTO(exercise_id=routine.exercises[0].exercise_id, sets=routine.exercises[0].sets, reps=routine.exercises[0].reps, rest_seconds=routine.exercises[0].rest_seconds)], creator_id=routine.creator_id)
        mock_uc = AsyncMock()
        mock_uc.create_routine.return_value = routine_response

        async def override_uc(db=None):
            return mock_uc
        app.dependency_overrides[get_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post('/api/v1/training/routines', json={'name': 'Full Body', 'description': 'All muscles', 'goal': 'STRENGTH', 'level': 'BEGINNER', 'exercises': [{'exercise_id': str(exercise_id), 'sets': 3, 'reps': 10, 'rest_seconds': 60}], 'creator_id': str(creator_id)})
        assert resp.status_code == 201

    def test_assign_routine_success(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.training_routes import get_use_cases
        uid = uuid4()
        mock_uc = AsyncMock()
        mock_uc.assign_routine.return_value = True

        async def override_uc(db=None):
            return mock_uc
        app.dependency_overrides[get_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post(f'/api/v1/users/{uid}/routines/assign', json={'routine_id': str(uuid4())})
        assert resp.status_code == 200

    def test_get_active_routine_not_found_returns_404(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.training_routes import get_use_cases
        uid = uuid4()
        mock_uc = AsyncMock()
        mock_uc.get_active_routine.return_value = None

        async def override_uc(db=None):
            return mock_uc
        app.dependency_overrides[get_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/routines/active')
        assert resp.status_code == 404

    def test_get_active_routine_returns_routine(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.training_routes import get_use_cases
        uid = uuid4()
        routine = make_routine_entity()
        from src.application.dtos.training_dtos import RoutineResponse, RoutineExerciseDTO
        routine_response = RoutineResponse(id=routine.id, name=routine.name, description=routine.description, goal=routine.goal, level=routine.level, exercises=[RoutineExerciseDTO(exercise_id=routine.exercises[0].exercise_id, sets=routine.exercises[0].sets, reps=routine.exercises[0].reps, rest_seconds=routine.exercises[0].rest_seconds)], creator_id=routine.creator_id)
        mock_uc = AsyncMock()
        mock_uc.get_active_routine.return_value = routine_response

        async def override_uc(db=None):
            return mock_uc
        app.dependency_overrides[get_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/routines/active')
        assert resp.status_code == 200

    def test_complete_workout_no_assignment_returns_400(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.training_routes import get_use_cases
        uid = uuid4()
        mock_uc = AsyncMock()
        mock_uc.complete_workout.side_effect = ValueError('No active routine assigned')

        async def override_uc(db=None):
            return mock_uc
        app.dependency_overrides[get_use_cases] = override_uc
        with TestClient(app) as client:
            resp = client.post(f'/api/v1/workouts/complete', params={'user_id': str(uid)}, json={'effort_level': 7})
        assert resp.status_code == 400

class TestNutritionRoutes:

    def test_create_nutrition_plan_success(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.nutrition_routes import get_repo
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.save.return_value = None

        async def override_repo(db=None):
            return mock_repo
        app.dependency_overrides[get_repo] = override_repo
        with TestClient(app) as client:
            resp = client.post('/api/v1/nutrition/plans', params={'user_id': str(uid)}, json={'name': 'Week 1', 'description': 'Cutting phase', 'week_number': 10, 'year': 2026, 'daily_plans': [{'day_of_week': 0, 'meals': [{'name': 'Oats', 'description': 'Breakfast'}]}], 'is_active': True})
        assert resp.status_code == 201
        data = resp.json()
        assert data['name'] == 'Week 1'

    def test_get_active_plan_not_found_returns_404(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.nutrition_routes import get_repo
        uid = uuid4()
        mock_repo = AsyncMock()
        mock_repo.find_active_by_user_id.return_value = None

        async def override_repo(db=None):
            return mock_repo
        app.dependency_overrides[get_repo] = override_repo
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/nutrition/active')
        assert resp.status_code == 404

    def test_get_active_plan_returns_plan(self, app_with_mock_db):
        app, session = app_with_mock_db
        from src.adapters.api.routes.nutrition_routes import get_repo
        uid = uuid4()
        plan = make_nutrition_plan_entity(user_id=uid)
        mock_repo = AsyncMock()
        mock_repo.find_active_by_user_id.return_value = plan

        async def override_repo(db=None):
            return mock_repo
        app.dependency_overrides[get_repo] = override_repo
        with TestClient(app) as client:
            resp = client.get(f'/api/v1/users/{uid}/nutrition/active')
        assert resp.status_code == 200
        data = resp.json()
        assert data['name'] == 'Week 1'
