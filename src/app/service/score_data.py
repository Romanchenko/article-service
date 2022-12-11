from tqdm import tqdm
from ..storage.articles_storage import get_all_cursor, update_tag
from .model_inf import TopicModeling

model_runner = None


def score_data(logger):
    global model_runner
    if model_runner is None:
        model_runner = TopicModeling('/models/bert_model_100k')
    for article in tqdm(get_all_cursor()):
        abstract = article['abstract']
        article_id = article['_id']
        topics = model_runner.score_text(abstract)
        if len(topics) > 0:
            logger.info(f"Will update {article_id} article with topic {topics[0]}")
            # update_tag(article_id, tag=topics_dict[topics[0]])
        else:
            logger.info(f"Empty topics for article {article_id}")


def update_scores(logger):
    score_data(logger)

