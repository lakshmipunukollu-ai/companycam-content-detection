"""Tests for project endpoints."""
import pytest


def test_create_project(client, auth_headers):
    """POST /projects creates a new project."""
    response = client.post("/projects", json={
        "name": "New Project",
        "description": "Test description",
        "address": "456 Test Ave",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "Test description"
    assert data["address"] == "456 Test Ave"
    assert data["status"] == "active"
    assert data["id"]


def test_create_project_minimal(client, auth_headers):
    """POST /projects works with only required fields."""
    response = client.post("/projects", json={"name": "Minimal"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Minimal"


def test_create_project_no_auth(client):
    """POST /projects requires authentication."""
    response = client.post("/projects", json={"name": "Unauth"})
    assert response.status_code == 401


def test_list_projects(client, auth_headers, test_project):
    """GET /projects returns user's projects."""
    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "Test Project" for p in data)


def test_list_projects_no_auth(client):
    """GET /projects requires authentication."""
    response = client.get("/projects")
    assert response.status_code == 401


def test_get_project(client, auth_headers, test_project):
    """GET /projects/{id} returns project details."""
    response = client.get(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"


def test_get_project_not_found(client, auth_headers):
    """GET /projects/{id} returns 404 for unknown id."""
    import uuid
    response = client.get(f"/projects/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def test_update_project(client, auth_headers, test_project):
    """PUT /projects/{id} updates project fields."""
    response = client.put(f"/projects/{test_project.id}", json={
        "name": "Updated Name",
        "status": "completed",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "completed"


def test_update_project_partial(client, auth_headers, test_project):
    """PUT /projects/{id} only updates provided fields."""
    response = client.put(f"/projects/{test_project.id}", json={
        "description": "Updated desc",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated desc"
    assert data["name"] == "Test Project"  # unchanged


def test_delete_project(client, auth_headers, test_project):
    """DELETE /projects/{id} removes the project."""
    response = client.delete(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify deleted
    response = client.get(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_project_not_found(client, auth_headers):
    """DELETE /projects/{id} returns 404 for unknown id."""
    import uuid
    response = client.delete(f"/projects/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
