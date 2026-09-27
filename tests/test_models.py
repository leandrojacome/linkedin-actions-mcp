from pathlib import Path

import pytest
from pydantic import ValidationError

from linkedin_actions_mcp.models import ApplicationRequest, PostRequest, ServiceProposalRequest


def test_post_requires_content() -> None:
    with pytest.raises(ValidationError):
        PostRequest(text="")


def test_post_rejects_missing_image() -> None:
    with pytest.raises(ValidationError):
        PostRequest(text="Python", image_path=Path("missing.png"))


def test_application_rejects_non_linkedin_url() -> None:
    with pytest.raises(ValidationError):
        ApplicationRequest(job_url="https://example.com/jobs/123")


def test_application_rejects_missing_resume() -> None:
    with pytest.raises(ValidationError):
        ApplicationRequest(
            job_url="https://www.linkedin.com/jobs/view/123",
            resume_path=Path("missing.pdf"),
        )


def test_service_proposal_rejects_non_linkedin_url() -> None:
    with pytest.raises(ValidationError):
        ServiceProposalRequest(
            request_url="https://example.com/services/request/123",
            message="A sufficiently detailed proposal message.",
            estimated_hours_min=4,
            estimated_hours_max=8,
        )


def test_service_proposal_rejects_inverted_hours() -> None:
    with pytest.raises(ValidationError):
        ServiceProposalRequest(
            request_url="https://www.linkedin.com/services/request/123",
            message="A sufficiently detailed proposal message.",
            estimated_hours_min=12,
            estimated_hours_max=6,
        )
