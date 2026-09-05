# Admission Data API

API для агрегации конкурсных списков российских вузов в едином формате.

## Что это

Парсит данные о поступающих с сайтов вузов и отдаёт через REST API. Любой желающий может написать скрапер для своего вуза — система подхватит его автоматически.

## Архитектура

```
┌─────────┐     ┌──────────┐     ┌────────────┐
│  Client │────▶│   API    │────▶│   Cache    │  Redis
│         │◀────│ (FastAPI)│◀────│  (hit?)    │
└─────────┘     └────┬─────┘     └────────────┘
                     │ miss
                     ▼
               ┌───────────┐
               │  Service   │  AdmissionSyncService
               │  (logic)   │
               └─────┬─────┘
                     │
              ┌──────┴──────┐
              ▼              ▼
        ┌──────────┐  ┌──────────┐
        │   Repo   │  │  Celery   │  background
        │   (DB)   │  │  Worker   │  ──▶ Scraper ──▶ Save
        └────┬─────┘  └──────────┘
             ▼
        PostgreSQL
```

### Запрос → Ответ

1. `GET /contest-lists?university=spbstu&code=09.03.04&...`
2. Проверяем **Redis cache** → HIT — отдаём сразу
3. MISS — идём в **PostgreSQL**
4. Если данных нет — enqueue **Celery task**, опрашиваем БД до 5 сек
5. Scraper парсит сайт вуза → сохраняет в БД → инвалидирует кэш
6. Следующий запрос получает данные из кэша

## Модели

```
University ──1:N──▶ Direction ──1:N──▶ Snapshot ──1:N──▶ Application ──N:1──▶ Applicant
```

```python
# University — вуз
class University(Base):
    id: int  # PK
    university_id: str  # "spbstu", "mock"
    full_name: str  # "СПбПУ им. Петра Великого"
    short_name: str  # "СПбПУ"


# Direction — направление подготовки
class Direction(Base):
    id: int  # PK
    university_id: int  # FK → University
    education_degree: EducationDegree  # bachelor / specialist / master
    code: str  # "09.03.04"
    name: str  # "Информатика и вычислительная техника"
    profile: str | None  # "Искусственный интеллект"
    education_form: EducationForm  # full_time / part_time / distance
    funding_type: FundingType  # budget / paid / ...


# Snapshot — снимок данных на момент скрапинга
class Snapshot(Base):
    id: int  # PK
    direction_id: int  # FK → Direction
    created_at: datetime  # когда был создан снимок


# Application — заявка абитуриента на направление
class Application(Base):
    applicant_db_id: int  # PK, FK → Applicant
    direction_id: int  # PK, FK → Direction
    snapshot_id: int  # PK, FK → Snapshot
    position: int  # позиция в списке
    score_for_ia: int  # баллы за ИД
    priority: int  # приоритет
    has_original: bool  # подан ли оригинал
    is_bvi: bool  # без вступительных испытаний
    status: ApplicantContestStatus


# Applicant — абитуриент
class Applicant(Base):
    id: int  # PK
    applicant_id: str  # внешний ID от вуза
    sum_of_scores: int  # сумма баллов
    score_for_exams: dict  # JSONB: {"rus": 91, "math_prof": 86, "it": 90}
```

Composite PK `(applicant_db_id, direction_id, snapshot_id)` гарантирует уникальность: один абитуриент — одна заявка на одно направление в одном снимке.

## Структура проекта

```
src/
├── api/v1/
│   └── contest_lists.py    # эндпоинты: /universities, /contest-lists
├── cache/
│   └── contest.py          # Redis cache (ContestCache)
├── core/
│   ├── config.py           # pydantic-settings (.env)
│   ├── database.py         # SQLAlchemy async engine + session
│   ├── enums.py            # EducationDegree, FundingType, ...
│   └── redis_client.py     # Redis connection pool
├── models/                 # SQLAlchemy ORM
├── repositories/           # DB access layer
├── schemas/                # Pydantic response/query models
├── scrapers/
│   ├── base_scraper.py     # абстрактный BaseScraper
│   ├── spbstu/             # СПбПУ
│   └── mock/               # тестовый скрапер
├── services/
│   └── admission_sync.py   # бизнес-логика sync
└── tasks/
    ├── __init__.py          # Celery app config
    └── admission.py         # scrape_contest_list task
```

## Добавить свой скрапер

### 1. Создай папку

```
src/scrapers/my_university/
├── __init__.py
├── config.py
└── main.py
```

### 2. `config.py` — метаданные вуза

