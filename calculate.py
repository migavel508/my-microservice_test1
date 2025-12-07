from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sample Microservice")

# -----------------------------
# Data Models
# -----------------------------
class Item(BaseModel):
    id: int
    name: str
    price: float

class CreateItem(BaseModel):
    name: str
    price: float

# -----------------------------
# In-memory database
# -----------------------------
db = {}


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service running"}

@app.get("/items")
def list_items():
    return {"items": list(db.values())}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]

@app.post("/items")
def create_item(item: CreateItem):
    new_id = len(db) + 1
    new_item = Item(id=new_id, name=item.name, price=item.price)
    db[new_id] = new_item.dict()
    return {"message": "Item created", "item": new_item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Cannot delete. Item not found")
    deleted = db.pop(item_id)
    return {"message": "Item deleted", "deleted_item": deleted}
