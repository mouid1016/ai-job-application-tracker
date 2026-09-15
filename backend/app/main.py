from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import Application, ApplicationStatus
from .schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate, StatsRead


def seed_database() -> None:
    if not settings.seed_demo_data:
        return

    with SessionLocal() as db:
        if db.scalar(select(func.count(Application.id))) != 0:
            return

        today = date.today()
        db.add_all(
            [
                Application(
                    company="OpenAI",
                    role="Software Engineer Intern",
                    location="San Francisco, CA",
                    status=ApplicationStatus.applied,
                    deadline=today + timedelta(days=9),
                    match_score=88,
                    notes="Follow up with the university recruiter next week.",
                ),
                Application(
                    company="Stripe",
                    role="Backend Engineering Intern",
                    location="London, UK",
                    status=ApplicationStatus.interview,
                    deadline=today + timedelta(days=4),
                    match_score=81,
                    notes="Technical interview focuses on APIs and data modelling.",
                ),
                Application(
                    company="Notion",
                    role="Product Engineer",
                    location="Remote",
                    status=ApplicationStatus.saved,
                    deadline=today + timedelta(days=16),
                    match_score=74,
                ),
                Application(
                    company="Vercel",
                    role="Frontend Developer Intern",
                    location="Remote",
                    status=ApplicationStatus.assessment,
                    match_score=92,
                ),
                Application(
                    company="Linear",
                    role="Full-stack Engineer",
                    location="Remote",
                    status=ApplicationStatus.offer,
                    match_score=86,
                ),
            ]
        )
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
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


@app.get("/api/applications", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db)) -> list[Application]:
    return list(db.scalars(select(Application).order_by(Application.updated_at.desc())).all())


@app.post(
    "/api/applications",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> Application:
    application = Application(**payload.model_dump(mode="json"))
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def find_application(application_id: int, db: Session) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.get("/api/applications/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)) -> Application:
    return find_application(application_id, db)


@app.patch("/api/applications/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
) -> Application:
    application = find_application(application_id, db)
    for field, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@app.delete("/api/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)) -> Response:
    application = find_application(application_id, db)
    db.delete(application)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stats", response_model=StatsRead)
def get_stats(db: Session = Depends(get_db)) -> StatsRead:
    counts = dict(
        db.execute(
            select(Application.status, func.count(Application.id)).group_by(Application.status)
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
