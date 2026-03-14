"""Tests for report endpoints."""
import uuid
import pytest


def test_get_project_report(client, auth_headers, test_project, test_photo, test_detection, test_classification, test_damage_assessment):
    """GET /reports/{project_id} returns aggregate report."""
    response = client.get(f"/reports/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == str(test_project.id)
    assert data["project_name"] == "Test Project"
    assert data["total_photos"] >= 1
    assert isinstance(data["material_summary"], list)
    assert isinstance(data["damage_summary"], list)
    assert "correction_stats" in data
    assert "total_detections" in data["correction_stats"]
    assert "corrections_made" in data["correction_stats"]
    assert "accuracy_rate" in data["correction_stats"]


def test_get_project_report_material_summary(client, auth_headers, test_project, test_photo, test_classification):
    """Report includes material summary from classifications."""
    response = client.get(f"/reports/{test_project.id}", headers=auth_headers)
    data = response.json()
    assert len(data["material_summary"]) >= 1
    mat = data["material_summary"][0]
    assert "material" in mat
    assert "total_count" in mat
    assert "unit" in mat


def test_get_project_report_damage_summary(client, auth_headers, test_project, test_photo, test_damage_assessment):
    """Report includes damage summary."""
    response = client.get(f"/reports/{test_project.id}", headers=auth_headers)
    data = response.json()
    assert len(data["damage_summary"]) >= 1
    dmg = data["damage_summary"][0]
    assert dmg["type"] == "hail_impact"
    assert dmg["severity"] == "high"


def test_get_project_report_accuracy(client, auth_headers, test_project, test_photo, test_detection):
    """Report accuracy rate is correct with no corrections."""
    response = client.get(f"/reports/{test_project.id}", headers=auth_headers)
    data = response.json()
    assert data["correction_stats"]["total_detections"] >= 1
    assert data["correction_stats"]["corrections_made"] == 0
    assert data["correction_stats"]["accuracy_rate"] == 1.0


def test_get_project_report_not_found(client, auth_headers):
    """GET /reports/{project_id} returns 404 for unknown project."""
    response = client.get(f"/reports/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def test_get_project_report_empty(client, auth_headers, test_project):
    """GET /reports/{project_id} works with no photos."""
    response = client.get(f"/reports/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_photos"] == 0
    assert data["material_summary"] == []
    assert data["damage_summary"] == []


def test_get_project_report_no_auth(client, test_project):
    """GET /reports/{project_id} requires authentication."""
    response = client.get(f"/reports/{test_project.id}")
    assert response.status_code == 401
