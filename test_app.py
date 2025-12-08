import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from generated.app import app, EmployeeCreate, Employee, HealthResponse, employees_db, next_employee_id

client = TestClient(app)

# Fixture for common setup
@pytest.fixture
def reset_data():
    employees_db.clear()
    employees_db.extend([
        Employee(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            department="Engineering",
            position="Senior Developer",
            created_at=datetime.utcnow().isoformat()
        ),
        Employee(
            id=2,
            name="Jane Smith",
            email="jane.smith@example.com",
            department="Product",
            position="Product Manager",
            created_at=datetime.utcnow().isoformat()
        )
    ])
    next_employee_id = 3

# Test health_check function
@pytest.mark.asyncio
async def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="astraflow-service",
        environment="production"
    ).dict()

# Test get_all_employees function
@pytest.mark.asyncio
async def test_get_all_employees(reset_data):
    response = client.get("/employee")
    assert response.status_code == 200
    assert response.json() == [employee.dict() for employee in employees_db]

# Test get_employee function
@pytest.mark.asyncio
@pytest.mark.parametrize("employee_id, status_code", [(1, 200), (3, 404)])
async def test_get_employee(employee_id, status_code, reset_data):
    response = client.get(f"/employee/{employee_id}")
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == [employee.dict() for employee in employees_db if employee.id == employee_id][0]

# Test create_employee function
@pytest.mark.asyncio
@pytest.mark.parametrize("employee_data, status_code", [
    (EmployeeCreate(name="Test User", email="test.user@example.com", department="Test", position="Test"), 201),
    (EmployeeCreate(name="Duplicate User", email="john.doe@example.com", department="Test", position="Test"), 400)
])
async def test_create_employee(employee_data, status_code, reset_data):
    response = client.post("/employee", json=employee_data.dict())
    assert response.status_code == status_code

# Test startup_event function
@patch("generated.app.logger")
@pytest.mark.asyncio
async def test_startup_event(mock_logger):
    mock_logger.info = MagicMock()
    await app.router.lifecycle.get("startup")[0]()
    assert mock_logger.info.call_count == 5

# Test shutdown_event function
@patch("generated.app.logger")
@pytest.mark.asyncio
async def test_shutdown_event(mock_logger):
    mock_logger.info = MagicMock()
    await app.router.lifecycle.get("shutdown")[0]()
    assert mock_logger.info.called_once_with("AstraFlow Employee Service Shutting Down")