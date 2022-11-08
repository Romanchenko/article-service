from ..models.citation import UNIVERSAL_KEYWORD
from ..storage.articles_storage import COLLECTION as ARTICLES_COLLECTION
from ..storage.articles_storage import COLLECTION_NAME as ARTICLES_COLLECTION_NAME
from ..storage import citation_storage
from ..storage.authors_storage import COLLECTION, ID_FIELD
from ..storage.mongo_client import client


def aggregate_citations():
    temp_collection = 'temp'
    results_collection = 'results'
    ARTICLES_COLLECTION.aggregate([
        {
            '$unwind': '$references'
        },
        {
            '$group': {
                '_id': "$references",
                'count': {'$count': {}}
            }
        },
        {
            '$out': {
                'db': 'main', 'coll': temp_collection
            }
        }
    ])
    temp_res = client['main'][temp_collection].find({})
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
            citation_storage.update_score(author_id, citations, UNIVERSAL_KEYWORD)

    client['main'].drop_collection(temp_collection)
    client['main'].drop_collection(results_collection)
