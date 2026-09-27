from patchright.async_api import Page, async_playwright

from .config import Settings
from .models import ServiceProposalRequest


class LinkedInServiceRequests:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def _authenticated_page(self, context) -> Page:
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(self.settings.service_requests_url, wait_until="domcontentloaded")
        if "login" in page.url or await page.locator('input[name="session_key"]').count():
            raise RuntimeError(
                "A sessão do LinkedIn não está autenticada. Execute o login local antes de continuar."
            )
        return page

    async def list(self, limit: int = 20) -> dict[str, object]:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                str(self.settings.browser_profile_dir),
                headless=self.settings.headless,
                channel="chrome",
            )
            try:
                page = await self._authenticated_page(context)
                links = page.locator('a[href*="/services/"]')
                requests: list[dict[str, str]] = []
                seen: set[str] = set()
                for index in range(min(await links.count(), limit * 4)):
                    link = links.nth(index)
                    href = await link.get_attribute("href")
                    text = " ".join((await link.inner_text()).split())
                    if not href or not text or href in seen:
                        continue
                    if "request" not in href.lower() and "proposal" not in href.lower():
                        continue
                    seen.add(href)
                    requests.append({"title": text, "url": href})
                    if len(requests) >= limit:
                        break
                return {"count": len(requests), "requests": requests}
            finally:
                await context.close()

    async def read(self, request_url: str) -> dict[str, object]:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                str(self.settings.browser_profile_dir),
                headless=self.settings.headless,
                channel="chrome",
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(request_url, wait_until="domcontentloaded")
                if "login" in page.url:
                    raise RuntimeError("A sessão do LinkedIn não está autenticada.")
                main = page.locator("main")
                content = await (main if await main.count() else page.locator("body")).inner_text()
                return {"url": page.url, "content": content[:12000]}
            finally:
                await context.close()

    async def propose(self, request: ServiceProposalRequest) -> dict[str, object]:
        preview = {
            "submitted": False,
            "request_url": str(request.request_url),
            "message": request.message,
            "estimated_hours_min": request.estimated_hours_min,
            "estimated_hours_max": request.estimated_hours_max,
        }
        if not request.confirmed:
            return preview

        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                str(self.settings.browser_profile_dir),
                headless=self.settings.headless,
                channel="chrome",
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(str(request.request_url), wait_until="domcontentloaded")
                if "login" in page.url:
                    raise RuntimeError("A sessão do LinkedIn não está autenticada.")

                message = page.locator("textarea").first
                if not await message.count():
                    raise RuntimeError("O campo da proposta não foi encontrado; nada foi enviado.")
                await message.fill(request.message)

                submit = page.get_by_role("button", name="Submit proposal")
                if not await submit.count():
                    submit = page.get_by_role("button", name="Enviar proposta")
                if not await submit.count():
                    raise RuntimeError("O botão de envio não foi encontrado; nada foi enviado.")
                await submit.first.click()
                await page.wait_for_timeout(1200)
                return {**preview, "submitted": True}
            finally:
                await context.close()
