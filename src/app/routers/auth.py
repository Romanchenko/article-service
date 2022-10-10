from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer

from models.user import UserCredentials, User
from .errors import AuthError
from .id_info import TokenInfo
from ..storage import users_storage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

@router.post("/login", tags=["authentication"], response_model=TokenInfo)
def get_author(creds: UserCredentials):
    user = User(login=creds.login, password=creds.password)
    user_found = users_storage.find_by_login_and_password(user.login, user.password_hash)
    if user_found is None:
        raise AuthError()
    return user_found.user_token


def get_user(token: str):
    user = users_storage.find_by_token(token)
    if user is None:
        raise AuthError("No token found")
    if user.updated < datetime.utcnow() - timedelta(hours=2):
        raise AuthError("Token is expired")
    return user
