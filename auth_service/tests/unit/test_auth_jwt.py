from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt


def test_hash_and_verify_password():
    from auth_jwt import hash_password, verify_password

    hashed = hash_password("pass123")
    assert hashed != "pass123"
    assert verify_password("pass123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token_roundtrip():
    from auth_jwt import create_access_token, decode_token
    from config import settings

    token = create_access_token({"sub": "42"})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload

    # exp should be in the future
    exp = payload["exp"]
    assert isinstance(exp, int)
    assert exp > int(datetime.now(timezone.utc).timestamp())


def test_decode_token_rejects_expired():
    from auth_jwt import decode_token
    from config import settings

    expired = datetime.now(timezone.utc) - timedelta(minutes=10)
    token = jwt.encode({"sub": "1", "exp": expired}, settings.secret_key, algorithm=settings.algorithm)

    with pytest.raises(Exception) as exc:
        decode_token(token)
    # HTTPException from FastAPI has .status_code, but we don't import it here
    assert "Невалидный" in str(exc.value) or "401" in str(exc.value)

