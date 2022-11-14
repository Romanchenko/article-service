from bson import ObjectId
from typing import List, Optional

from .auth import oauth2_scheme, get_user
from .id_info import IdInfo
from .. import storage
from ..service.citation_service import aggregate_citations
from fastapi import APIRouter, HTTPException, Depends
from ..storage.articles_storage import find_article, find_article_by_field, insert_article
from ..models.article import Article
from ..models.search_field_request import SearchFieldRequest


router = APIRouter()


@router.get("/articles/{id}", tags=["articles"], response_model=Article)
def get_article(id: str, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    id = ObjectId(id)
    result = find_article(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@router.post("/articles", tags=["articles"], response_model=IdInfo)
def post_article(article: Article, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    insert_article(article)
    aggregate_citations(article.keywords)
    return IdInfo(id=str(article.id))


@router.post("/articles/{id}", tags=["articles"])
def update_article(id: str, article: Article, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    id = ObjectId(id)
    if find_article(id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    aggregate_citations(article.keywords)
    storage.articles_storage.update_article(article)


@router.delete("/articles/{id}", tags=["articles"])
def delete_article(id: str, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    id = ObjectId(id)
    article = find_article(id)
    if article is None:
        raise HTTPException(status_code=404, detail="Item not found")

    aggregate_citations(article.keywords)
    storage.articles_storage.delete_article(id)


@router.get("/articles", tags=["articles"], response_model=List[Article])
def get_articles_by_field(search_request: List[SearchFieldRequest], token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    return find_article_by_field(search_request)
