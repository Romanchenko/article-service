from copy import deepcopy
from datetime import datetime
import uuid
from typing import List, Dict
from pydantic import BaseModel, Field
from bson.objectid import ObjectId


ID_FIELD = '_id'


class Article(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId)
    title: str
    authors: List[ObjectId] = []
    abstract: str = None
    conference: str = None
    year: int
    references: List[ObjectId] = []
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)
    doi: str = None
    fos: str = None
    isbn: str = None
    issn: str = None
    issue: str = None
    keywords: List[str] = []
    lang: str = None
    n_citation: float = None
    page_end: float = None
    page_start: float = None
    pdf: str = None
    url: str = None
    venue_id: ObjectId
    venue_name: str


    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d
