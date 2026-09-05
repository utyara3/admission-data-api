# Admission Data API

API для агрегации конкурсных списков российских вузов в едином формате.

## Что это

Парсит данные о поступающих с сайтов вузов и отдаёт через REST API. Любой желающий может написать скрапер для своего вуза — система подхватит его автоматически.

## Архитектура

```
┌─────────┐     ┌──────────┐     ┌────────────┐
│  Client  │────▶│   API    │────▶│   Cache    │  Redis
│          │◀────│ (FastAPI)│◀────│  (hit?)    │
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

1. Создай папку `src/scrapers/<university_id>/`
2. Добавь `config.py`:
```python
from src.scrapers.base_config import ScraperConfig

config = ScraperConfig(
    university_id="my_university",
    university_name="Мой Вуз",
    university_short_name="МВ",
    website_url="https://example.com",
)
```
3. Добавь `main.py`:
```python
from src.scrapers.base_scraper import BaseScraper
from src.schemas.contest import ContestListResponse


class MyUniversityScraper(BaseScraper):
    university_id = "my_university"

    async def scrape(
        self,
        education_degree,
        direction_code,
        profile,
        education_form,
        funding_type,
        **kwargs,
    ) -> ContestListResponse:
        # твой парсинг
        ...
```

Реестр подхватит скрапер автоматически.

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
