from fastapi import FastAPI
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
