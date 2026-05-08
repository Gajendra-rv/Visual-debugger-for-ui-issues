"""Test suite for database models."""
import os, sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        from app.database.db import init_db
        init_db()
    yield app


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


def test_create_user(ctx):
    from app.models.user import User
    u = User.create("dbtest", "dbtest@example.com", "Password@123")
    assert u is not None
    assert u.username == "dbtest"
    assert u.email == "dbtest@example.com"


def test_user_password_check(ctx):
    from app.models.user import User
    User.create("passtest", "passtest@example.com", "Secret@456")
    u = User.get_by_email("passtest@example.com")
    assert u.check_password("Secret@456") is True
    assert u.check_password("WrongPassword") is False


def test_create_session(ctx):
    from app.models.user import User
    from app.models.test_session import TestSession
    u = User.create("sessuser", "sessuser@example.com", "Pass@789")
    sid = TestSession.create(u.id, "https://example.com", "Test Session")
    assert isinstance(sid, int)
    s = TestSession.get_by_id(sid)
    assert s is not None
    assert s["target_url"] == "https://example.com"


def test_dashboard_stats(ctx):
    from app.models.test_session import TestSession
    stats = TestSession.dashboard_stats()
    assert "total_sessions" in stats
    assert "bugs_found" in stats
    assert "avg_accuracy" in stats
