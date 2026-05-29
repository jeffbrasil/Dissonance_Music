from fastapi import FastAPI

from app.api.endpoints import user_router

app = FastAPI()


app.include_router(user_router.router, prefix="/user", tags=["Usuario"])
