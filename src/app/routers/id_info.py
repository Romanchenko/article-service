from bson import ObjectId
from pydantic import BaseModel


class IdInfo(BaseModel):
    id: str

    class Config:
        arbitrary_types_allowed = True


class TokenInfo(BaseModel):
    token: str

    class Config:
        arbitrary_types_allowed = True
