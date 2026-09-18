from alembic.migration import MigrationContext
from sqlalchemy import inspect

from app.database import engine


def test_database_is_at_latest_revision() -> None:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        assert context.get_current_revision() == "20260918_0001"


def test_migration_created_every_application_table() -> None:
    tables = set(inspect(engine).get_table_names())
    assert {
        "users",
        "applications",
        "activities",
        "documents",
        "ai_analyses",
        "application_kits",
        "alembic_version",
    }.issubset(tables)
