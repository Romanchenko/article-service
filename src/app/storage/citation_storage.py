from bson import ObjectId

from .mongo_client import client
from ..models.citation import UNIVERSAL_KEYWORD, Citation
from ..models.py_objectid import PyObjectId

COLLECTION_NAME = 'citation_score'
COLLECTION = client['main'][COLLECTION_NAME]
ID_FIELD = '_id'


def deserialize(citation):
    if citation is None:
        return None
    citation['id'] = PyObjectId(citation.pop(ID_FIELD))
    citation['author'] = PyObjectId(citation['author'])
    print(f'Citation for parse: {citation}')
    return Citation.parse_obj(citation)


def delete_all_by_author(author_id: ObjectId):
    COLLECTION.delete_many({'author': author_id})


def get_all_keywords():
    return set(map(
        lambda x: x['keyword'],
        COLLECTION.find({}, projection={ID_FIELD: False, "keyword": True})
    ))


def update_score(author_id: ObjectId, score: int, keyword: str):
    print(f'author : {author_id}, keyword: {keyword}, score: {score}')
    COLLECTION.update_one({"author": author_id, "keyword": keyword}, {"$set": {"score": score}}, upsert=True)


def get_top(count: int, keyword: str):
    filter = {}
    if keyword != UNIVERSAL_KEYWORD:
        filter = {'keyword': keyword}
    res = list(COLLECTION.find(filter, sort=[('score', -1)]).limit(count))
    print('res:', res)
    return res
