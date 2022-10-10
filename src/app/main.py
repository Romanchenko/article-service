from fastapi import FastAPI, HTTPException

from routers.errors import AuthError
from .routers import articles
from .routers import authors
from .routers import users

app = FastAPI()
app.include_router(articles.router)
app.include_router(authors.router)
app.include_router(users.router)


@app.get("/ping")
def pong():
    return {"ping": "pong!"}


@app.exception_handler(AuthError)
def auth_exception_handler(request, err):
    raise HTTPException(status_code=401, detail="Authentication error")
