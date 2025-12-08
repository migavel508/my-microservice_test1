import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch
from datetime import datetime
from generated.app import app, EmployeeBase, Employee, EmployeeCreate, HealthResponse, employees_db

client = TestClient(app)

# Fixtures
@pytest.fixture
def employee_create():
    return EmployeeCreate(name="New Employee", email="new.employee@example.com", department="HR", position="HR Manager")

@pytest.fixture
def health_response():
    return HealthResponse(status="healthy", timestamp=datetime.utcnow().isoformat(), service="astraflow-service", environment="production")

# Tests
@patch("generated.app.logger")
def test_health_check(mock_logger, health_response):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == health_response.dict()
    mock_logger.info.assert_called_once_with("Health check requested")

@patch("generated.app.logger")
def test_get_all_employees(mock_logger):
    response = client.get("/employee")
    assert response.status_code == 200
    assert len(response.json()) == len(employees_db)
    mock_logger.info.assert_called_once()

@pytest.mark.parametrize("employee_id,expected_status", [(1, 200), (3, 404)])
@patch("generated.app.logger")
def test_get_employee(mock_logger, employee_id, expected_status):
    response = client.get(f"/employee/{employee_id}")
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == employees_db[employee_id - 1].dict()
    else:
        assert "detail" in response.json()
        mock_logger.warning.assert_called_once()

@patch("generated.app.logger")
def test_create_employee(mock_logger, employee_create):
    response = client.post("/employee", json=employee_create.dict())
    assert response.status_code == 201
    assert response.json()["name"] == employee_create.name
    mock_logger.info.assert_called()

@patch("generated.app.logger")
def test_create_employee_duplicate_email(mock_logger, employee_create):
    employees_db.append(Employee(id=3, name=employee_create.name, email=employee_create.email, department=employee_create.department, position=employee_create.position, created_at=datetime.utcnow().isoformat()))
    response = client.post("/employee", json=employee_create.dict())
    assert response.status_code == 400
    assert "detail" in response.json()
    mock_logger.warning.assert_called_once()

@patch("generated.app.logger")
def test_startup_event(mock_logger):
    with patch.object(app, "logger") as mock_logger:
        app.router.lifespan.startup()
    mock_logger.info.assert_called()

@patch("generated.app.logger")
def test_shutdown_event(mock_logger):
    with patch.object(app, "logger") as mock_logger:
        app.router.lifespan.shutdown()
    mock_logger.info.assert_called()