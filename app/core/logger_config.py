import logging
import logging.config
import os

os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "mode": "w",
            "formatter": "simple",
            "level": "INFO",
        },
    },
    "loggers": {
        "myapp": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "gradio": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "ERROR",
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("myapp")
