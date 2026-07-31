from playwright.async_api import async_playwright

from src.core.schemas import (
    ApplicantSchema,
    UniversitySchema,
    DirectionSchema,
    ContestListResponse,
)
from src.scrapers.base_scraper import BaseScraper
from src.core.logger_config import setup_logger
from .config import config

logger = setup_logger(__name__)


class SPBSTUScraper(BaseScraper):
    university_id = config.university_id

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
        self,
        education_grade: str,
        direction_code: str,
        profile: str | None,
        education_form: str,
        funding_type: str,
        **kwargs,
    ) -> ContestListResponse:
        direction_code = direction_code.lower()
        education_form = education_form.lower()
        funding_type = funding_type.lower()

        if education_grade == "specialist":
            education_grade = "bachelor"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                logger.info("Загружаем страницу политеха")
                await page.goto(
                    f"https://my.spbstu.ru/home/abit/list-applicants/{education_grade}",
                    timeout=30000,
                )
                await page.wait_for_load_state("networkidle")

                selects = page.locator("select")

                # Фильтр формы обучения
                logger.debug(f"Форма обучения {education_form}")
                await selects.nth(0).select_option(
                    self.SELECTOR_EDUCATION_FORMS_IDS[education_form]
                )

                # Фильтр типа финансирования
                logger.debug(f"Тип финансирования {funding_type}")
                await selects.nth(1).select_option(
                    self.SELECTOR_FUNDING_TYPE_IDS[funding_type]
                )

                # Фильтр направления, элементы которого появляются после get api
                logger.debug(f"Направление {direction_code}")
                direction_selector = selects.nth(2)
                await page.wait_for_function(
                    "el => el.options.length > 1",
                    arg=await direction_selector.element_handle(),
                )

                async with page.expect_response(
                    lambda res: "get-abit-list" in res.url and res.status == 200,
                    timeout=15000,
                ) as response_info:
                    all_options = await direction_selector.locator("option").all()

                    matching_options = []
                    for option in all_options:
                        text = await option.inner_text()
                        if direction_code in text:
                            matching_options.append(option)

                    if profile and matching_options:
                        profile_lower = profile.lower()
                        filtered_options = [
                            option
                            for option in matching_options
                            if profile_lower in (await option.inner_text()).lower()
                        ]
                        if filtered_options:
                            matching_options = filtered_options

                    if not matching_options:
                        raise ValueError(
                            f"Не найдено направление {direction_code}"
                            + (f"с профилем '{profile}'" if profile else "")
                        )

                    if len(matching_options) > 1:
                        texts = [
                            await option.inner_text() for option in matching_options
                        ]
                        raise ValueError(
                            "Найдено несколько направлений с теми же названиями:\n"
                            + "\n".join(texts)
                        )

                    target_option = matching_options[0]
                    option_value = await target_option.get_attribute("value")

                    await direction_selector.select_option(value=option_value)

                response = await response_info.value
                raw_json = await response.json()

                ret_data = self._validate_raw_json(
                    raw_json, direction_code, profile, education_form, funding_type
                )

                return ret_data

            except Exception as e:
                logger.error(f"Ошибка при парсинге: {str(e)}")
                raise

            finally:
                await context.close()
                await browser.close()

    def _validate_raw_json(
        self,
        raw_json: dict,
        code: str,
        profile: str | None,
        education_form: str,
        funding_type: str,
    ) -> ContestListResponse:
        applicants = []
        results = raw_json.get("results")

        if results is None:
            raise ValueError(f"Result of parsing {self.university_id} is None")

        for raw_applicant in results:
            keys = list(raw_applicant.keys())
            start_idx = keys.index("sum_vs")
            end_idx = keys.index("counl_ind")

            exam_scores = {
                k: raw_applicant[k] or 0 for k in keys[start_idx + 1 : end_idx]
            }

            # Считаем баллы
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
                profile=profile,
                education_form=education_form,
                funding_type=funding_type,
            ),
            applicant=applicants,
        )
