import time

import pandas as pd
import streamlit as st

import utils.data_processing as data_proc


@st.cache_data(ttl=10 * 60, show_spinner=False)
def load_data(user_id):
    result = {}

    df_user_inventory = pd.DataFrame(data_proc.load_api_data(url=f"users/{user_id}/inventory", method="get"))
    result["df_user_inventory"] = df_user_inventory

    try:
        df_user_requests = pd.DataFrame(data_proc.load_api_data(url=f"users/{user_id}/requests/show", method="get"))
    except Exception as e:
        print(e)
        df_user_requests = pd.DataFrame()
    result["df_user_requests"] = df_user_requests

    df_inventory = pd.DataFrame(data_proc.load_api_data(url="app/inventory", method="get"))
    result["df_inventory"] = df_inventory

    return result


@st.fragment
def show_user_inventory(src_df):
    df_user_inventory = src_df.copy()
    df_user_inventory.index += 1
    st.dataframe(df_user_inventory.drop(columns=["id", "item_id"]), use_container_width=True)


@st.fragment
def show_user_requests(src_df):
    df_user_requests = src_df.copy()
    df_user_requests.index += 1
    df_user_requests.drop(columns=["id", "user_id", "item_id"], inplace=True)
    df_user_requests = df_user_requests[["name", "request_type", "quantity", "status", "created_at", "updated_at"]]
    df_user_requests["created_at"] = pd.to_datetime(df_user_requests["created_at"], format="ISO8601")
    df_user_requests["updated_at"] = pd.to_datetime(df_user_requests["updated_at"], format="ISO8601")
    st.dataframe(df_user_requests, use_container_width=True)


@st.dialog("Создать заявку")
def create_request(df_src_inventory, df_src_user_inventory):
    df_user_inventory = df_src_user_inventory.copy()
    df_inventory = df_src_inventory.copy().rename(columns={"name": "item_name"})

    action = st.selectbox(label="Что Вы хотите сделать?", options=["получить", "отремонтировать", "заменить"], index=None)
    df = (pd.DataFrame() if not action else
          df_inventory if action == "получить" else
          df_user_inventory[df_user_inventory["status"] == "сломанный"])
    item_id = 0
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            item_list = df["item_name"].values
            item = st.selectbox("Выберите предмет", options=item_list)
            if item:
                item_id = df[df["item_name"] == item]["item_id"].values[0]
                item_id = int(item_id)
        with col2:
            max_val = df[df["item_name"] == item]["quantity"].values[0] if item else None
            quantity = st.number_input(label="Введите количество", min_value=1, max_value=max_val)

        if st.button("Подтвердить", type="primary", use_container_width=True):
            if all([action,
                    item_id,
                    quantity]):
                try:
                    user_id = st.session_state.user_id
                    json = {"action": action, "item_id": item_id, "quantity": quantity}
                    data_proc.load_api_data(url=f"users/{user_id}/requests/make", method="post", json=json)
                    load_data.clear()
                    st.success("Заявка успешно создана")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    print(e)
                    st.error("Ошибка создания заявки")


def display():
    st.title("Инвентарь")
    user_id = st.session_state.user_id
    data_dict = load_data(user_id)
    df_user_inventory = data_dict["df_user_inventory"]
    df_user_requests = data_dict["df_user_requests"]
    df_inventory = data_dict["df_inventory"]

    st.header("Просмотр состояния инвентаря")
    show_user_inventory(df_user_inventory)

    st.header("Мои заявки")
    if not df_user_requests.empty:
        show_user_requests(df_user_requests)
    if st.button("Создать заявку на изменение"):
        create_request(df_inventory, df_user_inventory)


display()
