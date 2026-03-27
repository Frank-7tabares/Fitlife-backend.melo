"""Configuración de logging para la aplicación FitLife."""
import logging
import logging.config
import os


def configure_logging() -> None:
    """Configura el sistema de logging según el entorno."""
    level = logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "fitlife": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": logging.INFO,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": logging.WARNING,
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": logging.WARNING,
        },
    }
    logging.config.dictConfig(config)
