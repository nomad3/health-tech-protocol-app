from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_hash_password():
    """Test password hashing."""
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 50  # Argon2 hashes are long


def test_verify_password():
    """Test password verification."""
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    payload = {"sub": "user@example.com", "role": "patient"}
    token = create_access_token(payload)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50


def test_decode_token():
    """Test JWT token decoding."""
    payload = {"sub": "user@example.com", "role": "patient"}
    token = create_access_token(payload)

    decoded = decode_token(token)
    assert decoded["sub"] == "user@example.com"
    assert decoded["role"] == "patient"
