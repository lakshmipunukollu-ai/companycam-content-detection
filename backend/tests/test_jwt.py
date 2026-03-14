"""Tests for JWT handler."""
import pytest
import uuid

from app.auth.jwt_handler import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def test_hash_password():
    """Hashing produces a different string than the original."""
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert len(hashed) > 20


def test_verify_password_correct():
    """Verifying with correct password returns True."""
    hashed = hash_password("secret")
    assert verify_password("secret", hashed) is True


def test_verify_password_wrong():
    """Verifying with wrong password returns False."""
    hashed = hash_password("secret")
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    """Token can be created and decoded."""
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id, "contractor")
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == "contractor"


def test_decode_invalid_token():
    """Decoding invalid token raises HTTPException."""
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        decode_token("invalid.token.here")
    assert exc_info.value.status_code == 401
