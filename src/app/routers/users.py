from uuid import UUID

from fastapi import APIRouter, HTTPException

from .id_info import IdInfo
from ..models.user import User
from ..storage import users_storage

router = APIRouter()


@router.get("/users/{user_id}", tags=["users"], response_model=User)
def get_user(user_id: UUID):
    user = users_storage.find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", tags=["users"])
def create_user(user: User):
    users_storage.insert_user(user)
    print(user.id)
    return IdInfo(id=str(user.id))


@router.delete("/users/{user_id}", tags=["users"])
def delete_user(user_id: UUID):
    users_storage.delete_user(user_id)


@router.post("/users/{user_id}", tags=["users"])
def update_user(id: UUID, user: User):
    if users_storage.find_user(id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    users_storage.update_user(user)
