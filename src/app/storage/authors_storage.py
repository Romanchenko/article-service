from bson import ObjectId

from ..models.author import Author
from .mongo_client import client

COLLECTION_NAME = 'authors'
COLLECTION = client['main'][COLLECTION_NAME]
ID_FIELD = '_id'


def find_author(document_id: ObjectId):
    return deserialize(COLLECTION.find_one({ID_FIELD: document_id}))


def find_authors_by_name(author_name: str, full_math: bool):
    expr = {'name': author_name} if full_math else {'name': {'$regex': author_name, '$options': 'i'}}
    return list(deserialize(author).id for author in COLLECTION.find(expr))


def insert_author(document: Author):
    COLLECTION.insert_one(document.serialize())


def update_author(document: Author):
    COLLECTION.update({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_author(document_id: ObjectId):
    COLLECTION.delete_one({ID_FIELD: document_id})


def deserialize(author_document):
    if author_document is None:
        return None
    author_document['id'] = author_document.pop('_id')
    return Author.parse_obj(author_document)


def drop_database():
    client.get_database('main').get_collection(COLLECTION_NAME).drop()
