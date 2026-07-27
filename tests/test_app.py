from fastapi.testclient import TestClient
from src.app import app, activities

# Keep an original copy to reset state between tests.
original_activities = {
    name: {
        "description": details["description"],
        "schedule": details["schedule"],
        "max_participants": details["max_participants"],
        "participants": list(details["participants"]),
    }
    for name, details in activities.items()
}

client = TestClient(app)


def setup_function():
    # Reset the in-memory activities state before each test.
    activities.clear()
    activities.update(
        {
            name: {
                "description": details["description"],
                "schedule": details["schedule"],
                "max_participants": details["max_participants"],
                "participants": list(details["participants"]),
            }
            for name, details in original_activities.items()
        }
    )


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    json_data = response.json()
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data
    assert "Gym Class" in json_data
    assert json_data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess Club/signup", params={"email": "new@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up new@mergington.edu for Chess Club"
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_email_returns_400():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_to_nonexistent_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_empty_email_returns_400():
    response = client.post("/activities/Chess Club/signup", params={"email": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email"
