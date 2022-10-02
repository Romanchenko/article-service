from copy import deepcopy
from datetime import datetime
import uuid
from typing import List, Dict
from pydantic import BaseModel, Field, validator, BaseConfig
from bson.objectid import ObjectId

from .py_objectid import PyObjectId

ID_FIELD = '_id'


class Article(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
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
    venue_id: ObjectId = None
    venue_name: str = None

    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d

    class Config:
        BaseConfig.arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
