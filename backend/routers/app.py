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


@router.post("/check_username")
async def get_all_usernames(login: str):
    query = """
SELECT TRUE
FROM users
WHERE login = $1;
"""
    result = await conn.execute_query(query, login)
    return {"validity": not bool(result)}


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
        return {"success": False, "user_id": None, "user_type": None}

    return {"success": True, "user_id": result[0]["id"], "user_type": result[0]["user_type"]}


@router.get("/inventory")
async def get_inventory():
    query = """
SELECT inv.id AS id,
       it.id AS item_id,
       it.name AS item_name,
       quantity,
       status
FROM inventory AS inv
LEFT JOIN items AS it ON inv.item_id = it.id;
    """
    result = await conn.execute_query(query)

    if not result:
        raise HTTPException(status_code=401, detail="Ошибка при получении инвентаря")

    return result
