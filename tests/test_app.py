import os

# ---------------------------------------------------------
# Test database
# ---------------------------------------------------------

os.environ["DATABASE_PATH"] = (
    "/tmp/pocketsmart_test.db"
)

os.environ["SECRET_KEY"] = (
    "test-secret-key"
)


from fastapi.testclient import TestClient

from app.main import app

from app.db import init_db


# Initialize database
init_db()


client = TestClient(
    app
)


# =========================================================
# Health
# =========================================================

def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


# =========================================================
# Register
# =========================================================

def test_register():

    username = (
        "testuser_unique"
    )

    email = (
        "testuser_unique@example.com"
    )

    response = client.post(
        "/register",
        json={
            "username":
                username,

            "email":
                email,

            "full_name":
                "Test User",

            "password":
                "secret123"
        }
    )

    assert response.status_code in (
        200,
        409
    )


# =========================================================
# Login
# =========================================================

def test_login():

    username = (
        "testlogin_unique"
    )

    email = (
        "testlogin_unique@example.com"
    )

    register_response = client.post(
        "/register",
        json={
            "username":
                username,

            "email":
                email,

            "full_name":
                "Login User",

            "password":
                "secret123"
        }
    )

    assert register_response.status_code in (
        200,
        409
    )


    login_response = client.post(
        "/token",
        data={
            "username":
                username,

            "password":
                "secret123"
        }
    )

    assert login_response.status_code == 200


# =========================================================
# Home planner
# =========================================================

def test_home_planner():

    username = (
        "homeplanner_unique"
    )

    email = (
        "homeplanner_unique@example.com"
    )

    client.post(
        "/register",
        json={
            "username":
                username,

            "email":
                email,

            "password":
                "secret123"
        }
    )


    login = client.post(
        "/token",
        data={
            "username":
                username,

            "password":
                "secret123"
        }
    )

    assert login.status_code == 200


    response = client.post(
        "/api/home-budget",
        json={
            "total_budget":
                50000,

            "num_lights":
                4,

            "num_fans":
                2,

            "num_furniture":
                2,

            "num_dining_tables":
                1,

            "has_living_room":
                True,

            "has_kitchen":
                True,

            "has_bedroom":
                True,

            "additional_requirements":
                "Modern design"
        }
    )


    assert response.status_code == 200

    data = response.json()

    assert (
        data["total_budget"]
        == 50000
    )

    assert "budget_breakdown" in data

    assert "remaining_budget" in data