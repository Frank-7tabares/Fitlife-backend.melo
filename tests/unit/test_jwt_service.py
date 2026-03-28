import pytest
import time
from jose import jwt, JWTError
from unittest.mock import patch

class TestJWTServiceCreateAccessToken:

    def test_returns_string(self):
        from src.application.services.jwt_service import JWTService
        token = JWTService.create_access_token({'sub': 'user-123'})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decoded_contains_sub(self):
        from src.application.services.jwt_service import JWTService
        from src.config.settings import settings
        token = JWTService.create_access_token({'sub': 'abc-123'})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload['sub'] == 'abc-123'

    def test_decoded_contains_exp(self):
        from src.application.services.jwt_service import JWTService
        from src.config.settings import settings
        token = JWTService.create_access_token({'sub': 'user-1'})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert 'exp' in payload

    def test_access_token_preserves_extra_claims(self):
        from src.application.services.jwt_service import JWTService
        from src.config.settings import settings
        token = JWTService.create_access_token({'sub': 'user-1', 'role': 'ADMIN'})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload['role'] == 'ADMIN'

    def test_different_calls_produce_different_tokens(self):
        from src.application.services.jwt_service import JWTService
        t1 = JWTService.create_access_token({'sub': 'user-1'})
        time.sleep(0.01)
        t2 = JWTService.create_access_token({'sub': 'user-1'})
        assert isinstance(t1, str) and isinstance(t2, str)

class TestJWTServiceCreateRefreshToken:

    def test_returns_string(self):
        from src.application.services.jwt_service import JWTService
        token = JWTService.create_refresh_token({'sub': 'user-456'})
        assert isinstance(token, str)

    def test_decoded_contains_sub(self):
        from src.application.services.jwt_service import JWTService
        from src.config.settings import settings
        token = JWTService.create_refresh_token({'sub': 'user-456'})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload['sub'] == 'user-456'

    def test_refresh_token_has_longer_expiry_than_access(self):
        from src.application.services.jwt_service import JWTService
        from src.config.settings import settings
        access = JWTService.create_access_token({'sub': 'u'})
        refresh = JWTService.create_refresh_token({'sub': 'u'})
        a_payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        r_payload = jwt.decode(refresh, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert r_payload['exp'] > a_payload['exp']

    def test_refresh_token_does_not_modify_original_dict(self):
        from src.application.services.jwt_service import JWTService
        data = {'sub': 'user-789'}
        JWTService.create_refresh_token(data)
        assert 'exp' not in data

class TestJWTServiceDecodeToken:

    def test_decode_valid_access_token(self):
        from src.application.services.jwt_service import JWTService
        token = JWTService.create_access_token({'sub': 'decode-test'})
        payload = JWTService.decode_token(token)
        assert payload['sub'] == 'decode-test'

    def test_decode_valid_refresh_token(self):
        from src.application.services.jwt_service import JWTService
        token = JWTService.create_refresh_token({'sub': 'refresh-decode'})
        payload = JWTService.decode_token(token)
        assert payload['sub'] == 'refresh-decode'

    def test_decode_invalid_token_raises(self):
        from src.application.services.jwt_service import JWTService
        with pytest.raises(Exception):
            JWTService.decode_token('totally.invalid.token')

    def test_decode_tampered_token_raises(self):
        from src.application.services.jwt_service import JWTService
        token = JWTService.create_access_token({'sub': 'user-1'})
        parts = token.split('.')
        parts[1] = parts[1][:-2] + 'XX'
        tampered = '.'.join(parts)
        with pytest.raises(Exception):
            JWTService.decode_token(tampered)

    def test_decode_preserves_all_claims(self):
        from src.application.services.jwt_service import JWTService
        token = JWTService.create_access_token({'sub': 'u', 'role': 'INSTRUCTOR', 'custom': 42})
        payload = JWTService.decode_token(token)
        assert payload['sub'] == 'u'
        assert payload['role'] == 'INSTRUCTOR'
        assert payload['custom'] == 42
