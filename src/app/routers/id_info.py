from uuid import UUID

from pydantic import BaseModel


class IdInfo(BaseModel):
    id: UUID
