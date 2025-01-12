from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import utils.connections as conn


router = APIRouter()


@router.get("/{user_id}/inventory")
async def get_user_inventory(user_id: int):
    query = """
    SELECT
        ui.id,
        ui.item_id,
        i.name AS item_name,
        ui.status,
        ui.quantity
    FROM user_inventory ui
    JOIN items i ON ui.item_id = i.id
    WHERE ui.user_id = $1;
    """
    result = await conn.execute_query(query, user_id)

    if not result:
        raise HTTPException(status_code=404, detail="Инвентарь для данного пользователя не найден")

    return result


class CreateRequest(BaseModel):
    action: str
    item_id: int
    quantity: int


@router.post("/{user_id}/requests/make")
async def create_request(user_id: int, request_data: CreateRequest):
    if request_data.action not in ["получить", "отремонтировать", "заменить"]:
        raise HTTPException(status_code=400, detail="Недопустимое действие")

    insert_query = """
INSERT INTO requests (user_id, item_id, request_type, quantity, status)
VALUES ($1, $2, $3, $4, 'на рассмотрении');
    """
    await conn.execute_query(insert_query,
                             user_id,
                             request_data.item_id,
                             request_data.action,
                             request_data.quantity)


@router.get("/{user_id}/requests/show")
async def get_requests(user_id: int):
    query = """
SELECT *
FROM requests
WHERE user_id = $1;
    """
    result = await conn.execute_query(query, user_id)

    if not result:
        raise HTTPException(status_code=404, detail="Заявки для данного пользователя не найдены")

    return result
