import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime
from generated.app import app, Employee, EmployeeCreate, employees_db, next_employee_id
from unittest.mock import patch

client = TestClient(app)

# Fixtures

@pytest.fixture
def test_employee():
    """
    Fixture for employee data
    """
    return Employee(
        id=1,
        name="Test Employee",
        email="test.employee@example.com",
        department="Test Department",
        position="Test Position",
        created_at=datetime.utcnow().isoformat()
    )

@pytest.fixture
def test_employee_create():
    """
    Fixture for employee data for creation
    """
    return EmployeeCreate(
        name="New Test Employee",
        email="new.test.employee@example.com",
        department="New Test Department",
        position="New Test Position"
    )


# Tests

def test_health_check():
    """
    Test health_check endpoint
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_all_employees():
    """
    Test get_all_employees endpoint
    """
    response = client.get("/employee")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_employee(test_employee):
    """
    Test get_employee endpoint
    """
    response = client.get(f"/employee/{test_employee.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_employee.id

def test_get_employee_not_found():
    """
    Test get_employee endpoint for non-existing employee
    """
    with pytest.raises(HTTPException):
        client.get("/employee/999")

def test_create_employee(test_employee_create):
    """
    Test create_employee endpoint
    """
    response = client.post("/employee", json=test_employee_create.dict())
    assert response.status_code == 201
    assert response.json()["name"] == test_employee_create.name

def test_create_employee_duplicate_email(test_employee):
    """
    Test create_employee endpoint with duplicate email
    """
    duplicate_employee = test_employee.dict()
    duplicate_employee.pop("id")
    with pytest.raises(HTTPException):
        client.post("/employee", json=duplicate_employee)

@patch("generated.app.startup_event")
def test_startup_event(mock_startup_event):
    """
    Test startup_event function
    """
    mock_startup_event()
    mock_startup_event.assert_called_once()

@patch("generated.app.shutdown_event")
def test_shutdown_event(mock_shutdown_event):
    """
    Test shutdown_event function
    """
    mock_shutdown_event()
    mock_shutdown_event.assert_called_once()