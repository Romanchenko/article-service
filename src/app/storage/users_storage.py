from uuid import UUID

from ..models.user import User
from .mongo_client import client

COLLECTION_NAME = 'users'
COLLECTION = client['main'][COLLECTION_NAME]
ID_FIELD = '_id'


def find_user(document_id: UUID):
    return deserialize(COLLECTION.find_one({ID_FIELD: document_id}))


def insert_user(document: User):
    COLLECTION.insert_one(document.serialize())


def update_user(document: User):
    COLLECTION.update({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_user(document_id: UUID):
    COLLECTION.delete_one({ID_FIELD: document_id})


def deserialize(user_document):
    if user_document is None:
        return None
    user_document['id'] = user_document.pop('_id')
    return User.parse_obj(user_document)
