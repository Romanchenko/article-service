from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


from .routers.errors import AuthError
from .routers import articles
from .routers import authors
from .routers import users
from .routers import auth

app = FastAPI()
app.include_router(articles.router)
app.include_router(authors.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/ping")
def pong():
    return {"ping": "pong!"}


@app.exception_handler(AuthError)
def auth_exception_handler(request, err: AuthError):
    print(err.message)
    return JSONResponse(status_code=401, content={"message" : f"Authentication error: {err.message}"})
