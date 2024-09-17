from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_list_books():
    response = client.get("/books")
    assert response.status_code == 200

def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []
    