from patchright.async_api import async_playwright

from .config import Settings
from .models import ApplicationRequest


class LinkedInApplicant:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def apply(self, request: ApplicationRequest) -> dict[str, object]:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                str(self.settings.browser_profile_dir),
                headless=self.settings.headless,
                channel="chrome",
            )
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto(str(request.job_url), wait_until="domcontentloaded")

            if "login" in page.url or await page.locator('input[name="session_key"]').count():
                await context.close()
                raise RuntimeError(
                    "A sessão do LinkedIn não está autenticada. Execute o login local antes de tentar novamente."
                )

            easy_apply = page.get_by_role("button", name="Easy Apply")
            portuguese_apply = page.get_by_role("button", name="Candidatura simplificada")
            button = easy_apply if await easy_apply.count() else portuguese_apply
            if not await button.count():
                external = page.locator('a[href*="apply"]')
                result = {
                    "submitted": False,
                    "application_type": "external",
                    "application_url": await external.first.get_attribute("href")
                    if await external.count()
                    else None,
                    "message": "A vaga não oferece candidatura simplificada.",
                }
                await context.close()
                return result

            await button.first.click()
            await page.wait_for_timeout(800)

            if request.resume_path is not None:
                upload = page.locator('input[type="file"]')
                if await upload.count():
                    await upload.first.set_input_files(str(request.resume_path))

            result: dict[str, object] = {
                "submitted": False,
                "application_type": "easy_apply",
                "message": "Formulário aberto e currículo anexado quando solicitado.",
            }
            if request.confirmed:
                submit = page.get_by_role("button", name="Submit application")
                if not await submit.count():
                    submit = page.get_by_role("button", name="Enviar candidatura")
                if await submit.count():
                    await submit.first.click()
                    await page.wait_for_timeout(1200)
                    result = {
                        "submitted": True,
                        "application_type": "easy_apply",
                        "message": "Candidatura enviada pelo fluxo simplificado.",
                    }
                else:
                    result["message"] = (
                        "O formulário exige etapas ou respostas adicionais; nenhuma candidatura foi enviada."
                    )
            await context.close()
            return result
