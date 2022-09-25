from uuid import UUID

from .mongo_client import client
from ..models.article import ID_FIELD, Article

DB_NAME = 'main'
COLLECTION_NAME = 'articles'
COLLECTION = client.get_database(DB_NAME).get_collection(COLLECTION_NAME)


def find_article(document_id: UUID):
    return COLLECTION.find_one({ID_FIELD: document_id})


def insert_article(document: Article):
    COLLECTION.insert_one(document.serialize())


def update_article(document: Article):
    COLLECTION.update({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_article(document_id: UUID):
    COLLECTION.delete_one({ID_FIELD: document_id})