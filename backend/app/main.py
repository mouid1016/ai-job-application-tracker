from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func, inspect, select, text, update
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .document_service import document_path, read_upload, remove_document, store_document
from .models import Activity, Application, ApplicationStatus, Document, User
from .schemas import (
    ActivityRead,
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    DocumentRead,
    LoginRequest,
    RegisterRequest,
    StatsRead,
    TokenRead,
    UserRead,
)
from .security import create_access_token, get_current_user, hash_password, verify_password


DEMO_EMAIL = "demo@applyflow.dev"
DEMO_PASSWORD = "demo1234"


def upgrade_v1_database() -> None:
    """Add ownership to databases created by the first project version."""
    inspector = inspect(engine)
    if "applications" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("applications")}
    if "user_id" in columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE applications "
                "ADD COLUMN user_id INTEGER REFERENCES users(id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_applications_user_id "
                "ON applications (user_id)"
            )
        )


def seed_database() -> None:
    if not settings.seed_demo_data:
        return

    with SessionLocal() as db:
        demo_user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if demo_user is None:
            demo_user = User(
                name="Demo User",
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
            )
            db.add(demo_user)
            db.flush()

        db.execute(
            update(Application)
            .where(Application.user_id.is_(None))
            .values(user_id=demo_user.id)
        )

        if db.scalar(select(func.count(Application.id))) == 0:
            today = date.today()
            db.add_all(
                [
                    Application(
                        user_id=demo_user.id,
                        company="OpenAI",
                        role="Software Engineer Intern",
                        location="San Francisco, CA",
                        status=ApplicationStatus.applied,
                        deadline=today + timedelta(days=9),
                        match_score=88,
                        notes="Follow up with the university recruiter next week.",
                    ),
                    Application(
                        user_id=demo_user.id,
                        company="Stripe",
                        role="Backend Engineering Intern",
                        location="London, UK",
                        status=ApplicationStatus.interview,
                        deadline=today + timedelta(days=4),
                        match_score=81,
                        notes="Technical interview focuses on APIs and data modelling.",
                    ),
                    Application(
                        user_id=demo_user.id,
                        company="Notion",
                        role="Product Engineer",
                        location="Remote",
                        status=ApplicationStatus.saved,
                        deadline=today + timedelta(days=16),
                        match_score=74,
                    ),
                    Application(
                        user_id=demo_user.id,
                        company="Vercel",
                        role="Frontend Developer Intern",
                        location="Remote",
                        status=ApplicationStatus.assessment,
                        match_score=92,
                    ),
                    Application(
                        user_id=demo_user.id,
                        company="Linear",
                        role="Full-stack Engineer",
                        location="Remote",
                        status=ApplicationStatus.offer,
                        match_score=86,
                    ),
                ]
            )
        db.commit()


def backfill_activity_history() -> None:
    """Give pre-existing applications a clear starting event."""
    with SessionLocal() as db:
        applications = db.scalars(
            select(Application).where(
                Application.id.not_in(select(Activity.application_id))
            )
        ).all()
        for application in applications:
            db.add(
                Activity(
                    application_id=application.id,
                    event_type="created",
                    description=f"Added {application.role} at {application.company}",
                    new_value=application.status.value,
                    created_at=application.created_at,
                )
            )
        db.commit()


def prepare_database() -> None:
    Base.metadata.create_all(bind=engine)
    upgrade_v1_database()
    seed_database()
    backfill_activity_history()


@asynccontextmanager
async def lifespan(_: FastAPI):
    prepare_database()
    yield


app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": settings.app_name, "docs": "/docs"}


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}


