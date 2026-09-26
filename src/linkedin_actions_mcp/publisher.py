from pathlib import Path

import httpx

from .config import Settings
from .models import PostRequest


class LinkedInPublisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def publish(self, request: PostRequest) -> dict[str, str | bool]:
        if not request.confirmed:
            preview: dict[str, str | bool] = {
                "published": False,
                "preview": request.text,
                "message": "Prévia criada. Reenvie com confirmed=true para publicar.",
            }
            if request.image_path is not None:
                preview["image_path"] = str(request.image_path)
            return preview

        if self.settings.access_token is None or self.settings.author_urn is None:
            raise RuntimeError(
                "Configure LINKEDIN_ACCESS_TOKEN e LINKEDIN_AUTHOR_URN para publicar pela API oficial."
            )

        headers = {
            "Authorization": f"Bearer {self.settings.access_token.get_secret_value()}",
            "LinkedIn-Version": "202609",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        payload: dict[str, object] = {
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
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            if request.image_path is not None:
                image_urn = await self._upload_image(client, request.image_path, headers)
                payload["content"] = {
                    "media": {
                        "id": image_urn,
                        "altText": request.image_alt_text or request.image_path.stem,
                    }
                }
            response = await client.post(
                "https://api.linkedin.com/rest/posts", json=payload, headers=headers
            )
            response.raise_for_status()
        return {
            "published": True,
            "post_id": response.headers.get("x-restli-id", ""),
            "message": "Publicação criada pela API oficial do LinkedIn.",
        }

    async def _upload_image(
        self,
        client: httpx.AsyncClient,
        image_path: Path,
        headers: dict[str, str],
    ) -> str:
        upload = await client.post(
            "https://api.linkedin.com/rest/images?action=initializeUpload",
            json={"initializeUploadRequest": {"owner": self.settings.author_urn}},
            headers=headers,
        )
        upload.raise_for_status()
        value = upload.json()["value"]
        upload_url = value["uploadUrl"]
        image_urn = value["image"]

        image_bytes = image_path.read_bytes()
        uploaded = await client.put(
            upload_url,
            content=image_bytes,
            headers={"Authorization": headers["Authorization"]},
        )
        uploaded.raise_for_status()
        return str(image_urn)
