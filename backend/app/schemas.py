from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from .models import ApplicationStatus


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    status: ApplicationStatus = ApplicationStatus.saved
    salary: str | None = Field(default=None, max_length=100)
    job_url: HttpUrl | None = None
    deadline: date | None = None
    notes: str | None = None
    job_description: str | None = None
    match_score: int | None = Field(default=None, ge=0, le=100)

    @field_validator("company", "role")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    role: str | None = Field(default=None, min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    status: ApplicationStatus | None = None
    salary: str | None = Field(default=None, max_length=100)
    job_url: HttpUrl | None = None
    deadline: date | None = None
    notes: str | None = None
    job_description: str | None = None
    match_score: int | None = Field(default=None, ge=0, le=100)


class ApplicationRead(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatsRead(BaseModel):
    total: int
    active: int
    interviews: int
    offers: int
    response_rate: float


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalise_login_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class ActivityRead(BaseModel):
    id: int
    application_id: int
    event_type: str
    description: str
    old_value: str | None
    new_value: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentRead(BaseModel):
    id: int
    application_id: int
    original_filename: str
    content_type: str
    size_bytes: int
    extracted_characters: int
    extraction_status: str
    uploaded_at: datetime

    @classmethod
    def from_document(cls, document: object) -> "DocumentRead":
        return cls(
            id=document.id,
            application_id=document.application_id,
            original_filename=document.original_filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            extracted_characters=len(document.extracted_text),
            extraction_status=document.extraction_status,
            uploaded_at=document.uploaded_at,
        )


class AIAnalysisRead(BaseModel):
    id: int
    application_id: int
    match_score: int
    skill_coverage: int
    matching_skills: list[str]
    missing_skills: list[str]
    cv_skills: list[str]
    job_skills: list[str]
    strengths: list[str]
    recommendations: list[str]
    summary: str
    provider: str
    model: str | None
    is_stale: bool
    created_at: datetime
    updated_at: datetime


class InterviewQuestionRead(BaseModel):
    question: str
    why_asked: str
    answer_framework: str
    talking_points: list[str]


class ApplicationKitRead(BaseModel):
    id: int
    application_id: int
    cover_letter: str
    elevator_pitch: str
    interview_questions: list[InterviewQuestionRead]
    questions_to_ask: list[str]
    provider: str
    model: str | None
    is_stale: bool
    created_at: datetime
    updated_at: datetime
