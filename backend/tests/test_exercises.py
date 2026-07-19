"""Exercises are a shared catalog (not per-user), so none of these need auth
headers - see DATA MODEL notes in the project state doc."""


def test_create_exercise(client):
    response = client.post(
        "/api/v1/exercises/",
        json={"name": "Squat", "muscle_group": "Legs", "equipment": "Barbell"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Squat"
    assert data["muscle_group"] == "Legs"
    assert data["equipment"] == "Barbell"
    assert "id" in data


def test_create_exercise_optional_fields(client):
    """muscle_group and equipment are optional on the model."""
    response = client.post("/api/v1/exercises/", json={"name": "Farmer's Carry"})
    assert response.status_code == 200
    data = response.json()
    assert data["muscle_group"] is None
    assert data["equipment"] is None


def test_create_exercise_duplicate_name(client, sample_exercise):
    response = client.post(
        "/api/v1/exercises/",
        json={"name": sample_exercise["name"], "muscle_group": "Back"},
    )
    assert response.status_code == 400


def test_get_exercise(client, sample_exercise):
    response = client.get(f"/api/v1/exercises/{sample_exercise['id']}")
    assert response.status_code == 200
    assert response.json() == sample_exercise


def test_get_exercise_not_found(client):
    response = client.get("/api/v1/exercises/9999")
    assert response.status_code == 404


def test_list_exercises(client):
    client.post("/api/v1/exercises/", json={"name": "Deadlift"})
    client.post("/api/v1/exercises/", json={"name": "Overhead Press"})

    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    names = [e["name"] for e in response.json()]
    assert "Deadlift" in names
    assert "Overhead Press" in names


def test_list_exercises_pagination(client):
    for i in range(5):
        client.post("/api/v1/exercises/", json={"name": f"Exercise {i}"})

    response = client.get("/api/v1/exercises/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/api/v1/exercises/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2