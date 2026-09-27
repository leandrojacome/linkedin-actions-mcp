from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LINKEDIN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    access_token: SecretStr | None = None
    author_urn: str | None = None
    browser_profile_dir: Path = Path.home() / ".config" / "linkedin-actions-mcp" / "browser"
    service_requests_url: str = "https://www.linkedin.com/services/page/admin/requests/"
    headless: bool = False
    request_timeout_seconds: float = 30.0
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8787
