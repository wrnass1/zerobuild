import pytest


def test_get_current_user_id_parses_sub():
    from jose import jwt
    from auth_deps import decode_token

    token = jwt.encode({"sub": "7"}, "test-secret", algorithm="HS256")
    payload = decode_token(token)
    assert payload["sub"] == "7"


def test_decode_token_rejects_invalid():
    from jose import jwt
    from auth_deps import decode_token

    token = jwt.encode({"sub": "7"}, "wrong", algorithm="HS256")
    with pytest.raises(Exception):
        decode_token(token)

