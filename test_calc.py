import pytest
from fastapi.testclient import TestClient
from calc import app, Item, CreateItem

client = TestClient(app)

# Fixture for setting up database
@pytest.fixture
def setup_db():
    db = {}
    for i in range(1, 6):
        item = Item(id=i, name=f'Item {i}', price=float(i))
        db[i] = item.dict()
    return db

 
# Test for health_check
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Service running"}


# Test for list_items
def test_list_items(setup_db):
    app.dependency_overrides[setup_db]
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()['items']) == 5  # As we added 5 items in setup_db fixture


# Test for get_item
def test_get_item(setup_db):
    app.dependency_overrides[setup_db]
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['name'] == 'Item 1'
    assert response.json()['price'] == 1.0


# Test for get_item when item does not exist
def test_get_item_not_found(setup_db):
    app.dependency_overrides[setup_db]
    response = client.get("/items/10")
    assert response.status_code == 404
    assert response.json()['detail'] == "Item not found"


# Test for create_item
def test_create_item(setup_db):
    app.dependency_overrides[setup_db]
    item = CreateItem(name='New Item', price=10.0)
    response = client.post("/items", json=item.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'Item created'
    assert response.json()['item']['id'] == 6  # As we added 5 items in setup_db fixture
    assert response.json()['item']['name'] == 'New Item'
    assert response.json()['item']['price'] == 10.0


# Test for delete_item
def test_delete_item(setup_db):
    app.dependency_overrides[setup_db]
    response = client.delete("/items/1")
    assert response.status_code == 200
    assert response.json()['message'] == 'Item deleted'
    assert response.json()['deleted_item']['id'] == 1
    assert response.json()['deleted_item']['name'] == 'Item 1'
    assert response.json()['deleted_item']['price'] == 1.0


# Test for delete_item when item does not exist
def test_delete_item_not_found(setup_db):
    app.dependency_overrides[setup_db]
    response = client.delete("/items/10")
    assert response.status_code == 404
    assert response.json()['detail'] == "Cannot delete. Item not found"