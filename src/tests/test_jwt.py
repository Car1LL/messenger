from messenger.utils.jwt.jwt import create_access_token, decode_access_token
from messenger.utils.jwt.jwt_config import jwt_settings
from datetime import datetime, timezone, timedelta
import pytest
import jwt

TEST_SECRET_KEY = "test-secret-key-for-jwt-long-for-32-bytes-super-long"

def test_create_and_decode_access_token(monkeypatch):
    monkeypatch.setattr(
        jwt_settings,
        "SECRET_KEY",
        TEST_SECRET_KEY
    )

    token = create_access_token(123)

    user_id = decode_access_token(token)

    assert user_id == 123

def test_create_access_token_exp(monkeypatch):
    monkeypatch.setattr(
        jwt_settings,
        "SECRET_KEY",
        TEST_SECRET_KEY
    )

    token = create_access_token(123)

    payload = jwt.decode(
        token,
        TEST_SECRET_KEY,
        algorithms=["HS256"]
    )

    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()

def test_expired_access_token(monkeypatch):
    monkeypatch.setattr(
        jwt_settings,
        "SECRET_KEY",
        TEST_SECRET_KEY
    )

    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)

    token = jwt.encode(
        {"sub": 123,
         "exp": expired_time},
         TEST_SECRET_KEY,
         algorithm="HS256"
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)

def test_invalid_access_token(monkeypatch):
    monkeypatch.setattr(
        jwt_settings,
        "SECRET_KEY",
        TEST_SECRET_KEY
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("this-is-not-a-jwt")

def test_access_token_wrong_secret(monkeypatch):
    monkeypatch.setattr(
        jwt_settings,
        "SECRET_KEY",
        TEST_SECRET_KEY
    )

    token = jwt.encode(
        {"sub": 123,
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
         "another-secret-key-that-is-at-least-32-bytes-long",
         algorithm="HS256"
    )

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(token)

def test_access_token_missing(monkeypatch):
    monkeypatch.setattr(
        jwt_settings,
        "SECRET_KEY",
        TEST_SECRET_KEY
    )

    token = None

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)