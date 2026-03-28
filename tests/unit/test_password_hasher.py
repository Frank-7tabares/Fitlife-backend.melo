import pytest
from src.infrastructure.security.password_hasher import PasswordHasher

class TestPasswordHasher:

    def test_hash_returns_different_value_than_plain(self):
        plain = 'MiPassword123!'
        hashed = PasswordHasher.hash(plain)
        assert hashed != plain

    def test_verify_correct_password_returns_true(self):
        plain = 'MiPassword123!'
        hashed = PasswordHasher.hash(plain)
        assert PasswordHasher.verify(plain, hashed) is True

    def test_verify_wrong_password_returns_false(self):
        hashed = PasswordHasher.hash('PasswordCorrecto')
        assert PasswordHasher.verify('PasswordIncorrecto', hashed) is False

    def test_same_password_produces_different_hashes(self):
        plain = 'MiPassword123!'
        hash1 = PasswordHasher.hash(plain)
        hash2 = PasswordHasher.hash(plain)
        assert hash1 != hash2

    def test_both_hashes_verify_correctly(self):
        plain = 'MiPassword123!'
        hash1 = PasswordHasher.hash(plain)
        hash2 = PasswordHasher.hash(plain)
        assert PasswordHasher.verify(plain, hash1) is True
        assert PasswordHasher.verify(plain, hash2) is True

    def test_empty_password_can_be_hashed(self):
        hashed = PasswordHasher.hash('')
        assert PasswordHasher.verify('', hashed) is True

    def test_very_long_password(self):
        long_password = 'A' * 72
        hashed = PasswordHasher.hash(long_password)
        assert PasswordHasher.verify(long_password, hashed) is True

    def test_special_characters_in_password(self):
        special = 'P@$$w0rd!#%^&*()'
        hashed = PasswordHasher.hash(special)
        assert PasswordHasher.verify(special, hashed) is True

    def test_unicode_password(self):
        unicode_pw = 'ContraseñaÄöü123'
        hashed = PasswordHasher.hash(unicode_pw)
        assert PasswordHasher.verify(unicode_pw, hashed) is True

    def test_verify_with_empty_hash_returns_false(self):
        with pytest.raises(Exception):
            PasswordHasher.verify('password', '')
