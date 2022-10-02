import datetime
from copy import deepcopy

from bson import ObjectId
from pydantic import BaseModel, Field


class Author(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId)
    name: str
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d