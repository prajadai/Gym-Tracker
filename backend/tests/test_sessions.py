def test_create_session_requires_auth(client):
    response = client.post("/api/v1/sessions/", json={"date": "2026-07-19"})
    assert response.status_code == 401


def test_create_session(client, auth_headers):
    response = client.post(
        "/api/v1/sessions/",
        json={"date": "2026-07-19", "notes": "Leg day"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-07-19"
    assert data["notes"] == "Leg day"
    assert "id" in data


def test_create_session_without_notes(client, auth_headers):
    """notes is optional on the model."""
    response = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["notes"] is None


def test_list_sessions_requires_auth(client):
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 401


def test_list_sessions_only_returns_own(client, auth_headers, other_user_headers):
    client.post("/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers)
    client.post("/api/v1/sessions/", json={"date": "2026-07-18"}, headers=other_user_headers)

    response = client.get("/api/v1/sessions/", headers=auth_headers)
    assert response.status_code == 200
    dates = [s["date"] for s in response.json()]
    assert dates == ["2026-07-19"]


def test_get_session_grouped_by_exercise(client, auth_headers, sample_exercise):
    session_resp = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={
            "exercise_id": sample_exercise["id"],
            "set_number": 1,
            "weight": 100.0,
            "reps": 5,
            "rpe": 8,
        },
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/workout-sets/{session_id}",
        json={
            "exercise_id": sample_exercise["id"],
            "set_number": 2,
            "weight": 105.0,
            "reps": 5,
        },
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/sessions/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_exercises"] == 1
    assert data["total_sets"] == 2
    assert data["exercises"][0]["exercise_id"] == sample_exercise["id"]
    assert data["exercises"][0]["exercise_name"] == sample_exercise["name"]
    assert len(data["exercises"][0]["sets"]) == 2


def test_get_session_not_found(client, auth_headers):
    response = client.get("/api/v1/sessions/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_session_wrong_owner_returns_404_not_403(client, auth_headers, other_user_headers):
    """Ownership checks return 404 (not 403) on non-owned resources, per the
    project's KEY DESIGN DECISIONS - this avoids leaking whether a given
    session id exists at all to a user who doesn't own it."""
    session_resp = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-19"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    response = client.get(f"/api/v1/sessions/{session_id}", headers=other_user_headers)
    assert response.status_code == 404