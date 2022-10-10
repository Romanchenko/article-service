from uuid import UUID

from ..models.user import User
from .mongo_client import client

COLLECTION_NAME = 'users'
COLLECTION = client['main'][COLLECTION_NAME]
ID_FIELD = '_id'
TOKEN_FIELD = "token"
LOGIN_FIELD = "login"
PASSWORD_HASH_FIELD = "password_hash"


def find_user(document_id: UUID):
    return deserialize(COLLECTION.find_one({ID_FIELD: document_id}))


def find_by_login_and_password(login: str, password_hash: str):
    return deserialize(COLLECTION.find_one({LOGIN_FIELD: login, PASSWORD_HASH_FIELD: password_hash}))


def insert_user(document: User):
    COLLECTION.insert_one(document.serialize())


def update_user(document: User):
    COLLECTION.update({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_user(document_id: UUID):
    COLLECTION.delete_one({ID_FIELD: document_id})


def find_by_token(token: str):
    return deserialize(COLLECTION.find_one({TOKEN_FIELD: token}))


def deserialize(user_document):
    if user_document is None:
        return None
    user_document['id'] = user_document.pop('_id')
    return User.parse_obj(user_document)
