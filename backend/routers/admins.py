from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import utils.connections as conn


router = APIRouter()


class AddUserRequest(BaseModel):
    login: str
    hashed_password: str
    user_type: str


@router.post("/add_user")
async def add_user(credentials: AddUserRequest):
    query = """
INSERT INTO users (login, hashed_password, user_type)
VALUES ($1, $2, $3);
    """
    await conn.execute_query(query, credentials.login, credentials.hashed_password, credentials.user_type)


@router.get("/get_items")
async def get_items():
    query = """
SELECT *
FROM items;
"""
    result = await conn.execute_query(query)

    if not result:
        raise HTTPException(status_code=404, detail="Предметы не найдены")

    return result


class AddInventoryItem(BaseModel):
    item_id: int
    quantity: int


@router.post("/inventory/extend")
async def add_inventory_item(data: AddInventoryItem):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Количество должно быть больше нуля")

    # Проверяем, есть ли запись с этим item_id и status = 'новый'
    check_query = """
SELECT id, quantity
FROM inventory
WHERE item_id = $1 AND status = 'новый';
    """
    existing_item = await conn.execute_query(check_query, data.item_id)

    if existing_item:
        # Если запись существует, увеличиваем quantity
        update_query = """
UPDATE inventory
SET quantity = quantity + $1
WHERE id = $2;
        """
        await conn.execute_query(update_query, data.quantity, existing_item[0]["id"])
        return {"message": f"Количество обновлено, теперь {existing_item[0]['quantity'] + data.quantity}"}
    else:
        # Если записи нет, создаём новую
        insert_query = """
INSERT INTO inventory (item_id, quantity, status)
VALUES ($1, $2, 'новый')
RETURNING id, item_id, quantity, status;
        """
        new_item = await conn.execute_query(insert_query, data.item_id, data.quantity)
        return {"message": "Новая позиция добавлена", "data": new_item[0]}


class EditInventoryStatus(BaseModel):
    inventory_id: int
    new_quantity: int
    new_status: str


@router.put("/inventory/edit_status")
async def edit_inventory_status(data: EditInventoryStatus):
    # Проверяем валидность нового статуса
    valid_statuses = ["новый", "используемый", "сломанный"]
    if data.new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Недопустимый статус")

    # Получаем текущую запись из инвентаря
    select_query = """
SELECT item_id, quantity, status
FROM inventory
WHERE id = $1;
    """
    current_item = await conn.execute_query(select_query, data.inventory_id)

    if not current_item:
        raise HTTPException(status_code=404, detail="Предмет в инвентаре не найден")

    current_item = current_item[0]  # Извлекаем единственную запись
    current_quantity = current_item["quantity"]
    current_status = current_item["status"]

    # Проверяем количество
    if data.new_quantity > current_quantity:
        raise HTTPException(status_code=400, detail="Невозможно увеличить количество больше текущего")

    # Уменьшаем количество в текущей записи
    update_query = """
UPDATE inventory
SET quantity = quantity - $1
WHERE id = $2;
    """
    await conn.execute_query(update_query, data.new_quantity, data.inventory_id)

    # Если количество стало 0, удаляем запись
    if data.new_quantity == current_quantity:
        delete_query = "DELETE FROM inventory WHERE id = $1;"
        await conn.execute_query(delete_query, data.inventory_id)

    # Добавляем или обновляем запись с новым статусом
    insert_query = """
INSERT INTO inventory (item_id, quantity, status)
VALUES ($1, $2, $3)
ON CONFLICT (item_id, status)
DO UPDATE SET quantity = inventory.quantity + $2;
    """
    await conn.execute_query(insert_query, current_item["item_id"], data.new_quantity, data.new_status)

    return {"message": "Инвентарь успешно обновлен"}


class UpdateInventoryQuantity(BaseModel):
    inventory_id: int
    new_quantity: int


@router.put("/inventory/edit_quantity")
async def update_inventory_quantity(data: UpdateInventoryQuantity):
    # Проверяем, что новое количество не отрицательное
    if data.new_quantity < 0:
        raise HTTPException(status_code=400, detail="Количество не может быть отрицательным")

    # Получаем текущую запись из инвентаря
    select_query = """
SELECT quantity
FROM inventory
WHERE id = $1;
    """
    current_item = await conn.execute_query(select_query, data.inventory_id)

    if not current_item:
        raise HTTPException(status_code=404, detail="Предмет в инвентаре не найден")

    current_quantity = current_item[0]["quantity"]

    # Проверяем, что новое количество меньше или равно текущему
    if data.new_quantity > current_quantity:
        raise HTTPException(status_code=400, detail="Новое количество не может быть больше текущего")

    # Если новое количество равно 0, удаляем запись
    if data.new_quantity == 0:
        delete_query = "DELETE FROM inventory WHERE id = $1;"
        await conn.execute_query(delete_query, data.inventory_id)
        return {"message": "Запись успешно удалена"}

    # Обновляем количество
    update_query = """
UPDATE inventory
SET quantity = $1
WHERE id = $2;
    """
    await conn.execute_query(update_query, data.new_quantity, data.inventory_id)
    return {"message": f"Количество обновлено до {data.new_quantity}"}


