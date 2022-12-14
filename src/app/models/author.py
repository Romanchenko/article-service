from datetime import datetime
from copy import deepcopy
from typing import Dict, List

from bson import ObjectId
from pydantic import BaseModel, Field

from .py_objectid import PyObjectId


class Author(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class Authors(BaseModel):
    authors: List[Author]

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
