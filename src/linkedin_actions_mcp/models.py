from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Visibility(StrEnum):
    PUBLIC = "PUBLIC"
    CONNECTIONS = "CONNECTIONS"


class PostRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    image_path: Path | None = None
    image_alt_text: str | None = Field(default=None, max_length=4086)
    visibility: Visibility = Visibility.PUBLIC
    confirmed: bool = False

    @field_validator("image_path")
    @classmethod
    def validate_image(cls, value: Path | None) -> Path | None:
        if value is None:
            return None
        resolved = value.expanduser().resolve()
        if not resolved.is_file():
            raise ValueError("A imagem informada não existe")
        if resolved.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif"}:
            raise ValueError("A imagem precisa estar em JPG, PNG ou GIF")
        return resolved


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


class ServiceProposalRequest(BaseModel):
    request_url: HttpUrl
    message: str = Field(min_length=20, max_length=2000)
    estimated_hours_min: int = Field(ge=1, le=2000)
    estimated_hours_max: int = Field(ge=1, le=2000)
    confirmed: bool = False

    @field_validator("request_url")
    @classmethod
    def validate_request_url(cls, value: HttpUrl) -> HttpUrl:
        host = (value.host or "").lower()
        if host not in {"linkedin.com", "www.linkedin.com"}:
            raise ValueError("A URL precisa pertencer ao domínio linkedin.com")
        if "/services/" not in value.path:
            raise ValueError("A URL precisa apontar para uma solicitação de serviços")
        return value

    @field_validator("estimated_hours_max")
    @classmethod
    def validate_hours(cls, value: int, info) -> int:
        minimum = info.data.get("estimated_hours_min")
        if minimum is not None and value < minimum:
            raise ValueError("A estimativa máxima não pode ser menor que a mínima")
        return value
