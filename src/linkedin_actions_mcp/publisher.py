import httpx

from .config import Settings
from .models import PostRequest


class LinkedInPublisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def publish(self, request: PostRequest) -> dict[str, str | bool]:
        if not request.confirmed:
            return {
                "published": False,
                "preview": request.text,
                "message": "Prévia criada. Reenvie com confirmed=true para publicar.",
            }

        if self.settings.access_token is None or self.settings.author_urn is None:
            raise RuntimeError(
                "Configure LINKEDIN_ACCESS_TOKEN e LINKEDIN_AUTHOR_URN para publicar pela API oficial."
            )

        payload = {
            "author": self.settings.author_urn,
            "commentary": request.text,
            "visibility": request.visibility.value,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.access_token.get_secret_value()}",
            "LinkedIn-Version": "202609",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(
                "https://api.linkedin.com/rest/posts", json=payload, headers=headers
            )
            response.raise_for_status()
        return {
            "published": True,
            "post_id": response.headers.get("x-restli-id", ""),
            "message": "Publicação criada pela API oficial do LinkedIn.",
        }
