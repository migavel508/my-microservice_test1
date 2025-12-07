import pytest
from fastapi.testclient import TestClient
from pydantic import EmailStr
from generated.app import app, Employee, EmployeeCreate, employees_db, next_employee_id

client = TestClient(app)

# Fixtures
@pytest.fixture
def clear_db():
    """
    Fixture to clear the database before each test.
    """
    employees_db.clear()
    next_employee_id = 3
    yield
    employees_db.append(Employee(
        id=1,
        name="John Doe",
        email=EmailStr("john.doe@example.com"),
        department="Engineering",
        position="Senior Developer",
        created_at=datetime.utcnow().isoformat()
    ))
    employees_db.append(Employee(
        id=2,
        name="Jane Smith",
        email=EmailStr("jane.smith@example.com"),
        department="Product",
        position="Product Manager",
        created_at=datetime.utcnow().isoformat()
    ))

# Test Cases
def test_health_check():
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.usefixtures("clear_db")
def test_get_all_employees():
    """
    Test the get all employees endpoint.
    """
    response = client.get("/employee")
    assert response.status_code == 200
    assert len(response.json()) == 2

@pytest.mark.parametrize("employee_id", [1, 2])
@pytest.mark.usefixtures("clear_db")
def test_get_employee_success(employee_id):
    """
    Test the get employee endpoint when the employee exists.
    """
    response = client.get(f"/employee/{employee_id}")
    assert response.status_code == 200
    assert response.json()["id"] == employee_id

@pytest.mark.usefixtures("clear_db")
def test_get_employee_failure():
    """
    Test the get employee endpoint when the employee does not exist.
    """
    response = client.get("/employee/999")
    assert response.status_code == 404

@pytest.mark.usefixtures("clear_db")
def test_create_employee_success():
    """
    Test the create employee endpoint with valid data.
    """
    employee_data = EmployeeCreate(
        name="Test Employee",
        email=EmailStr("test.employee@example.com"),
        department="Testing",
        position="Test Engineer",
    )
    response = client.post("/employee", json=employee_data.dict())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Employee"

@pytest.mark.usefixtures("clear_db")
def test_create_employee_duplicate_email():
    """
    Test the create employee endpoint with a duplicate email.
    """
    employee_data = EmployeeCreate(
        name="Test Employee",
        email=EmailStr("john.doe@example.com"),
        department="Testing",
        position="Test Engineer",
    )
    response = client.post("/employee", json=employee_data.dict())
    assert response.status_code == 400