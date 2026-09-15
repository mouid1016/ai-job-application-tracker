from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, inspect, select, text, update
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import Application, ApplicationStatus, User
from .schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
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


def prepare_database() -> None:
    Base.metadata.create_all(bind=engine)
    upgrade_v1_database()
    seed_database()


@asynccontextmanager
async def lifespan(_: FastAPI):
    prepare_database()
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
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
        **payload.model_dump(mode="json"),
        user_id=current_user.id,
    )
    db.add(application)
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
    for field, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@app.delete("/api/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    application = find_application(application_id, current_user.id, db)
    db.delete(application)
    db.commit()
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
