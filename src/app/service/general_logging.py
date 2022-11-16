def get_logging_conf(log_file):
    log_conf = {
        "version": 1,
        "formatters": {
            "file_formatter": {
                "format": "%(asctime)s\t%(levelname)s\t%(message)s",
            },
            "stdout_formatter": {
                "format": "%(asctime)s\t%(levelname)s\t%(funcName)s\t%(message)s",
            },
        },
        "handlers": {
            "file_handler": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "filename": log_file,
                "formatter": "file_formatter",
            },
            "stream_handler": {
                "level": "DEBUG",
                "formatter": "stdout_formatter",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["file_handler", "stream_handler"],
            }
        }
    }
    return log_conf