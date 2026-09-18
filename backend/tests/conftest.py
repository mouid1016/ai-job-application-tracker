import os
from pathlib import Path
import tempfile
from collections.abc import Callable, Generator

from alembic import command
from alembic.config import Config
import pytest
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = Path(tempfile.mkdtemp(prefix="job-tracker-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["OPENAI_API_KEY"] = ""
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-thirty-two-bytes"

alembic_config = Config(str(BACKEND_ROOT / "alembic.ini"))
alembic_config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
command.upgrade(alembic_config, "head")

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def register(client: TestClient) -> Callable[[str, str], dict[str, str]]:
    def register_user(name: str, email: str) -> dict[str, str]:
        response = client.post(
            "/api/auth/register",
            json={"name": name, "email": email, "password": "securepass123"},
        )
        assert response.status_code == 201
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return register_user


@pytest.fixture()
def create_application(client: TestClient) -> Callable[[dict[str, str], dict[str, object] | None], dict[str, object]]:
    def create(headers: dict[str, str], overrides: dict[str, object] | None = None) -> dict[str, object]:
        payload: dict[str, object] = {
            "company": "Example Labs",
            "role": "Software Engineer Intern",
            "status": "saved",
            "job_description": "Build REST APIs with Python, FastAPI, PostgreSQL, Docker and teamwork.",
        }
        payload.update(overrides or {})
        response = client.post("/api/applications", headers=headers, json=payload)
        assert response.status_code == 201
        return response.json()

    return create
