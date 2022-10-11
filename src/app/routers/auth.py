from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .errors import AuthError
from .id_info import TokenInfo
from ..storage import users_storage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

@router.post("/login", tags=["authentication"], response_model=TokenInfo)
def get_author(creds: OAuth2PasswordRequestForm = Depends()):
    from ..models.user import User
    user = User(login=creds.username, password=creds.password)
    user_found = users_storage.find_by_login_and_password(user.login, user.password_hash)
    print(user_found)
    if user_found is None:
        raise AuthError()
    return TokenInfo(access_token=str(user_found.user_token))


def get_user(token: str):
    user = users_storage.find_by_token(token)
    print(f'token is {token}')

    if user is None:
        raise AuthError("No token found")
    if user.updated < datetime.utcnow() - timedelta(hours=2):
        raise AuthError("Token is expired")
    return user
