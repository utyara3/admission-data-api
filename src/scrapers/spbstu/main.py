from playwright.async_api import async_playwright

from src.core.schemas import (
    ApplicantSchema,
    UniversitySchema,
    DirectionSchema,
    ContestListResponse,
)
from src.scrapers.base import BaseScraper
from .config import config


class SPBSTUScraper(BaseScraper):
    university_id = "spbstu"

    SELECTOR_EDUCATION_FORMS_IDS = {"distance": "1", "full_time": "2", "part_time": "3"}
    SELECTOR_FUNDING_TYPE_IDS = {
        "budget": "1",
        "paid": "2",
        "commercial": "3",
        "special_quota": "4",
        "separate_quota": "5",
        "target": "6",
    }

    async def scrape(
        self, direction_code: str, education_form: str, funding_type: str, **kwargs
    ) -> ContestListResponse:
        direction_code = direction_code.lower()
        education_form = education_form.lower()
        funding_type = funding_type.lower()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                print("Загружаем страницу политеха")
                await page.goto(
                    "https://my.spbstu.ru/home/abit/list-applicants/bachelor",
                    timeout=30000,
                )
                await page.wait_for_load_state("networkidle")

                selects = page.locator("select")

                # Фильтр формы обучения
                print(f"Форма обучения {education_form}")
                await selects.nth(0).select_option(
                    self.SELECTOR_EDUCATION_FORMS_IDS[education_form]
                )

                # Фильтр типа финансирования
                print(f"Тип финансирования {funding_type}")
                await selects.nth(1).select_option(
                    self.SELECTOR_FUNDING_TYPE_IDS[funding_type]
                )

                # Фильтр направления, элементы которого появляются после get api
                print(f"Направление {direction_code}")
                direction_selector = selects.nth(2)
                await page.wait_for_function(
                    "el => el.options.length > 1",
                    arg=await direction_selector.element_handle(),
                )

                async with page.expect_response(
                    lambda res: "get-abit-list" in res.url and res.status == 200,
                    timeout=15000,
                ) as response_info:
                    target_option = direction_selector.locator(
                        "option", has_text=direction_code
                    )
                    option_value = await target_option.get_attribute("value")
                    await direction_selector.select_option(value=option_value)

                response = await response_info.value
                raw_json = await response.json()

                print("Данные успешно перехвачены из API")
                ret_data = self._validate_raw_json(
                    raw_json, direction_code, education_form, funding_type
                )

                return ret_data

            except Exception as e:
                print(f"Ошибка при парсинге: {str(e)[:500]}")
                raise

            finally:
                await context.close()
                await browser.close()

    def _validate_raw_json(
        self, raw_json: dict, code: str, education_form: str, funding_type: str
    ) -> ContestListResponse:
        applicants = []

        contest_list = raw_json.get("results")
        if contest_list is None:
            raise ValueError(f"Result of parsing {self.university_id} is None")

        for raw_applicant in contest_list:
            keys = list(raw_applicant.keys())
            start_idx = keys.index("sum_vs")
            end_idx = keys.index("counl_ind")

            exam_scores = {
                k: raw_applicant[k] or 0 for k in keys[start_idx + 1 : end_idx]
            }

            if raw_applicant["sum"] is None:
                total_score = 0
                ia_score = 0
            else:
                total_score = raw_applicant["sum"]
                ia_score = int(raw_applicant["sum"]) - int(raw_applicant["sum_vs"])

            applicant = ApplicantSchema(
                position=raw_applicant["num"],
                applicant_id=raw_applicant["code"],
                priority=raw_applicant["priority"],
                has_original=True if raw_applicant["approval"] == "+" else False,
                is_bvi=True
                if "Без вступительных испытаний" in raw_applicant["base"]
                else False,
                total_score=total_score,
                ia_score=ia_score,
                exam_scores=exam_scores,
                status=raw_applicant["info"],
            )

            applicants.append(applicant)

        return ContestListResponse(
            university=UniversitySchema(
                id=self.university_id,
                full_name=config.university_name,
                short_name=config.university_short_name,
            ),
            direction=DirectionSchema(
                code=code,
                profile=None,
                education_form=education_form,
                funding_type=funding_type,
            ),
            applicant=applicants,
        )

    async def get_available_directions(self) -> list[dict]:
        return [{}]
