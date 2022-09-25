from copy import deepcopy
from datetime import datetime
import uuid
from typing import List, Dict
from pydantic import BaseModel, Field

ID_FIELD = '_id'


class Article(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    authors: List[uuid.UUID] = []
    abstract = ''
    conference = ''
    year: int
    references: List[uuid.UUID] = []
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d
