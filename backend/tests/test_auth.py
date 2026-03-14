"""Tests for auth endpoints."""
import pytest


def test_register_user(client):
    """POST /auth/register creates a new user."""
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "password123",
        "full_name": "New User",
        "role": "contractor",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["full_name"] == "New User"
    assert data["user"]["role"] == "contractor"


def test_register_duplicate_email(client):
    """POST /auth/register rejects duplicate email."""
    payload = {
        "email": "dup@example.com",
        "password": "password123",
        "full_name": "First User",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "password456",
        "full_name": "Second User",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_default_role(client):
    """POST /auth/register defaults to contractor role."""
    response = client.post("/auth/register", json={
        "email": "default@example.com",
        "password": "password123",
        "full_name": "Default Role",
    })
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "contractor"


def test_login_valid(client):
    """POST /auth/login returns token for valid credentials."""
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "mypassword",
        "full_name": "Login User",
    })
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "login@example.com"


def test_login_invalid_password(client):
    """POST /auth/login rejects wrong password."""
    client.post("/auth/register", json={
        "email": "badpw@example.com",
        "password": "correct",
        "full_name": "Bad PW",
    })
    response = client.post("/auth/login", json={
        "email": "badpw@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """POST /auth/login rejects unknown email."""
    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "password",
    })
    assert response.status_code == 401


def test_get_me(client, auth_headers):
    """GET /auth/me returns current user info."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "test_" in data["email"]
    assert data["full_name"] == "Test User"


def test_get_me_no_auth(client):
    """GET /auth/me requires authentication."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    """GET /auth/me rejects invalid token."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
