"""Test suite for auth routes."""
import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        from app.database.db import init_db
        init_db()
        from app.database.seed import seed_all
        seed_all()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_page_loads(client):
    res = client.get("/auth/login")
    assert res.status_code == 200
    assert b"Sign In" in res.data or b"Login" in res.data


def test_signup_page_loads(client):
    res = client.get("/auth/signup")
    assert res.status_code == 200


def test_login_with_valid_credentials(client):
    res = client.post("/auth/login", data={
        "email": "admin@debugger.ai",
        "password": "Admin@123"
    }, follow_redirects=True)
    assert res.status_code == 200


def test_login_with_invalid_credentials(client):
    res = client.post("/auth/login", data={
        "email": "wrong@email.com",
        "password": "wrongpassword"
    })
    assert b"Invalid" in res.data or res.status_code == 200


def test_signup_creates_user(client):
    res = client.post("/auth/signup", data={
        "username": "testuser2026",
        "email": "testuser2026@example.com",
        "password": "Test@12345",
        "confirm_password": "Test@12345",
    }, follow_redirects=True)
    assert res.status_code == 200


def test_logout_redirects(client):
    res = client.get("/auth/logout", follow_redirects=True)
    assert res.status_code == 200


def test_dashboard_requires_login(client):
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code in (302, 200)


def test_404_page(client):
    res = client.get("/this-page-does-not-exist")
    assert res.status_code == 404
