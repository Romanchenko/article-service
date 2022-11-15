from typing import List, Optional, Set

from bson import ObjectId

from ..models.citation import UNIVERSAL_KEYWORD
from ..storage.articles_storage import COLLECTION as ARTICLES_COLLECTION
from ..storage.articles_storage import COLLECTION_NAME as ARTICLES_COLLECTION_NAME
from ..storage import citation_storage
from ..storage.authors_storage import COLLECTION, ID_FIELD
from ..storage.mongo_client import client


def delete_citation_by_author(author_id: str):
    citation_storage.delete_all_by_author(ObjectId(author_id))


def get_all_keyword() -> Set:
    keywords = citation_storage.get_all_keywords()
    if UNIVERSAL_KEYWORD in keywords:
        keywords.remove(UNIVERSAL_KEYWORD)
    return keywords


def aggregate_citations(keywords: List[str]):
    keywords.append(None)
    for keyword in keywords:
        aggregate_citations_by_word(keyword)


def aggregate_citations_by_word(keyword: Optional[str]):
    temp_collection = 'temp'
    results_collection = 'results'
    stages = []
    if keyword is not None:
        stages.append(
            {
                '$match': {
                    'keywords': {'$elemMatch': {'$regex': keyword}}
                }
            }
        )
    stages.append(
        {
            '$unwind': '$references'
        }
    )
    stages.append(
        {
            '$group': {
                '_id': "$references",
                'count': {'$count': {}}
            }
        }
    )
    stages.append(
        {
            '$out': {
                'db': 'main', 'coll': temp_collection
            }
        }
    )
    ARTICLES_COLLECTION.aggregate(stages)
    if keyword is None:
        keyword = UNIVERSAL_KEYWORD
    else:
        temp = list(client['main'][temp_collection].find({}))
        print('temp size: {}', len(temp))
    COLLECTION.aggregate([
        {
            '$lookup': {
                'from': ARTICLES_COLLECTION_NAME,
                'localField': ID_FIELD,
                'foreignField': 'authors',
                'as': 'author_docs'
            }
        },
        {
            '$lookup': {
                'from': temp_collection,
                'localField': 'author_docs._id',
                'foreignField': '_id',
                'as': 'citations'
            }
        },
        {
            '$out': {
                'db': 'main', 'coll': results_collection
            }
        }
    ])

    all_documents = list(client['main'][results_collection].find({}))
    for result_doc in all_documents:
        author_id = result_doc['_id']
        if 'citations' in result_doc:
            citations = sum(list(map(lambda x: x['count'], result_doc['citations'])))
            citation_storage.update_score(author_id, citations, keyword)

    client['main'].drop_collection(temp_collection)
    client['main'].drop_collection(results_collection)
