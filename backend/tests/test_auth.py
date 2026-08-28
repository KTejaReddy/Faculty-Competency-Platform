"""Authentication tests."""
from __future__ import annotations

import uuid

from .conftest import faculty_token, register_faculty

PASSWORD = "secret1234"


def unique_name() -> str:
    return f"TEST FACULTY {uuid.uuid4().hex[:8].upper()}"


class TestRegistration:
    def test_register_returns_token_and_uppercases_name(self, client):
        name = unique_name()
        data = register_faculty(client, f"  {name.lower()}  ")
        assert data["user"]["full_name"] == name
        assert data["user"]["role"] == "faculty"
        assert data["access_token"]

    def test_name_normalization_collapses_spaces(self, client):
        data = register_faculty(client, f"j o h n   smith {uuid.uuid4().hex[:4]}")
        assert data["user"]["full_name"].startswith("J O H N SMITH")
        assert "  " not in data["user"]["full_name"]

    def test_duplicate_account_rejected(self, client):
        name = unique_name()
        register_faculty(client, name)
        r = client.post(
            "/api/auth/register",
            json={
                "full_name": f"  {name.lower()}  ",  # normalized form collides
                "department": "COMPUTER SCIENCE AND ENGINEERING",
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        assert r.status_code == 409

    def test_duplicate_name_across_departments_rejected(self, client):
        # Names are globally unique (login no longer uses department).
        name = unique_name()
        register_faculty(client, name)
        r = client.post(
            "/api/auth/register",
            json={
                "full_name": name,
                "department": "INFORMATION TECHNOLOGY",
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        assert r.status_code == 409

    def test_password_mismatch_rejected(self, client):
        r = client.post(
            "/api/auth/register",
            json={
                "full_name": unique_name(),
                "department": "COMPUTER SCIENCE AND ENGINEERING",
                "password": PASSWORD,
                "confirm_password": "different123",
            },
        )
        assert r.status_code == 400
        assert "do not match" in r.json()["detail"].lower()

    def test_short_password_rejected(self, client):
        r = client.post(
            "/api/auth/register",
            json={
                "full_name": unique_name(),
                "department": "COMPUTER SCIENCE AND ENGINEERING",
                "password": "short",
                "confirm_password": "short",
            },
        )
        assert r.status_code in (400, 422)  # rejected by schema or handler

    def test_invalid_department_rejected(self, client):
        r = client.post(
            "/api/auth/register",
            json={
                "full_name": unique_name(),
                "department": "NO SUCH DEPARTMENT",
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        assert r.status_code == 400
        assert "department" in r.json()["detail"].lower()

    def test_no_plaintext_password_stored(self, db):
        from sqlalchemy import select

        from app.models.models import User

        users = list(db.scalars(select(User)))
        for u in users:
            assert u.password_hash.startswith("$2")  # bcrypt
            assert PASSWORD not in u.password_hash


class TestLogin:
    def test_login_success(self, client):
        name = unique_name()
        register_faculty(client, name)
        token = faculty_token(client, name)
        assert token

    def test_invalid_password(self, client):
        name = unique_name()
        register_faculty(client, name)
        r = client.post(
            "/api/auth/login",
            json={"full_name": name, "password": "wrongpass1"},
        )
        assert r.status_code == 401

    def test_unknown_user(self, client):
        r = client.post(
            "/api/auth/login",
            json={"full_name": "NOBODY HERE", "password": "whatever1"},
        )
        assert r.status_code == 401

    def test_rate_limiting(self, client):
        name = unique_name()
        for _ in range(10):
            client.post(
                "/api/auth/login",
                json={"full_name": name, "password": "badpass12"},
            )
        r = client.post(
            "/api/auth/login",
            json={"full_name": name, "password": "badpass12"},
        )
        assert r.status_code == 429

    def test_admin_login(self, client):
        r = client.post("/api/auth/admin-login", json={"username": "ADMIN", "password": "admin123"})
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "admin"

    def test_admin_login_wrong_password(self, client):
        r = client.post("/api/auth/admin-login", json={"username": "ADMIN", "password": "nope"})
        assert r.status_code == 401

    def test_admin_can_login_via_faculty_login(self, client):
        # The shared login form accepts admin credentials too (department is gone).
        r = client.post("/api/auth/login", json={"full_name": "ADMIN", "password": "admin123"})
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "admin"


class TestTokens:
    def test_me_endpoint(self, client):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["full_name"] == name

    def test_invalid_token_rejected(self, client):
        r = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage.token.here"})
        assert r.status_code == 401
