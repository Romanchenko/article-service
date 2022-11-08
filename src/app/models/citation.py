from copy import deepcopy
from dataclasses import dataclass
from typing import Dict

from bson import ObjectId
from pydantic import Field, BaseModel, BaseConfig

from .py_objectid import PyObjectId

UNIVERSAL_KEYWORD = "__ALL__"


@dataclass
class Citation(BaseModel):
    author: PyObjectId
    score: int
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    keyword: str = Field(default=UNIVERSAL_KEYWORD)

    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d

    class Config:
        BaseConfig.arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
