def test_create_workout_set_requires_auth(client, sample_exercise):
    response = client.post(
        "/api/v1/workout-sets/9999",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 100.0, "reps": 5},
    )
    assert response.status_code == 401


def test_create_workout_set(client, auth_headers, sample_exercise):
    session_id = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    ).json()["id"]

    response = client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 100.0, "reps": 5, "rpe": 8},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exercise_id"] == sample_exercise["id"]
    assert data["set_number"] == 1
    assert data["weight"] == 100.0
    assert data["reps"] == 5
    assert data["rpe"] == 8
    assert "id" in data


def test_create_workout_set_without_rpe(client, auth_headers, sample_exercise):
    """rpe is optional on the model."""
    session_id = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    ).json()["id"]

    response = client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 100.0, "reps": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["rpe"] is None


def test_create_workout_set_session_not_found(client, auth_headers, sample_exercise):
    response = client.post(
        "/api/v1/workout-sets/9999",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 100.0, "reps": 5},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_workout_set_wrong_owner_returns_404(
    client, auth_headers, other_user_headers, sample_exercise
):
    session_id = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    ).json()["id"]

    response = client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 100.0, "reps": 5},
        headers=other_user_headers,
    )
    assert response.status_code == 404


def test_list_workout_sets_requires_auth(client):
    response = client.get("/api/v1/workout-sets/9999")
    assert response.status_code == 401


def test_list_workout_sets(client, auth_headers, sample_exercise):
    session_id = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    ).json()["id"]

    client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 100.0, "reps": 5},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={"exercise_id": sample_exercise["id"], "set_number": 2, "weight": 102.5, "reps": 5},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/workout-sets/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {s["set_number"] for s in data} == {1, 2}


def test_list_workout_sets_session_not_found(client, auth_headers):
    response = client.get("/api/v1/workout-sets/9999", headers=auth_headers)
    assert response.status_code == 404


def test_list_workout_sets_wrong_owner_returns_404(client, auth_headers, other_user_headers):
    session_id = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    ).json()["id"]

    response = client.get(f"/api/v1/workout-sets/{session_id}", headers=other_user_headers)
    assert response.status_code == 404