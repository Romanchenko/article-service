from tqdm import tqdm
from text_preprocess import text_preprocessing
from bertopic import BERTopic
from ..storage.articles_storage import get_all_cursor, update_tag


def score_data(model, logger):
    topics_dict = dict(zip(model.get_topic_info()['Topic'], model.get_topic_info()['Name']))
    for article in tqdm(get_all_cursor()):
        abstract = article['abstract']
        article_id = article['_id']
        preprocessed_abstract = text_preprocessing(abstract[1])
        topics, prob = model.transform(preprocessed_abstract)
        if len(topics) > 0:
            logger.info(f"Will update {article_id} article with topic {topics_dict[topics[0]]}")
            # update_tag(article_id, tag=topics_dict[topics[0]])
        else:
            logger.info(f"Empty topics for article {article_id}")


def update_scores(logger):
    model = BERTopic.load('/models/bert_model_100k')
    score_data(model, logger)

