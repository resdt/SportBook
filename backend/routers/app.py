from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import utils.connections as conn


router = APIRouter()


class SignUpRequest(BaseModel):
    login: str
    hashed_password: str


@router.post("/sign_up")
async def add_user(credentials: SignUpRequest):
    query = """
INSERT INTO users (login, hashed_password, user_type)
VALUES ($1, $2, 'user');
    """
    await conn.execute_query(query, credentials.login, credentials.hashed_password)


class LoginRequest(BaseModel):
    login: str
    hashed_password: str


@router.post("/login")
async def login_user(credentials: LoginRequest):
    query = """
SELECT id, user_type
FROM users
WHERE login = $1 AND hashed_password = $2;
    """
    result = await conn.execute_query(query, credentials.login, credentials.hashed_password)

    if not result:
        raise HTTPException(status_code=401, detail="Неверные логин или пароль")

    return {"user_id": result[0]["id"], "user_type": result[0]["user_type"]}


@router.get("/inventory")
async def get_inventory():
    query = """
SELECT *
FROM inventory;
    """
    result = await conn.execute_query(query)

    if not result:
        raise HTTPException(status_code=401, detail="Ошибка при получении инвентаря")

    return result