@router.get("/get_users")
async def get_usernames():
    query = """
SELECT id, login
FROM users;
    """
    result = await conn.execute_query(query)
    return result


@router.get("/get_user_inventory")
async def get_user_inventory():
    query = """
SELECT ui.id AS id,
       i.id AS item_id,
       u.login AS login,
       i.name AS item_name,
       ui.quantity,
       ui.status
FROM user_inventory AS ui
LEFT JOIN users AS u ON ui.user_id = u.id
LEFT JOIN items AS i ON ui.item_id = i.id;
    """
    result = await conn.execute_query(query)
    return result


class AssignInventory(BaseModel):
    inventory_id: int
    user_id: int
    quantity: int


@router.post("/inventory/assign")
async def assign_inventory(data: AssignInventory):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Количество должно быть больше нуля")

    # Получаем текущую запись из инвентаря
    select_query = """
SELECT item_id, quantity, status
FROM inventory
WHERE id = $1;
    """
    current_item = await conn.execute_query(select_query, data.inventory_id)

    if not current_item:
        raise HTTPException(status_code=404, detail="Предмет в инвентаре не найден")

    current_item = current_item[0]  # Извлекаем единственную запись
    current_quantity = current_item["quantity"]

    # Проверяем, достаточно ли количества
    if data.quantity > current_quantity:
        raise HTTPException(status_code=400, detail="Недостаточно доступного инвентаря")

    # Уменьшаем количество в inventory или удаляем запись
    if data.quantity == current_quantity:
        delete_query = "DELETE FROM inventory WHERE id = $1;"
        await conn.execute_query(delete_query, data.inventory_id)
    else:
        update_query = """
UPDATE inventory
SET quantity = quantity - $1
WHERE id = $2;
        """
        await conn.execute_query(update_query, data.quantity, data.inventory_id)

    # Обновляем или создаем запись в user_inventory
    insert_query = """
INSERT INTO user_inventory (user_id, item_id, quantity, status)
VALUES ($1, $2, $3, $4)
ON CONFLICT (user_id, item_id, status)
DO UPDATE SET quantity = user_inventory.quantity + $3;
    """
    await conn.execute_query(
        insert_query,
        data.user_id,
        current_item["item_id"],
        data.quantity,
        current_item["status"]
    )

    return {"message": "Инвентарь успешно закреплен за пользователем"}


@router.get("/requests/get")
async def get_requests():
    query = """
SELECT r.id,
       u.login,
       i.name AS item_name,
       r.request_type,
       r.quantity,
       r.status,
       r.created_at,
       r.updated_at
FROM requests AS r
LEFT JOIN users AS u ON r.user_id = u.id
LEFT JOIN items AS i ON r.item_id = i.id;
    """
    result = await conn.execute_query(query)
    return result


async def process_get_request(request):
    # Проверяем остаток в inventory
    select_inventory_query = """
SELECT id, quantity
FROM inventory
WHERE item_id = $1 AND status = 'новый';
    """
    inventory = await conn.execute_query(select_inventory_query, request["item_id"])

    if not inventory or inventory[0]["quantity"] < request["quantity"]:
        raise HTTPException(status_code=400, detail="Недостаточно доступного инвентаря")

    # Уменьшаем количество в inventory
    if inventory[0]["quantity"] == request["quantity"]:
        delete_query = "DELETE FROM inventory WHERE id = $1;"
        await conn.execute_query(delete_query, inventory[0]["id"])
    else:
        update_inventory_query = """
UPDATE inventory
SET quantity = quantity - $1
WHERE id = $2;
        """
        await conn.execute_query(update_inventory_query, request["quantity"], inventory[0]["id"])

    # Добавляем предмет пользователю
    insert_user_inventory_query = """
INSERT INTO user_inventory (user_id, item_id, quantity, status)
VALUES ($1, $2, $3, 'новый')
ON CONFLICT (user_id, item_id, status)
DO UPDATE SET quantity = user_inventory.quantity + $3;
    """
    await conn.execute_query(insert_user_inventory_query, request["user_id"], request["item_id"], request["quantity"])


async def process_repair_request(request):
    # Проверяем, есть ли сломанные предметы у пользователя
    select_user_inventory_query = """
SELECT quantity
FROM user_inventory
WHERE user_id = $1 AND item_id = $2 AND status = 'сломанный';
    """
    user_inventory = await conn.execute_query(select_user_inventory_query, request["user_id"], request["item_id"])

    if not user_inventory or user_inventory[0]["quantity"] < request["quantity"]:
        raise HTTPException(status_code=400, detail="Недостаточно сломанных предметов для ремонта")

    # Уменьшаем количество сломанных предметов
    update_user_inventory_query = """
UPDATE user_inventory
SET quantity = quantity - $1
WHERE user_id = $2 AND item_id = $3 AND status = 'сломанный';
    """
    await conn.execute_query(update_user_inventory_query, request["quantity"], request["user_id"], request["item_id"])

    # Увеличиваем количество используемых предметов
    insert_used_inventory_query = """
INSERT INTO user_inventory (user_id, item_id, quantity, status)
VALUES ($1, $2, $3, 'используемый')
ON CONFLICT (user_id, item_id, status)
DO UPDATE SET quantity = user_inventory.quantity + $3;
    """
    await conn.execute_query(insert_used_inventory_query, request["user_id"], request["item_id"], request["quantity"])


