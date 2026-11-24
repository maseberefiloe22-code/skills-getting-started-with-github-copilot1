import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_activity():
    name = "Test Activity"
    original = activities.get(name)
    activity = {
        "description": "Activity for API tests",
        "schedule": "Fridays",
        "max_participants": 10,
        "participants": [],
    }
    activities[name] = activity

    yield name, activity

    if original is None:
        del activities[name]
    else:
        activities[name] = original


def test_get_activities_returns_current_data_without_caching(client, test_activity):
    activity_name, _ = test_activity

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert activity_name in response.json()


def test_student_can_sign_up_for_activity(client, test_activity):
    activity_name, activity = test_activity
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activity["participants"]


def test_student_cannot_sign_up_twice_for_activity(client, test_activity):
    activity_name, activity = test_activity
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    first_response = client.post(url, params={"email": email})
    duplicate_response = client.post(url, params={"email": email})

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert activity["participants"].count(email) == 1


def test_sign_up_for_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_participant_can_be_removed_from_activity(client, test_activity):
    activity_name, activity = test_activity
    email = "student@mergington.edu"
    activity["participants"].append(email)

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activity["participants"]


def test_removing_unregistered_participant_returns_not_found(client, test_activity):
    activity_name, _ = test_activity

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_removing_participant_from_unknown_activity_returns_not_found(client):
    response = client.delete(
        "/activities/Unknown Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
