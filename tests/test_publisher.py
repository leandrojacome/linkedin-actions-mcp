import pytest

from linkedin_actions_mcp.config import Settings
from linkedin_actions_mcp.models import PostRequest
from linkedin_actions_mcp.publisher import LinkedInPublisher


@pytest.mark.asyncio
async def test_unconfirmed_post_returns_preview() -> None:
    result = await LinkedInPublisher(Settings()).publish(PostRequest(text="Olá LinkedIn"))
    assert result["published"] is False
    assert result["preview"] == "Olá LinkedIn"


@pytest.mark.asyncio
async def test_unconfirmed_image_post_returns_image_path(tmp_path) -> None:
    image = tmp_path / "python.png"
    image.write_bytes(b"image")
    result = await LinkedInPublisher(Settings()).publish(
        PostRequest(text="Python", image_path=image)
    )
    assert result["published"] is False
    assert result["image_path"] == str(image.resolve())
