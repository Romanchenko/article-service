from fastapi import FastAPI
from .routers import articles
from .routers import authors

app = FastAPI()
app.include_router(articles.router)
app.include_router(authors.router)


@app.get("/ping")
def pong():
    return {"ping": "pong!"}
