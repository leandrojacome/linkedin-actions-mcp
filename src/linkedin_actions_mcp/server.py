from fastmcp import FastMCP

from .applicant import LinkedInApplicant
from .config import Settings
from .models import ApplicationRequest, PostRequest, ServiceProposalRequest, Visibility
from .publisher import LinkedInPublisher
from .service_requests import LinkedInServiceRequests

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


@mcp.tool()
async def list_linkedin_service_requests(limit: int = 20) -> dict[str, object]:
    """Lista solicitações de serviços da sessão autenticada, sem alterar seu estado."""
    return await LinkedInServiceRequests(settings).list(limit=max(1, min(limit, 50)))


@mcp.tool()
async def read_linkedin_service_request(request_url: str) -> dict[str, object]:
    """Lê os detalhes de uma solicitação de serviços para análise e estimativa."""
    return await LinkedInServiceRequests(settings).read(request_url)


@mcp.tool()
async def submit_linkedin_service_proposal(
    request_url: str,
    message: str,
    estimated_hours_min: int,
    estimated_hours_max: int,
    confirmed: bool = False,
) -> dict[str, object]:
    """Gera uma prévia e só envia a proposta quando confirmed for verdadeiro."""
    request = ServiceProposalRequest(
        request_url=request_url,
        message=message,
        estimated_hours_min=estimated_hours_min,
        estimated_hours_max=estimated_hours_max,
        confirmed=confirmed,
    )
    return await LinkedInServiceRequests(settings).propose(request)


def main() -> None:
    if settings.transport == "http":
        mcp.run(transport="http", host=settings.host, port=settings.port)
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
