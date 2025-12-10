import sys
from pathlib import Path
from loguru import logger
from src.config.loader import config

def setup_logger():
    """Настройка логгера loguru на основе настроек."""
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file", "logs/app.log")
    rotation = config.get("logging.rotation", "10 MB")

    # Удаление стандартного обработчика
    logger.remove()

    # Добавление обработчика консоли
    # Добавление обработчика консоли
    if sys.stderr:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

    # Добавление файлового обработчика
    log_file_path = Path(log_file)
    if not log_file_path.is_absolute():
        log_file_path = config.user_dir / log_file_path

    log_dir = log_file_path.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file_path),
        rotation=rotation,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    logger.info("Логгер инициализирован")

# Инициализация при импорте
setup_logger()
