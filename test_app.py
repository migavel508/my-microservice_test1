import pytest
from fastapi.testclient import TestClient
from app import app, employees_db, Employee
from datetime import datetime

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    global employees_db
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
    yield
    employees_db.clear()

class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test that health check returns 200 and correct structure"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "astraflow-service"
        assert "timestamp" in data
        assert "environment" in data
    
    def test_health_check_response_schema(self, client):
        """Test that health check response has all required fields"""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "timestamp", "service", "environment"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

class TestGetAllEmployees:
    """Tests for GET /employee endpoint"""
    
    def test_get_all_employees_success(self, client):
        """Test retrieving all employees"""
        response = client.get("/employee")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_get_all_employees_structure(self, client):
        """Test that employee objects have correct structure"""
        response = client.get("/employee")
        data = response.json()
        
        required_fields = ["id", "name", "email", "department", "position", "created_at"]
        for employee in data:
            for field in required_fields:
                assert field in employee, f"Missing field: {field}"
    
    def test_get_all_employees_empty_db(self, client):
        """Test getting employees when database is empty"""
        employees_db.clear()
        response = client.get("/employee")
        assert response.status_code == 200
        assert response.json() == []

class TestGetEmployeeById:
    """Tests for GET /employee/{id} endpoint"""
    
    def test_get_employee_by_id_success(self, client):
        """Test retrieving a specific employee by ID"""
        response = client.get("/employee/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
    
    def test_get_employee_by_id_not_found(self, client):
        """Test retrieving non-existent employee"""
        response = client.get("/employee/999")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_employee_invalid_id_type(self, client):
        """Test with invalid ID type"""
        response = client.get("/employee/invalid")
        assert response.status_code == 422  # Validation error

class TestCreateEmployee:
    """Tests for POST /employee endpoint"""
    
    def test_create_employee_success(self, client):
        """Test creating a new employee"""
        new_employee = {
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "department": "Marketing",
            "position": "Marketing Manager"
        }
        
        response = client.post("/employee", json=new_employee)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == new_employee["name"]
        assert data["email"] == new_employee["email"]
        assert data["department"] == new_employee["department"]
        assert data["position"] == new_employee["position"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_employee_duplicate_email(self, client):
        """Test creating employee with duplicate email"""
        duplicate_employee = {
            "name": "John Clone",
            "email": "john.doe@example.com",  # Already exists
            "department": "Engineering",
            "position": "Developer"
        }
        
        response = client.post("/employee", json=duplicate_employee)
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()
    
    def test_create_employee_invalid_email(self, client):
        """Test creating employee with invalid email format"""
        invalid_employee = {
            "name": "Bob Smith",
            "email": "not-an-email",
            "department": "Sales",
            "position": "Sales Rep"
        }
        
        response = client.post("/employee", json=invalid_employee)
        assert response.status_code == 422  # Validation error
    
    def test_create_employee_missing_fields(self, client):
        """Test creating employee with missing required fields"""
        incomplete_employee = {
            "name": "Incomplete User",
            "email": "incomplete@example.com"
            # Missing department and position
        }
        
        response = client.post("/employee", json=incomplete_employee)
        assert response.status_code == 422  # Validation error
    
    def test_create_employee_increments_id(self, client):
        """Test that employee IDs are incremented correctly"""
        employee1 = {
            "name": "Employee One",
            "email": "emp1@example.com",
            "department": "IT",
            "position": "Developer"
        }
        
        employee2 = {
            "name": "Employee Two",
            "email": "emp2@example.com",
            "department": "IT",
            "position": "Developer"
        }
        
        response1 = client.post("/employee", json=employee1)
        id1 = response1.json()["id"]
        
        response2 = client.post("/employee", json=employee2)
        id2 = response2.json()["id"]
        
        assert id2 == id1 + 1

class TestIntegration:
    """Integration tests for multiple operations"""
    
    def test_create_and_retrieve_employee(self, client):
        """Test creating an employee and then retrieving it"""
        new_employee = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "department": "QA",
            "position": "QA Engineer"
        }
        
        # Create employee
        create_response = client.post("/employee", json=new_employee)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # Retrieve employee
        get_response = client.get(f"/employee/{created_id}")
        assert get_response.status_code == 200
        
        retrieved_employee = get_response.json()
        assert retrieved_employee["name"] == new_employee["name"]
        assert retrieved_employee["email"] == new_employee["email"]
    
    def test_create_multiple_employees_and_list(self, client):
        """Test creating multiple employees and listing all"""
        initial_count = len(client.get("/employee").json())
        
        employees_to_create = [
            {
                "name": f"Test User {i}",
                "email": f"test{i}@example.com",
                "department": "Testing",
                "position": "Tester"
            }
            for i in range(3)
        ]
        
        for emp in employees_to_create:
            response = client.post("/employee", json=emp)
            assert response.status_code == 201
        
        # Get all employees
        all_employees = client.get("/employee").json()
        assert len(all_employees) == initial_count + 3