def token_for(user: User) -> TokenRead:
    return TokenRead(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


def application_payload(payload: ApplicationCreate | ApplicationUpdate, *, exclude_unset: bool = False) -> dict[str, object]:
    data = payload.model_dump(exclude_unset=exclude_unset, mode="python")
    if data.get("job_url") is not None:
        data["job_url"] = str(data["job_url"])
    return data


@app.post("/api/auth/register", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenRead:
    existing = db.scalar(select(User).where(func.lower(User.email) == payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return token_for(user)


@app.post("/api/auth/login", response_model=TokenRead)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenRead:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return token_for(user)


@app.get("/api/auth/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.get("/api/applications", response_model=list[ApplicationRead])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Application]:
    statement = (
        select(Application)
        .where(Application.user_id == current_user.id)
        .order_by(Application.updated_at.desc())
    )
    return list(db.scalars(statement).all())


@app.post(
    "/api/applications",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    application = Application(
        **application_payload(payload),
        user_id=current_user.id,
    )
    db.add(application)
    db.flush()
    db.add(
        Activity(
            application_id=application.id,
            event_type="created",
            description=f"Added {application.role} at {application.company}",
            new_value=application.status.value,
        )
    )
    db.commit()
    db.refresh(application)
    return application


def find_application(application_id: int, user_id: int, db: Session) -> Application:
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def serialise_activity_value(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, ApplicationStatus):
        return value.value
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[union-attr]
    return str(value)


def describe_field_changes(changes: list[tuple[str, str | None, str | None]]) -> str:
    labels = {
        "company": "company",
        "role": "role",
        "location": "location",
        "salary": "salary",
        "job_url": "job URL",
        "deadline": "deadline",
        "notes": "notes",
        "job_description": "job description",
        "match_score": "match score",
    }
    if len(changes) == 1:
        field, old_value, new_value = changes[0]
        if field == "deadline":
            return f"Changed deadline from {old_value or 'not set'} to {new_value or 'not set'}"
        if field == "notes":
            return "Updated personal notes"
        if field == "job_description":
            return "Updated the job description"
        return f"Updated {labels.get(field, field.replace('_', ' '))}"
    changed_labels = ", ".join(labels.get(field, field.replace("_", " ")) for field, _, _ in changes)
    return f"Updated application details: {changed_labels}"


@app.get("/api/applications/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    return find_application(application_id, current_user.id, db)


@app.patch("/api/applications/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    application = find_application(application_id, current_user.id, db)
    field_changes: list[tuple[str, str | None, str | None]] = []
    status_change: tuple[str | None, str | None] | None = None
    for field, value in application_payload(payload, exclude_unset=True).items():
        old_value = serialise_activity_value(getattr(application, field))
        new_value = serialise_activity_value(value)
        if old_value == new_value:
            continue
        if field == "status":
            status_change = (old_value, new_value)
        else:
            field_changes.append((field, old_value, new_value))
        setattr(application, field, value)

    if status_change is not None:
        old_status, new_status = status_change
        old_label = (old_status or "unknown").replace("_", " ").title()
        new_label = (new_status or "unknown").replace("_", " ").title()
        db.add(
            Activity(
                application_id=application.id,
                event_type="status_changed",
                description=f"Moved from {old_label} to {new_label}",
                old_value=old_status,
                new_value=new_status,
            )
        )
    if field_changes:
        db.add(
            Activity(
                application_id=application.id,
                event_type="details_updated",
                description=describe_field_changes(field_changes),
                old_value=" | ".join(value or "" for _, value, _ in field_changes),
                new_value=" | ".join(value or "" for _, _, value in field_changes),
            )
        )
    db.commit()
    db.refresh(application)
    return application


@app.get("/api/applications/{application_id}/activities", response_model=list[ActivityRead])
def list_activities(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Activity]:
    application = find_application(application_id, current_user.id, db)
    statement = (
        select(Activity)
        .where(Activity.application_id == application.id)
        .order_by(Activity.created_at.desc(), Activity.id.desc())
    )
    return list(db.scalars(statement).all())


def find_cv(application_id: int, user_id: int, db: Session) -> Document | None:
    return db.scalar(
        select(Document).where(
            Document.application_id == application_id,
            Document.user_id == user_id,
        )
    )


@app.get("/api/applications/{application_id}/documents/cv", response_model=DocumentRead | None)
def get_cv(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead | None:
    find_application(application_id, current_user.id, db)
    document = find_cv(application_id, current_user.id, db)
    return DocumentRead.from_document(document) if document else None


@app.post(
    "/api/applications/{application_id}/documents/cv",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_cv(
    application_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    application = find_application(application_id, current_user.id, db)
    original_filename, content_type, content, extracted_text = await read_upload(file)
    stored_filename = store_document(content, content_type)
    previous = find_cv(application_id, current_user.id, db)

    try:
        if previous is not None:
            previous_stored_filename = previous.stored_filename
            previous_original_filename = previous.original_filename
            db.delete(previous)
            db.flush()
        else:
            previous_stored_filename = None
            previous_original_filename = None

        document = Document(
            application_id=application.id,
            user_id=current_user.id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=content_type,
            size_bytes=len(content),
            extracted_text=extracted_text,
            extraction_status="complete",
        )
        db.add(document)
        db.flush()
        db.add(
            Activity(
                application_id=application.id,
                event_type="cv_replaced" if previous_original_filename else "cv_uploaded",
                description=(
                    f"Replaced {previous_original_filename} with {original_filename}"
                    if previous_original_filename
                    else f"Uploaded CV: {original_filename}"
                ),
                old_value=previous_original_filename,
                new_value=original_filename,
            )
        )
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        remove_document(stored_filename)
        raise

    if previous_stored_filename:
        remove_document(previous_stored_filename)
    return DocumentRead.from_document(document)


@app.get("/api/applications/{application_id}/documents/cv/download")
def download_cv(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    find_application(application_id, current_user.id, db)
    document = find_cv(application_id, current_user.id, db)
    if document is None:
        raise HTTPException(status_code=404, detail="CV not found")
    return FileResponse(
        document_path(document.stored_filename),
        media_type=document.content_type,
        filename=document.original_filename,
    )


@app.delete("/api/applications/{application_id}/documents/cv", status_code=status.HTTP_204_NO_CONTENT)
def delete_cv(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    application = find_application(application_id, current_user.id, db)
    document = find_cv(application_id, current_user.id, db)
    if document is None:
        raise HTTPException(status_code=404, detail="CV not found")
    stored_filename = document.stored_filename
    original_filename = document.original_filename
    db.delete(document)
    db.add(
        Activity(
            application_id=application.id,
            event_type="cv_removed",
            description=f"Removed CV: {original_filename}",
            old_value=original_filename,
        )
    )
    db.commit()
    remove_document(stored_filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/api/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    application = find_application(application_id, current_user.id, db)
    cv = find_cv(application.id, current_user.id, db)
    stored_filename = cv.stored_filename if cv else None
    db.delete(application)
    db.commit()
    if stored_filename:
        remove_document(stored_filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stats", response_model=StatsRead)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsRead:
    counts = dict(
        db.execute(
            select(Application.status, func.count(Application.id))
            .where(Application.user_id == current_user.id)
            .group_by(Application.status)
        ).all()
    )
    total = sum(counts.values())
    rejected = counts.get(ApplicationStatus.rejected, 0)
    offers = counts.get(ApplicationStatus.offer, 0)
    interviews = counts.get(ApplicationStatus.interview, 0)
    responses = interviews + offers + rejected
    return StatsRead(
        total=total,
        active=total - offers - rejected,
        interviews=interviews,
        offers=offers,
        response_rate=round((responses / total * 100) if total else 0, 1),
    )
