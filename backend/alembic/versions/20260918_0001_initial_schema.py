"""Create the initial job tracker schema.

Revision ID: 20260918_0001
Revises:
Create Date: 2026-09-18
"""

from collections.abc import Callable

from alembic import op
import sqlalchemy as sa


revision = "20260918_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    def create(name: str, operation: Callable[[], None]) -> None:
        if name not in existing:
            operation()
            existing.add(name)

    create("users", _create_users)
    create("applications", _create_applications)
    create("activities", _create_activities)
    create("documents", _create_documents)
    create("ai_analyses", _create_ai_analyses)
    create("application_kits", _create_application_kits)

    if "user_id" not in {column["name"] for column in sa.inspect(bind).get_columns("applications")}:
        with op.batch_alter_table("applications") as batch_op:
            batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key("fk_applications_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
            batch_op.create_index("ix_applications_user_id", ["user_id"])


def _create_users() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def _create_applications() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company", sa.String(120), nullable=False),
        sa.Column("role", sa.String(160), nullable=False),
        sa.Column("location", sa.String(160)),
        sa.Column("status", sa.Enum("saved", "applied", "assessment", "interview", "offer", "rejected", name="applicationstatus", native_enum=False), nullable=False),
        sa.Column("salary", sa.String(100)),
        sa.Column("job_url", sa.String(500)),
        sa.Column("deadline", sa.Date()),
        sa.Column("notes", sa.Text()),
        sa.Column("job_description", sa.Text()),
        sa.Column("match_score", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ("id", "user_id", "company", "role", "status"):
        op.create_index(f"ix_applications_{column}", "applications", [column])


def _create_activities() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("old_value", sa.Text()),
        sa.Column("new_value", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activities_id", "activities", ["id"])
    op.create_index("ix_activities_application_id", "activities", ["application_id"])
    op.create_index("ix_activities_created_at", "activities", ["created_at"])


def _create_documents() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False, unique=True),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("extraction_status", sa.String(40), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_id", "documents", ["id"])
    op.create_index("ix_documents_application_id", "documents", ["application_id"], unique=True)
    op.create_index("ix_documents_user_id", "documents", ["user_id"])


def _create_ai_analyses() -> None:
    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("match_score", sa.Integer(), nullable=False),
        sa.Column("skill_coverage", sa.Integer(), nullable=False),
        sa.Column("matching_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("cv_skills", sa.JSON(), nullable=False),
        sa.Column("job_skills", sa.JSON(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(120)),
        sa.Column("source_cv_uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_job_description_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_analyses_id", "ai_analyses", ["id"])
    op.create_index("ix_ai_analyses_application_id", "ai_analyses", ["application_id"], unique=True)
    op.create_index("ix_ai_analyses_user_id", "ai_analyses", ["user_id"])


def _create_application_kits() -> None:
    op.create_table(
        "application_kits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cover_letter", sa.Text(), nullable=False),
        sa.Column("elevator_pitch", sa.Text(), nullable=False),
        sa.Column("interview_questions", sa.JSON(), nullable=False),
        sa.Column("questions_to_ask", sa.JSON(), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(120)),
        sa.Column("source_analysis_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_cv_uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_job_description_hash", sa.String(64), nullable=False),
        sa.Column("source_company", sa.String(120), nullable=False),
        sa.Column("source_role", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_application_kits_id", "application_kits", ["id"])
    op.create_index("ix_application_kits_application_id", "application_kits", ["application_id"], unique=True)
    op.create_index("ix_application_kits_user_id", "application_kits", ["user_id"])


def downgrade() -> None:
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    for table in ("application_kits", "ai_analyses", "documents", "activities", "applications", "users"):
        if table in existing:
            op.drop_table(table)
