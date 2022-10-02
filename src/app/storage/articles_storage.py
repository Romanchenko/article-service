from bson import ObjectId

from .mongo_client import client
from ..models.article import ID_FIELD, Article

DB_NAME = 'main'
COLLECTION_NAME = 'articles'
COLLECTION = client.get_database(DB_NAME).get_collection(COLLECTION_NAME)


def find_article(document_id: ObjectId):
    return deserialize(COLLECTION.find_one({ID_FIELD: document_id}))


def insert_article(document: Article):
    COLLECTION.insert_one(document.serialize())


def update_article(document: Article):
    COLLECTION.update({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_article(document_id: ObjectId):
    COLLECTION.delete_one({ID_FIELD: document_id})


def deserialize(article_document):
    article_document['id'] = article_document.pop('_id')
    return Article.parse_obj(article_document)