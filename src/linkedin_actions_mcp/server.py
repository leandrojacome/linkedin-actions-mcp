from fastmcp import FastMCP

from .applicant import LinkedInApplicant
from .config import Settings
from .models import ApplicationRequest, PostRequest, Visibility
from .publisher import LinkedInPublisher

mcp = FastMCP("CodeSpec LinkedIn Actions")
settings = Settings()


@mcp.tool()
async def publish_linkedin_post(
    text: str,
    image_path: str | None = None,
    image_alt_text: str | None = None,
    visibility: Visibility = Visibility.PUBLIC,
    confirmed: bool = False,
) -> dict[str, str | bool]:
    """Cria uma prévia ou publica texto e imagem no LinkedIn pela API oficial."""
    return await LinkedInPublisher(settings).publish(
        PostRequest(
            text=text,
            image_path=image_path,
            image_alt_text=image_alt_text,
            visibility=visibility,
            confirmed=confirmed,
        )
    )


@mcp.tool()
async def apply_to_linkedin_job(
    job_url: str,
    resume_path: str | None = None,
    answers: dict[str, str | bool | int | float] | None = None,
    confirmed: bool = False,
) -> dict[str, object]:
    """Abre uma vaga, anexa o currículo e envia somente quando o formulário estiver completo."""
    request = ApplicationRequest(
        job_url=job_url,
        resume_path=resume_path,
        answers=answers or {},
        confirmed=confirmed,
    )
    return await LinkedInApplicant(settings).apply(request)


def main() -> None:
    if settings.transport == "http":
        mcp.run(transport="http", host=settings.host, port=settings.port)
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
