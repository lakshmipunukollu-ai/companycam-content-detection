"""Tests for photo endpoints."""
import io
import os
import uuid
import pytest


def test_upload_photo(client, auth_headers, test_project):
    """POST /photos/upload saves a photo."""
    # Create a fake image file
    image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    response = client.post(
        "/photos/upload",
        files={"file": ("test.png", io.BytesIO(image_data), "image/png")},
        data={"project_id": str(test_project.id), "photo_type": "roof"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["photo_type"] == "roof"
    assert data["status"] == "pending"
    assert data["project_id"] == str(test_project.id)
    assert data["filename"].endswith(".png")


def test_upload_photo_default_type(client, auth_headers, test_project):
    """POST /photos/upload defaults to general type."""
    image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    response = client.post(
        "/photos/upload",
        files={"file": ("test.png", io.BytesIO(image_data), "image/png")},
        data={"project_id": str(test_project.id)},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["photo_type"] == "general"


def test_upload_photo_no_auth(client, test_project):
    """POST /photos/upload requires authentication."""
    image_data = b'\x89PNG\r\n\x1a\n'
    response = client.post(
        "/photos/upload",
        files={"file": ("test.png", io.BytesIO(image_data), "image/png")},
        data={"project_id": str(test_project.id)},
    )
    assert response.status_code == 401


def test_get_photo(client, auth_headers, test_photo):
    """GET /photos/{id} returns photo details."""
    response = client.get(f"/photos/{test_photo.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_photo.jpg"
    assert data["photo_type"] == "roof"
    assert data["status"] == "completed"


def test_get_photo_not_found(client, auth_headers):
    """GET /photos/{id} returns 404 for unknown id."""
    response = client.get(f"/photos/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def test_get_photo_results(client, auth_headers, test_photo, test_detection, test_classification, test_damage_assessment):
    """GET /photos/{id}/results returns full analysis results."""
    response = client.get(f"/photos/{test_photo.id}/results", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["photo_id"] == str(test_photo.id)
    assert data["status"] == "completed"
    assert len(data["detections"]) >= 1
    assert len(data["classifications"]) >= 1
    assert len(data["damage_assessments"]) >= 1
    assert isinstance(data["requires_human_review"], bool)

    # Check detection structure
    det = data["detections"][0]
    assert "label" in det
    assert "confidence" in det
    assert "bbox" in det
    assert "x" in det["bbox"]


def test_get_photo_results_empty(client, auth_headers, test_photo):
    """GET /photos/{id}/results works with no detections."""
    response = client.get(f"/photos/{test_photo.id}/results", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["detections"] == []
    assert data["classifications"] == []


def test_list_photos(client, auth_headers, test_photo):
    """GET /photos returns user's photos."""
    response = client.get("/photos", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_list_photos_by_project(client, auth_headers, test_photo, test_project):
    """GET /photos?project_id=x filters by project."""
    response = client.get(f"/photos?project_id={test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(p["project_id"] == str(test_project.id) for p in data)


def test_list_photos_by_status(client, auth_headers, test_photo):
    """GET /photos?status=completed filters by status."""
    response = client.get("/photos?status=completed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(p["status"] == "completed" for p in data)


def test_delete_photo(client, auth_headers, test_photo):
    """DELETE /photos/{id} removes the photo."""
    response = client.delete(f"/photos/{test_photo.id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify deleted
    response = client.get(f"/photos/{test_photo.id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_photo_not_found(client, auth_headers):
    """DELETE /photos/{id} returns 404 for unknown id."""
    response = client.delete(f"/photos/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
