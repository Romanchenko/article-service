from typing import List

from bson import ObjectId

from ..models.search_field_request import SearchFieldRequest
from .authors_storage import find_authors_by_name
from .mongo_client import client
from ..models.article import ID_FIELD, Article

DB_NAME = 'main'
COLLECTION_NAME = 'articles'
COLLECTION = client.get_database(DB_NAME).get_collection(COLLECTION_NAME)
PAGE_LIMIT = 10
YEAR_FIELD = 'year'
AUTHORS_FIELD = 'authors'


def find_article(document_id: ObjectId):
    return deserialize(COLLECTION.find_one({ID_FIELD: document_id}))


def find_article_by_citation(author_id: ObjectId) -> int:
    return COLLECTION.count_documents({'references': author_id})


def find_article_by_citation(author_id: ObjectId, keyword: str) -> int:
    return COLLECTION.count_documents({'references': author_id, 'keywords': keyword})


def find_article_by_field(search_request: List[SearchFieldRequest]):
    search_request.sort(key=lambda x: x['field'])
    expr = {'$and': []}
    for triple in search_request:
        field, value, full_match = triple.values()
        if field == YEAR_FIELD:
            expr['$and'].append({field: {'$eq': int(value)}})
        elif field == AUTHORS_FIELD:
            author_ids = find_authors_by_name(value, full_match)
            expr['$and'].append({field: {'$in': author_ids}})
        else:
            expr['$and'].append({field: value} if full_match else {field: {'$regex': value}})
    return list(deserialize(article) for article in COLLECTION.find(expr).limit(PAGE_LIMIT))


def drop_database():
    client.get_database(DB_NAME).get_collection(COLLECTION_NAME).drop()


def insert_article(document: Article):
    COLLECTION.insert_one(document.serialize())


def update_article(document: Article):
    COLLECTION.update_one({ID_FIELD: document.id}, {"$set": document.serialize()}, upsert=False)


def delete_article(document_id: ObjectId):
    COLLECTION.delete_one({ID_FIELD: document_id})


def deserialize(article_document):
    if article_document is None:
        return None
    article_document['id'] = article_document.pop('_id')
    return Article.parse_obj(article_document)
