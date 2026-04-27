import pytest


def test_decode_token_accepts_valid_token():
    from jose import jwt
    from auth_deps import decode_token

    token = jwt.encode({"sub": "10"}, "test-secret", algorithm="HS256")
    payload = decode_token(token)
    assert payload["sub"] == "10"


def test_decode_token_rejects_invalid_signature():
    from jose import jwt
    from auth_deps import decode_token

    token = jwt.encode({"sub": "10"}, "wrong-secret", algorithm="HS256")
    with pytest.raises(Exception):
        decode_token(token)

