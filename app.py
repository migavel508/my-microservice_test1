from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import logging
import os
import uvicorn

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AstraFlow Employee Service",
    description="Employee management microservice",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class EmployeeBase(BaseModel):
    """Base employee model"""
    name: str
    email: EmailStr
    department: str
    position: str

class EmployeeCreate(EmployeeBase):
    """Model for creating an employee"""
    pass

class Employee(EmployeeBase):
    """Complete employee model with ID"""
    id: int
    created_at: str

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    service: str
    environment: str

# In-memory data store
employees_db: List[Employee] = [
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
]
next_employee_id = 3

# API Endpoints
@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service is running.
    
    Returns:
        HealthResponse: Service health status
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="astraflow-service",
        environment=os.getenv("APP_ENV", "production")
    )

@app.get("/employee", response_model=List[Employee], status_code=status.HTTP_200_OK)
async def get_all_employees():
    """
    Retrieve all employees.
    
    Returns:
        List[Employee]: List of all employees
    """
    logger.info(f"Fetching all employees. Count: {len(employees_db)}")
    return employees_db

@app.get("/employee/{employee_id}", response_model=Employee, status_code=status.HTTP_200_OK)
async def get_employee(employee_id: int):
    """
    Retrieve a specific employee by ID.
    
    Args:
        employee_id: The ID of the employee to retrieve
        
    Returns:
        Employee: The requested employee
        
    Raises:
        HTTPException: If employee not found
    """
    logger.info(f"Fetching employee with ID: {employee_id}")
    
    for employee in employees_db:
        if employee.id == employee_id:
            return employee
    
    logger.warning(f"Employee not found: {employee_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Employee with ID {employee_id} not found"
    )

@app.post("/employee", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_data: EmployeeCreate):
    """
    Create a new employee.
    
    Args:
        employee_data: Employee data for creation
        
    Returns:
        Employee: The newly created employee
    """
    global next_employee_id
    
    logger.info(f"Creating new employee: {employee_data.name}")
    
    # Check if email already exists
    for existing_employee in employees_db:
        if existing_employee.email == employee_data.email:
            logger.warning(f"Duplicate email attempted: {employee_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with email {employee_data.email} already exists"
            )
    
    new_employee = Employee(
        id=next_employee_id,
        name=employee_data.name,
        email=employee_data.email,
        department=employee_data.department,
        position=employee_data.position,
        created_at=datetime.utcnow().isoformat()
    )
    
    employees_db.append(new_employee)
    next_employee_id += 1
    
    logger.info(f"Employee created successfully: ID {new_employee.id}")
    return new_employee

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 50)
    logger.info("AstraFlow Employee Service Starting")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'production')}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("AstraFlow Employee Service Shutting Down")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        log_level=LOG_LEVEL.lower()
    )
