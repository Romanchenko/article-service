import nltk
from nltk.corpus import stopwords
import spacy
import re

nlp=spacy.load('en_core_web_sm')

mystopwords = stopwords.words('english') + \
              ['paper', 'result', 'experiment', 'from', 'subject', 're', 'edu', 'use', 'data', 'method',
               'based', 'new', 'approach', 'also', 'system', 'model', 'present', 'research', 'propose', 'base']


def words_only(text, regex=re.compile('[A-Za-z]+')):
    return ' '.join(regex.findall(text))


def lemmatize(text: str):
    """
    guarantee that text is a string! otherwise it will fail
    """
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc])


def remove_stopwords(text, mystopwords=mystopwords):
    return ' '.join([token for token in text.split() if not token in mystopwords])


def text_preprocessing(text):
    text = words_only(text)
    text = lemmatize(text)
    text = remove_stopwords(text)
    return text
