"""Tests for health endpoint."""


def test_health_check(client):
    """GET /health returns 200 with status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_health_check_no_auth_required(client):
    """Health check does not require authentication."""
    response = client.get("/health")
    assert response.status_code == 200
