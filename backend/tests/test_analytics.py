def test_progress_requires_auth(client, sample_exercise):
    response = client.get(f"/api/v1/analytics/progress/{sample_exercise['id']}")
    assert response.status_code == 401


def test_progress_exercise_not_found(client, auth_headers):
    response = client.get("/api/v1/analytics/progress/9999", headers=auth_headers)
    assert response.status_code == 404


def test_progress_no_sets_yet(client, auth_headers, sample_exercise):
    response = client.get(
        f"/api/v1/analytics/progress/{sample_exercise['id']}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exercise_id"] == sample_exercise["id"]
    assert data["exercise_name"] == sample_exercise["name"]
    assert data["history"] == []
    assert data["personal_best_weight"] == 0.0


def test_progress_computes_history_and_personal_best(client, auth_headers, sample_exercise):
    # Session 1 (earlier date): two sets, max weight 100
    s1 = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-01"}, headers=auth_headers
    ).json()
    client.post(
        f"/api/v1/workout-sets/{s1['id']}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 95.0, "reps": 5},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/workout-sets/{s1['id']}",
        json={"exercise_id": sample_exercise["id"], "set_number": 2, "weight": 100.0, "reps": 5},
        headers=auth_headers,
    )

    # Session 2 (later date): one set, a new PB
    s2 = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-08"}, headers=auth_headers
    ).json()
    client.post(
        f"/api/v1/workout-sets/{s2['id']}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 105.0, "reps": 3},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/analytics/progress/{sample_exercise['id']}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["personal_best_weight"] == 105.0
    assert len(data["history"]) == 2

    # history is ordered by session date ascending
    first, second = data["history"]
    assert first["session_id"] == s1["id"]
    assert first["max_weight"] == 100.0
    assert first["total_volume"] == 95.0 * 5 + 100.0 * 5
    assert first["total_sets"] == 2

    assert second["session_id"] == s2["id"]
    assert second["max_weight"] == 105.0
    assert second["total_volume"] == 105.0 * 3
    assert second["total_sets"] == 1


def test_progress_scoped_to_current_user(client, auth_headers, other_user_headers, sample_exercise):
    """Another user's sets for the same shared-catalog exercise must not
    leak into this user's progress or personal best."""
    other_session = client.post(
        "/api/v1/sessions/", json={"date": "2026-07-01"}, headers=other_user_headers
    ).json()
    client.post(
        f"/api/v1/workout-sets/{other_session['id']}",
        json={"exercise_id": sample_exercise["id"], "set_number": 1, "weight": 200.0, "reps": 1},
        headers=other_user_headers,
    )

    response = client.get(
        f"/api/v1/analytics/progress/{sample_exercise['id']}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["history"] == []
    assert data["personal_best_weight"] == 0.0