async def process_replace_request(request):
    # Проверяем, есть ли сломанные предметы у пользователя
    select_user_inventory_query = """
SELECT quantity
FROM user_inventory
WHERE user_id = $1 AND item_id = $2 AND status = 'сломанный';
    """
    user_inventory = await conn.execute_query(select_user_inventory_query, request["user_id"], request["item_id"])

    if not user_inventory or user_inventory[0]["quantity"] < request["quantity"]:
        raise HTTPException(status_code=400, detail="Недостаточно сломанных предметов для замены")

    # Уменьшаем количество сломанных предметов у пользователя
    update_user_inventory_query = """
UPDATE user_inventory
SET quantity = quantity - $1
WHERE user_id = $2 AND item_id = $3 AND status = 'сломанный';
    """
    await conn.execute_query(update_user_inventory_query, request["quantity"], request["user_id"], request["item_id"])

    # Добавляем сломанные предметы в inventory
    insert_inventory_query = """
INSERT INTO inventory (item_id, quantity, status)
VALUES ($1, $2, 'сломанный')
ON CONFLICT (item_id, status)
DO UPDATE SET quantity = inventory.quantity + $2;
    """
    await conn.execute_query(insert_inventory_query, request["item_id"], request["quantity"])

    # Проверяем, достаточно ли нового/используемого инвентаря
    select_new_inventory_query = """
SELECT id, quantity
FROM inventory
WHERE item_id = $1 AND status IN ('новый', 'используемый')
ORDER BY status = 'новый' DESC LIMIT 1;
    """
    inventory = await conn.execute_query(select_new_inventory_query, request["item_id"])

    if not inventory or inventory[0]["quantity"] < request["quantity"]:
        raise HTTPException(status_code=400, detail="Недостаточно нового/используемого инвентаря")

    # Уменьшаем количество в inventory
    update_inventory_query = """
UPDATE inventory
SET quantity = quantity - $1
WHERE id = $2;
    """
    await conn.execute_query(update_inventory_query, request["quantity"], inventory[0]["id"])

    # Увеличиваем количество нового/используемого у пользователя
    insert_user_inventory_query = """
INSERT INTO user_inventory (user_id, item_id, quantity, status)
VALUES ($1, $2, $3, 'новый')
ON CONFLICT (user_id, item_id, status)
DO UPDATE SET quantity = user_inventory.quantity + $3;
    """
    await conn.execute_query(insert_user_inventory_query, request["user_id"], request["item_id"], request["quantity"])


class ProcessRequest(BaseModel):
    request_id: int
    response: str


@router.post("/requests/process")
async def process_request(data: ProcessRequest):
    # Проверяем валидность отклика
    if data.response not in ["одобрено", "отклонено"]:
        raise HTTPException(status_code=400, detail="Недопустимый отклик")
    # Получаем информацию о заявке
    select_query = """
SELECT user_id, item_id, request_type, quantity, status
FROM requests
WHERE id = $1;
    """
    request = await conn.execute_query(select_query, data.request_id)

    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    request = request[0]  # Извлекаем единственную запись

    # Если заявка уже обработана
    if request["status"] in ["одобрено", "отклонено"]:
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    # Если заявка отклонена
    if data.response == "отклонено":
        # Обновляем статус заявки
        update_query = """
UPDATE requests
SET status = 'отклонено', updated_at = CURRENT_TIMESTAMP
WHERE id = $1;
        """
        await conn.execute_query(update_query, data.request_id)
        return {"message": "Заявка отклонена"}

    # Если заявка одобрена, выполняем соответствующую логику
    if request["request_type"] == "получить":
        await process_get_request(request)
    elif request["request_type"] == "отремонтировать":
        await process_repair_request(request)
    elif request["request_type"] == "заменить":
        await process_replace_request(request)
    else:
        raise HTTPException(status_code=400, detail="Неизвестный тип заявки")

    # Обновляем статус заявки на "одобрено"
    update_query = """
UPDATE requests
SET status = 'одобрено', updated_at = CURRENT_TIMESTAMP
WHERE id = $1;
    """
    await conn.execute_query(update_query, data.request_id)

    return {"message": "Заявка успешно обработана"}


@router.get("/supply")
async def get_supply():
    query = """
SELECT *
FROM provider_items AS pi
LEFT JOIN items AS i ON pi.item_id = i.id;
    """
    result = await conn.execute_query(query)
    return result
