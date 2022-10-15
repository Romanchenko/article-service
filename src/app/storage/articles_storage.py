from bson import ObjectId

from .mongo_client import client
from ..models.article import ID_FIELD, Article

DB_NAME = 'main'
COLLECTION_NAME = 'articles'
COLLECTION = client.get_database(DB_NAME).get_collection(COLLECTION_NAME)
PAGE_LIMIT = 10


def find_article(document_id: ObjectId):
    return deserialize(COLLECTION.find_one({ID_FIELD: document_id}))


def find_article_by_field(field: str, value: str, full_match=False):
    expr = {field: value} if full_match else {field: {'$regex': value}}
    return list(deserialize(article) for article in COLLECTION.find(expr).limit(PAGE_LIMIT))


def drop_database():
    client.get_database(DB_NAME).get_collection(COLLECTION_NAME).drop()


def insert_article(document: Article):
    COLLECTION.insert_one(document.serialize())


def update_article(document: Article):
    COLLECTION.update({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_article(document_id: ObjectId):
    COLLECTION.delete_one({ID_FIELD: document_id})


def deserialize(article_document):
    if article_document is None:
        return None
    article_document['id'] = article_document.pop('_id')
    return Article.parse_obj(article_document)