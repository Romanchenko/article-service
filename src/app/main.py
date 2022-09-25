from fastapi import FastAPI
from .routers import articles

app = FastAPI()
app.include_router(articles.router)


@app.get("/ping")
def pong():
    return {"ping": "pong!"}
