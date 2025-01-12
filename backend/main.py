from fastapi import FastAPI
from routers import users, app, admins


api = FastAPI()

api.include_router(app.router, prefix="/api/v1/app")
api.include_router(users.router, prefix="/api/v1/users")
api.include_router(admins.router, prefix="/api/v1/admins")


@api.get("/")
async def root():
    return {"message": "Server is running. Welcome!"}
