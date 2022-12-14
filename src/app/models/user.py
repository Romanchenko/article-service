from copy import deepcopy
from datetime import datetime
import hashlib
import uuid
from typing import Dict

from bson import ObjectId
from pydantic import BaseModel, Field, BaseConfig

from .py_objectid import PyObjectId


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    login: str
    password_hash: str
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)
    user_token: PyObjectId = Field(default_factory=PyObjectId)

    def __init__(self, **kwargs):
        if "password" in kwargs:
            password = kwargs.pop("password")
            kwargs["password_hash"] = hashlib.md5(password.encode('utf-8')).hexdigest()
        super().__init__(**kwargs)

    def serialize(self) -> Dict:
        d = deepcopy(self.__dict__)
        d['_id'] = d.pop('id')
        return d

    class Config:
        BaseConfig.arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

