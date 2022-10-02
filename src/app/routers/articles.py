from bson import ObjectId

from .id_info import IdInfo
from .. import storage
from fastapi import APIRouter, HTTPException
from ..storage.articles_storage import find_article, insert_article
from ..models.article import Article

router = APIRouter()


@router.get("/articles/{id}", tags=["articles"], response_model=Article)
def get_article(id: ObjectId):
    result = find_article(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@router.post("/articles", tags=["articles"], response_model=IdInfo)
def post_article(article: Article):
    insert_article(article)
    return IdInfo(id=article.id)


@router.post("/articles/{id}", tags=["articles"])
def update_article(id: ObjectId, article: Article):
    if find_article(id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    storage.articles_storage.update_article(article)


@router.delete("/articles/{id}", tags=["articles"])
def delete_article(id: ObjectId):
    storage.articles_storage.delete_article(id)
