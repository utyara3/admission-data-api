import logging
import os
from logging.handlers import RotatingFileHandler

_is_configured = False


def setup_logger(name: str):
    global _is_configured

    if not _is_configured:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Формат: Время | Уровень | Модуль:Функция:Строка | Сообщение
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 2. Файл (включаем, если переменная LOG_TO_FILE=true)
        if os.getenv("LOG_TO_FILE", "false").lower() == "true":
            log_dir = os.getenv("LOG_DIR", "logs")
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=os.path.join(log_dir, "app.log"),
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=3,  # Хранить 3 старых файла + текущий
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            root_logger.info(f"Логирование в файл активировано: {log_dir}/app.log")

        uvicorn_loggers = ("uvicorn", "uvicorn.error", "uvicorn.access")
        for logger in uvicorn_loggers:
            uvicorn_logger = logging.getLogger(logger)
            uvicorn_logger.handlers = []
            uvicorn_logger.propagate = True

        logging.getLogger("uvicorn.access").setLevel(logging.INFO)

        _is_configured = True

    return logging.getLogger(name)
