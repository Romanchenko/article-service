from tqdm import tqdm
from bertopic import BERTopic
from ..storage.articles_storage import get_all_cursor, update_tag

import pickle
import re
import spacy
from nltk.corpus import stopwords

model_runner = None
nlp = spacy.load('en_core_web_sm')
class TopicModeling:

    def __init__(self, path_to_model: str):
        self.bert_model = BERTopic.load(path_to_model)
        self.topic_dict = dict(zip(self.bert_model.get_topic_info()['Topic'],
                                   self.bert_model.get_topic_info()['Name']))

    def text_preprocessing(self, text):
        if isinstance(text, str):
            text = [text]
        for idx, txt in enumerate(text):
            regex = re.compile('[A-Za-z]+')
            mystopwords = stopwords.words('english') + ['paper', 'result', 'experiment', 'from', 'subject',
                                                        're', 'edu', 'use', 'data', 'method', 'based',
                                                        'new', 'approach', 'also', 'system', 'model',
                                                        'present', 'research', 'propose', 'base']

            text[idx] = ' '.join(regex.findall(txt))
            doc = nlp(txt)
            text[idx] = ' '.join([token.lemma_ for token in doc])
            text[idx] = ' '.join([token for token in txt.split() if not token in mystopwords])

        return text

    def score_text(self, text):
        text = self.text_preprocessing(text)
        topics, prob = self.bert_model.transform(text)
        for idx, topic in enumerate(topics):
            topics[idx] = self.topic_dict[topic]
        return topics

def score_data(logger):
    global model_runner
    if model_runner is None:
        model_runner = TopicModeling('/models/topic_modeling_pipeline.pkl')
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

