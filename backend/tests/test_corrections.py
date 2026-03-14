"""Tests for correction endpoints."""
import uuid
import pytest


def test_create_correction_label(client, auth_headers, test_photo, test_detection):
    """POST /photos/{id}/corrections creates a label correction."""
    response = client.post(
        f"/photos/{test_photo.id}/corrections",
        json={
            "detection_id": str(test_detection.id),
            "correction_type": "label",
            "corrected_label": "ridge_cap_shingle",
            "notes": "This is a ridge cap",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["correction_type"] == "label"
    assert data["corrected_label"] == "ridge_cap_shingle"
    assert data["original_label"] == "shingle_bundle"
    assert data["notes"] == "This is a ridge cap"
    assert data["photo_id"] == str(test_photo.id)
    assert data["detection_id"] == str(test_detection.id)


def test_create_correction_delete(client, auth_headers, test_photo, test_detection):
    """POST /photos/{id}/corrections creates a delete correction."""
    response = client.post(
        f"/photos/{test_photo.id}/corrections",
        json={
            "detection_id": str(test_detection.id),
            "correction_type": "delete",
            "notes": "False positive",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["correction_type"] == "delete"


def test_create_correction_photo_not_found(client, auth_headers):
    """POST /photos/{id}/corrections returns 404 for unknown photo."""
    response = client.post(
        f"/photos/{uuid.uuid4()}/corrections",
        json={"correction_type": "label", "corrected_label": "test"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_correction_detection_not_found(client, auth_headers, test_photo):
    """POST /photos/{id}/corrections returns 404 for unknown detection."""
    response = client.post(
        f"/photos/{test_photo.id}/corrections",
        json={
            "detection_id": str(uuid.uuid4()),
            "correction_type": "label",
            "corrected_label": "test",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_corrections(client, auth_headers, test_photo, test_detection):
    """GET /photos/{id}/corrections returns corrections list."""
    # Create a correction first
    client.post(
        f"/photos/{test_photo.id}/corrections",
        json={
            "detection_id": str(test_detection.id),
            "correction_type": "label",
            "corrected_label": "corrected",
        },
        headers=auth_headers,
    )

    response = client.get(f"/photos/{test_photo.id}/corrections", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["corrected_label"] == "corrected"


def test_get_corrections_empty(client, auth_headers, test_photo):
    """GET /photos/{id}/corrections returns empty list when none exist."""
    response = client.get(f"/photos/{test_photo.id}/corrections", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_correction_no_auth(client, test_photo):
    """POST /photos/{id}/corrections requires authentication."""
    response = client.post(
        f"/photos/{test_photo.id}/corrections",
        json={"correction_type": "label", "corrected_label": "test"},
    )
    assert response.status_code == 401
