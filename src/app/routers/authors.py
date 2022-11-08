from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from ..models.citation import UNIVERSAL_KEYWORD
from .auth import oauth2_scheme, get_user
from .. import storage
from ..storage.authors_storage import insert_author, find_author
from ..service.citation_service import delete_citation_by_author
from ..models.author import Author, Authors
from .id_info import IdInfo
from ..storage import citation_storage

router = APIRouter()


@router.get("/authors/{id}", tags=["authors"], response_model=Author)
def get_author(id: str, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    id = ObjectId(id)
    result = find_author(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@router.post("/authors", tags=["authors"], response_model=IdInfo)
def post_author(author: Author, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    insert_author(author)
    return IdInfo(id=str(author.id))


@router.post("/authors/{id}", tags=["authors"])
def update_author(id: str, author: Author, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    id = ObjectId(id)
    if find_author(id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    storage.authors_storage.update_author(author)


@router.delete("/authors/{id}", tags=["authors"])
def delete_article(id: str, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    delete_citation_by_author(id)
    id = ObjectId(id)
    storage.authors_storage.delete_author(id)


@router.get("/stats/authors/top", tags=["authors"], response_model=Authors)
def get_top(count: int, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    ids = citation_storage.get_top(count, UNIVERSAL_KEYWORD)
    authors = list(map(lambda x: storage.authors_storage.find_author(x['author']), ids))
    return Authors(authors=authors)
