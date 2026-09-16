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
