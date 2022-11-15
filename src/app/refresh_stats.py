import schedule
import time
import logging.config
from .service.citation_service import get_all_keyword, aggregate_citations
import logging

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
            "filename": "cron.log",
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

logging.config.dictConfig(log_conf)
log = logging.getLogger(__name__)


def job():
    start_ts = time.time()
    keywords = get_all_keyword()
    log.info("Got %s keywords", len(keywords))
    end_ts = time.time()
    log.info(f"Finished search of keywords in {end_ts - start_ts}ms")

    log.info("Starting aggregation")
    start_ts = time.time()
    aggregate_citations(list(keywords))
    end_ts = time.time()
    log.info("Finished aggregation in %d ms", end_ts - start_ts)


if __name__ == '__main__':
    schedule.every(3).hours.do(job)
    while 1:
        schedule.run_pending()
        time.sleep(1)