```python
from src.scrapers.base_config import ScraperConfig

config = ScraperConfig(
    university_id="my_university",           # уникальный ID (латиница, используется в URL)
    university_name="Мой Университет",       # полное название
    university_short_name="МУ",              # короткое название
    website_url="https://myuni.ru",          # сайт вуза
    description="Описание для /universities",
)
```

### 3. `main.py` — логика парсинга

```python
from src.core.enums import EducationDegree, EducationForm, FundingType
from src.schemas import (
    ApplicantSchema,
    ContestListResponse,
    DirectionSchema,
    UniversitySchema,
)
from src.scrapers.base_scraper import BaseScraper

from .config import config


class MyUniversityScraper(BaseScraper):
    university_id = config.university_id

    async def scrape(
        self,
        education_degree: EducationDegree,
        direction_code: str,
        profile: str | None,
        education_form: EducationForm,
        funding_type: FundingType,
        **kwargs,
    ) -> ContestListResponse:
        # --- Твой парсинг ---
        # Например, через httpx + BeautifulSoup или Playwright:
        #
        # async with httpx.AsyncClient() as client:
        #     html = await client.get(f"https://myuni.ru/contest/{direction_code}")
        # soup = BeautifulSoup(html.text, "html.parser")
        #
        # applicants = []
        # for row in soup.select("table.contest tr")[1:]:
        #     cells = row.find_all("td")
        #     applicants.append(ApplicantSchema(
        #         position=int(cells[0].text),
        #         applicant_id=int(cells[1].text),
        #         priority=int(cells[2].text),
        #         has_original=cells[3].text == "Да",
        #         is_bvi=False,
        #         total_score=int(cells[4].text),
        #         ia_score=int(cells[5].text),
        #         exam_scores={"rus": 80, "math_prof": 70, "it": 90},
        #         status="Участвует в конкурсе",
        #     ))
        #
        # return ContestListResponse(...)

        # Заглушка (удали и замени на реальный парсинг):
        return ContestListResponse(
            university=UniversitySchema(
                id=config.university_id,
                full_name=config.university_name,
                short_name=config.university_short_name,
            ),
            direction=DirectionSchema(
                code=direction_code,
                profile=profile,
                education_form=education_form,
                funding_type=funding_type,
                education_degree=education_degree,
            ),
            applicant=[],
        )
```

### 4. Что должен вернуть `scrape()`

Метод возвращает `ContestListResponse` — единый формат для всех вузов:

```
ContestListResponse
├── university: UniversitySchema      # id, full_name, short_name
├── direction: DirectionSchema        # code, profile, education_form, funding_type, education_degree
└── applicant: list[ApplicantSchema]  # каждый абитуриент
    ├── position          # позиция в конкурсном списке
    ├── applicant_id      # уникальный ID абитуриента (внутренний ID вуза)
    ├── priority          # приоритет направления (1, 2, 3...)
    ├── has_original      # подан ли оригинал аттестата
    ├── is_bvi            # поступает ли без вступительных
    ├── total_score       # суммарный балл
    ├── ia_score          # баллы за индивидуальные достижения
    ├── exam_scores       # баллы по предметам: {"rus": 91, "math_prof": 86, "it": 90}
    └── status            # "Участвует в конкурсе", "Передано в вуз", ...
```

### 5. Именование

Класс скрапера **должен** заканчиваться на `Scraper` и наследовать `BaseScraper`:

```python
class MyUniversityScraper(BaseScraper):  # ✅ правильно
class MyUniversity(BaseScraper):         # ❌ не будет найден
```

### 6. Тестирование

```bash
# проверь что скрапер загрузился
curl http://localhost:8000/universities | jq '.[].id'

# запроси данные
curl "http://localhost:8000/contest-lists?university=my_university&education_degree=bachelor&code=09.03.04&education_form=full_time&funding_type=budget"
```

### Полный пример: mock-скрапер

Готовый рабочий пример — `src/scrapers/mock/`. Генерирует случайные данные, полезен для разработки без реальных HTTP-запросов.

## Запуск

```bash
cp .env-example .env       # настрой переменные
make dcu                   # docker compose up (postgres + redis + api + celery)
```

```bash
# без Docker
alembic upgrade head
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
make lint                  # ruff check + format
python -m pytest tests/ -v # тесты
```

## Стек

- **FastAPI** — async API
- **SQLAlchemy 2.x** — async ORM
- **PostgreSQL** — основная БД
- **Redis** — кэш + Celery broker
- **Celery** — фоновые задачи (скрапинг)
- **Playwright** — парсинг динамических сайтов
- **Alembic** — миграции
