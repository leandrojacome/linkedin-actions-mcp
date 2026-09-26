from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Visibility(StrEnum):
    PUBLIC = "PUBLIC"
    CONNECTIONS = "CONNECTIONS"


class PostRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    visibility: Visibility = Visibility.PUBLIC
    confirmed: bool = False


class ApplicationRequest(BaseModel):
    job_url: HttpUrl
    resume_path: Path | None = None
    answers: dict[str, str | bool | int | float] = Field(default_factory=dict)
    confirmed: bool = False

    @field_validator("job_url")
    @classmethod
    def validate_linkedin_job(cls, value: HttpUrl) -> HttpUrl:
        host = (value.host or "").lower()
        if host not in {"linkedin.com", "www.linkedin.com"}:
            raise ValueError("A URL precisa pertencer ao domínio linkedin.com")
        if "/jobs/" not in value.path:
            raise ValueError("A URL precisa apontar para uma vaga do LinkedIn")
        return value

    @field_validator("resume_path")
    @classmethod
    def validate_resume(cls, value: Path | None) -> Path | None:
        if value is None:
            return None
        resolved = value.expanduser().resolve()
        if not resolved.is_file():
            raise ValueError("O currículo informado não existe")
        if resolved.suffix.lower() != ".pdf":
            raise ValueError("O currículo precisa estar em PDF")
        return resolved
