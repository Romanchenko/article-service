from bson import ObjectId
from fastapi import APIRouter, HTTPException

import storage
from storage.articles_storage import find_article
from storage.authors_storage import insert_author, find_author
from ..models.author import Author
from .id_info import IdInfo

router = APIRouter()


@router.get("/authors/{id}", tags=["authors"], response_model=Author)
def get_author(id: ObjectId):
    result = find_author(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@router.post("/authors", tags=["authors"], response_model=IdInfo)
def post_author(article: Author):
    insert_author(article)
    return IdInfo(id=article.id)


@router.post("/authors/{id}", tags=["authors"])
def update_article(id: ObjectId, article: Author):
    if find_article(id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    storage.authors_storage.update_author(article)


@router.delete("/authors/{id}", tags=["authors"])
def delete_article(id: ObjectId):
    storage.authors_storage.delete_author(id)
