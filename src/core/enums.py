from enum import Enum


class EducationDegree(str, Enum):
    """Вид образования"""

    BACHELOR = "bachelor"  # бакалавриат
    SPECIALIST = "specialist"  # специалитет
    MASTER = "master"  # магистратура
    POSTGRADUATE = "postgraduate"  # аспирантура


class EducationForm(str, Enum):
    """Форма образования"""

    FULL_TIME = "full_time"  # очная
    PART_TIME = "part_time"  # очно-заочная
    DISTANCE = "distance"  # заочная


class FundingType(str, Enum):
    """Тип финансирования"""

    BUDGET = "budget"
    PAID = "paid"  # платное
    COMMERCIAL = "commercial"  # контракт
    SPECIAL_QUOTA = "special_quota"  # специальная квота
    SEPARATE_QUOTA = "separate_quota"  # отдельная квота
    TARGET = "target"  # целевое


class ApplicantContestStatus(Enum):
    """Статусы абитуриента, отображаемые в конкурсных и рейтинговых списках вузов"""

    # Активное участие в конкурсе
    IN_CONTEST = "Участвует в конкурсе"

    # Этап ожидания и проверки баллов
    AWAITING_RESULTS = "Ожидание результатов испытаний"
    AWAITING_CHECK = "На рассмотрении"

    # Финальные положительные статусы
    SUBMITTED = "Передано в вуз"

    # Финальные отрицательные статусы
    REJECTED = "Вуз отклонил выбор конкурсной группы"
    EXCLUDED = "Конкурсная группа исключена"


class ExamSubject(str, Enum):
    """Доступные предметы ЕГЭ"""

    # Обязательные предметы
    RUSSIAN = "rus"
    MATH_BASE = "math_base"  # Базовая математика
    MATH_PROF = "math_prof"  # Профильная математика

    # Точные и естественные науки
    PHYSICS = "phys"
    CHEMISTRY = "chem"
    INFORMATICS = "it"
    BIOLOGY = "bio"
    GEOGRAPHY = "geo"

    # Гуманитарные и социальные науки
    SOCIOLOGY = "social"  # Обществознание
    HISTORY = "hist"
    LITERATURE = "lit"

    # Иностранные языки
    ENGLISH = "eng"
    GERMAN = "ger"
    FRENCH = "fra"
    SPANISH = "spa"
    CHINESE = "chn"
