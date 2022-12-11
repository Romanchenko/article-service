from bertopic import BERTopic

import re
import spacy
from nltk.corpus import stopwords


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
            nlp = spacy.load('en_core_web_sm')
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
