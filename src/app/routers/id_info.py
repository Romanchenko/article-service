from bson import ObjectId
from pydantic import BaseModel


class IdInfo(BaseModel):
    id: ObjectId
