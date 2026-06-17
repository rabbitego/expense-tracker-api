import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_auth_header():
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    })
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Expense Tracker API" in response.json()["message"]


def test_register_user():
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_login():
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123",
    })
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_expense():
    headers = get_auth_header()
    response = client.post("/expenses/", json={
        "amount": 25.50,
        "category": "Food",
        "description": "Lunch at cafe",
    }, headers=headers)
    assert response.status_code == 201
    assert response.json()["amount"] == 25.50


def test_get_expenses():
    headers = get_auth_header()
    client.post("/expenses/", json={"amount": 10, "category": "Food"}, headers=headers)
    client.post("/expenses/", json={"amount": 50, "category": "Transport"}, headers=headers)

    response = client.get("/expenses/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_expenses_by_category():
    headers = get_auth_header()
    client.post("/expenses/", json={"amount": 10, "category": "Food"}, headers=headers)
    client.post("/expenses/", json={"amount": 50, "category": "Transport"}, headers=headers)

    response = client.get("/expenses/?category=Food", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_stats():
    headers = get_auth_header()
    client.post("/expenses/", json={"amount": 100, "category": "Food"}, headers=headers)
    client.post("/expenses/", json={"amount": 200, "category": "Food"}, headers=headers)
    client.post("/expenses/", json={"amount": 50, "category": "Transport"}, headers=headers)

    response = client.get("/expenses/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_spent"] == 350.0
    assert data["top_category"] == "Food"


def test_delete_expense():
    headers = get_auth_header()
    create_resp = client.post("/expenses/", json={
        "amount": 30, "category": "Shopping"
    }, headers=headers)
    expense_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/expenses/{expense_id}", headers=headers)
    assert delete_resp.status_code == 204
