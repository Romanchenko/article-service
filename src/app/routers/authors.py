from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from ..models.citation import UNIVERSAL_KEYWORD
from .auth import oauth2_scheme, get_user
from .. import storage
from ..storage.authors_storage import insert_author, find_author, find_whole_authors_by_name
from ..service.citation_service import delete_citation_by_author
from ..service.recommendations import recommend
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

@router.get("/author", tags=["authors"], response_model=Author)
def get_author(name: str, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    result = find_whole_authors_by_name(name, full_math=True)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return result[0]


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
def get_top(count: int, keyword: Optional[str] = None, token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    if keyword is None:
        keyword = UNIVERSAL_KEYWORD
    ids = citation_storage.get_top(count, keyword)
    authors = list(map(lambda x: storage.authors_storage.find_author(x['author']), ids))
    return Authors(authors=authors)


@router.get("/stats/authors/rec", tags=["authors"], response_model=Authors)
def get_top(author_id: str, count: Optional[int], token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    recs = recommend(author_id, top=count)
    authors = list(map(lambda x: storage.authors_storage.find_author(ObjectId(x)), recs))
    return Authors(authors=authors)
