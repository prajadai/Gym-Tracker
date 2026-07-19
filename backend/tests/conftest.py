import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

# Importing app.models registers every table on SQLModel.metadata before
# create_all() runs below - same reason app/models/__init__.py imports all
# four model modules. Using `from app import models` (not `import app.models`)
# so this doesn't rebind the `app` name above back to the package.
from app import models  # noqa: F401


@pytest.fixture(name="session")
def session_fixture():
    """Fresh in-memory SQLite DB per test. StaticPool keeps the single
    connection alive for the lifetime of the test (a plain in-memory engine
    would otherwise drop the DB between connections)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client: TestClient) -> dict:
    """Registers a user and returns their raw (pre-hash) credentials."""
    payload = {"email": "test@example.com", "password": "testpass123"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200, response.text
    return payload


@pytest.fixture
def auth_headers(client: TestClient, test_user: dict) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(client: TestClient) -> dict:
    """A second, independent user - for ownership/isolation tests."""
    payload = {"email": "other@example.com", "password": "otherpass123"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200, response.text

    login = client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_exercise(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/exercises/",
        json={"name": "Bench Press", "muscle_group": "Chest", "equipment": "Barbell"},
    )
    assert response.status_code == 200, response.text
    return response.json()