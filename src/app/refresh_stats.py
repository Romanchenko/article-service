import schedule
import time
import logging.config
from .service.citation_service import get_all_keyword, aggregate_citations
import logging

from .service.general_logging import get_logging_conf
from .service.score_data import update_scores

logging.config.dictConfig(get_logging_conf('cron.log'))
log = logging.getLogger(__name__)


def update_stats():
    start_ts = time.time()
    keywords = get_all_keyword()
    log.info("Got %s keywords", len(keywords))
    end_ts = time.time()
    log.info(f"Finished search of keywords in {end_ts - start_ts}s")

    log.info("Starting aggregation")
    start_ts = time.time()
    aggregate_citations(list(keywords))
    end_ts = time.time()
    log.info("Finished aggregation in %d s", end_ts - start_ts)


def calculate_model():
    log.info("Starting score update")
    start_ts = time.time()
    update_scores()
    end_ts = time.time()
    log.info("Finished scores update in %d s", end_ts - start_ts)


if __name__ == '__main__':
    schedule.every(3).hours.do(update_stats)
    schedule.every(3).hours.do(calculate_model())
    while 1:
        schedule.run_pending()
        time.sleep(1)
