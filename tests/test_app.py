import sys
import pytest

# Ensure src is importable
sys.path.insert(0, "src")

from fastapi.testclient import TestClient

from app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # Known activity from seeded data
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity_name = "Chess Club"
    email = "pytest-user@example.com"

    # Ensure clean state: remove email if present
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Signup
    signup_resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Verify GET shows the new participant
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert email in data[activity_name]["participants"]

    # Unregister
    del_resp = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert del_resp.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # Verify GET no longer includes the email
    get_resp2 = client.get("/activities")
    assert get_resp2.status_code == 200
    data2 = get_resp2.json()
    assert email not in data2[activity_name]["participants"]
