from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
    title="AstraFlow Product Service",
    description="Product management microservice",
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
class ProductBase(BaseModel):
    """Base product model"""
    name: str
    description: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    category: str
    stock_quantity: int = Field(ge=0, description="Stock quantity must be non-negative")

class ProductCreate(ProductBase):
    """Model for creating a product"""
    pass

class ProductUpdate(BaseModel):
    """Model for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)

class Product(ProductBase):
    """Complete product model with ID"""
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    service: str
    environment: str

# In-memory data store
products_db: List[Product] = [
    Product(
        id=1,
        name="Laptop Pro 15",
        description="High-performance laptop with 16GB RAM and 512GB SSD",
        price=1299.99,
        category="Electronics",
        stock_quantity=25,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    ),
    Product(
        id=2,
        name="Wireless Mouse",
        description="Ergonomic wireless mouse with 6 buttons",
        price=29.99,
        category="Accessories",
        stock_quantity=150,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    ),
    Product(
        id=3,
        name="USB-C Hub",
        description="7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader",
        price=49.99,
        category="Accessories",
        stock_quantity=80,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
]
next_product_id = 4

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
        service="product-service",
        environment=os.getenv("APP_ENV", "production")
    )

@app.get("/products", response_model=List[Product], status_code=status.HTTP_200_OK)
async def get_all_products(category: Optional[str] = None):
    """
    Retrieve all products, optionally filtered by category.
    
    Args:
        category: Optional category filter
        
    Returns:
        List[Product]: List of products
    """
    if category:
        logger.info(f"Fetching products for category: {category}")
        filtered_products = [p for p in products_db if p.category.lower() == category.lower()]
        return filtered_products
    
    logger.info(f"Fetching all products. Count: {len(products_db)}")
    return products_db

@app.get("/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def get_product(product_id: int):
    """
    Retrieve a specific product by ID.
    
    Args:
        product_id: The ID of the product to retrieve
        
    Returns:
        Product: The requested product
        
    Raises:
        HTTPException: If product not found
    """
    logger.info(f"Fetching product with ID: {product_id}")
    
    for product in products_db:
        if product.id == product_id:
            return product
    
    logger.warning(f"Product not found: {product_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with ID {product_id} not found"
    )

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate):
    """
    Create a new product.
    
    Args:
        product_data: Product data for creation
        
    Returns:
        Product: The newly created product
    """
    global next_product_id
    
    logger.info(f"Creating new product: {product_data.name}")
    
    # Check if product name already exists
    for existing_product in products_db:
        if existing_product.name.lower() == product_data.name.lower():
            logger.warning(f"Duplicate product name attempted: {product_data.name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with name '{product_data.name}' already exists"
            )
    
    new_product = Product(
        id=next_product_id,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock_quantity=product_data.stock_quantity,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    products_db.append(new_product)
    next_product_id += 1
    
    logger.info(f"Product created successfully: ID {new_product.id}")
    return new_product

@app.put("/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product_data: ProductUpdate):
    """
    Update an existing product.
    
    Args:
        product_id: The ID of the product to update
        product_data: Product data for update
        
    Returns:
        Product: The updated product
        
    Raises:
        HTTPException: If product not found
    """
    logger.info(f"Updating product with ID: {product_id}")
    
    for idx, product in enumerate(products_db):
        if product.id == product_id:
            # Update only provided fields
            update_data = product_data.dict(exclude_unset=True)
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update"
                )
            
            updated_product = product.copy(update={
                **update_data,
                "updated_at": datetime.utcnow().isoformat()
            })
            
            products_db[idx] = updated_product
            logger.info(f"Product updated successfully: ID {product_id}")
            return updated_product
    
    logger.warning(f"Product not found for update: {product_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with ID {product_id} not found"
    )

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    """
    Delete a product by ID.
    
    Args:
        product_id: The ID of the product to delete
        
    Raises:
        HTTPException: If product not found
    """
    logger.info(f"Deleting product with ID: {product_id}")
    
    for idx, product in enumerate(products_db):
        if product.id == product_id:
            products_db.pop(idx)
            logger.info(f"Product deleted successfully: ID {product_id}")
            return
    
    logger.warning(f"Product not found for deletion: {product_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with ID {product_id} not found"
    )

@app.get("/products/category/{category}", response_model=List[Product], status_code=status.HTTP_200_OK)
async def get_products_by_category(category: str):
    """
    Retrieve all products in a specific category.
    
    Args:
        category: The category to filter by
        
    Returns:
        List[Product]: List of products in the category
    """
    logger.info(f"Fetching products for category: {category}")
    filtered_products = [p for p in products_db if p.category.lower() == category.lower()]
    return filtered_products

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 50)
    logger.info("AstraFlow Product Service Starting")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'production')}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("AstraFlow Product Service Shutting Down")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8081,
        log_level=LOG_LEVEL.lower()
    )
