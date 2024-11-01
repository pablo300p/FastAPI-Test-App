from fastapi.testclient import TestClient
from app.main import app
from app import schemas

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.json().get('message') == "Welcome to my API"
    assert res.status_code == 200


def test_create_user():
    res = client.post("/users", json = {"email" : "User5@gmail.com","password": "password124"})
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "User5@gmail.com"
    assert res.status_code == 201


def test_login_user():
    res = client.post("/login", data = {"username" : "User5@gmail.com","password": "password124"})
    assert res.status_code == 200