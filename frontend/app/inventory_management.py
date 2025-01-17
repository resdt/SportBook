import time

import pandas as pd
import streamlit as st

import utils.data_processing as data_proc


@st.cache_data(ttl=10 * 60, show_spinner=False)
def load_data():
    result = {}

    df_inventory = pd.DataFrame(data_proc.load_api_data(url="app/inventory", method="get"))
    result["df_inventory"] = df_inventory

    df_items = pd.DataFrame(data_proc.load_api_data(url="admins/get_items", method="get"))
    result["df_items"] = df_items

    df_usernames = pd.DataFrame(data_proc.load_api_data(url="admins/get_users", method="get"))
    result["df_usernames"] = df_usernames

    df_user_inventory = pd.DataFrame(data_proc.load_api_data(url="admins/get_user_inventory", method="get"))
    result["df_user_inventory"] = df_user_inventory

    return result


@st.fragment
def display_filter_block(src_df):
    df = src_df.copy()

    col1, col2 = st.columns(2)
    data_dict = {"item_name": {"col": col1, "title": "Название товара", "key": "item_name_inv"},
                 "status": {"col": col2, "title": "Состояние товара", "key": "status_inv"}}

    filter_dict = {}
    for f_key, f_val in data_dict.items():
        cur_filter_list = ["Все"] + sorted(filter(lambda x: x, df[f_key].unique()))
        selected_filter = f_val["col"].selectbox(f_val["title"],
                                                 cur_filter_list,
                                                 key=f_val["key"])

        if selected_filter != "Все":
            if f_key in df.columns:
                df = df[df[f_key] == selected_filter]
        filter_dict[f_key] = selected_filter

    df = df.sort_values(by=["item_name", "status"]).reset_index(drop=True)
    df.index +=1
    st.dataframe(df, use_container_width=True)


@st.fragment
def extend_inventory(src_df):
    with st.expander("Добавление позиций инвентаря"):
        df_items = src_df.copy()

        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Выберите название товара", options=df_items["name"])
            item_id = df_items[df_items["name"] == item]["id"].values[0]
            item_id = int(item_id)
        with col2:
            quantity = st.number_input("Введите количество товара", min_value=1)

        if st.button("Добавить", type="primary"):
            try:
                json = {"item_id": item_id, "quantity": quantity}
                data_proc.load_api_data(url="admins/inventory/extend", method="post", json=json)
                st.success("Предмет успешно добавлен в инвентарь")
                load_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка добавления предмета в инвентарь")


@st.fragment
def edit_inventory(src_df):
    with st.expander("Редактирование предметов в инвентаре"):
        df_inventory = src_df.copy().sort_values(by=["item_name", "status"])
        df_inventory["options"] = df_inventory["item_name"] + " | " + df_inventory["status"]

        item = st.selectbox("Выберите название товара", options=df_inventory["options"], key="item")
        name, status = item.split(" | ")
        inventory_id = df_inventory[(df_inventory["item_name"] == name)
                                    & (df_inventory["status"] == status)]["id"].values[0]
        inventory_id = int(inventory_id)

        new_status = st.selectbox("Выберите новое состояние товара", options=["новый", "используемый", "сломанный"], key="status")

        max_val = df_inventory[df_inventory["id"] == inventory_id]["quantity"].values[0]
        new_quantity = st.number_input("Введите количество товара для изменения", min_value=0, max_value=max_val)

        if st.button("Изменить статус", type="primary"):
            try:
                json = {"inventory_id": inventory_id, "new_quantity": new_quantity, "new_status": new_status}
                data_proc.load_api_data(url="admins/inventory/edit_status", method="put", json=json)
                st.success("Статус предметов успешно изменен")
                load_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка изменения статуса предмета")
        if st.button("Изменить количество", type="primary"):
            try:
                json = {"inventory_id": inventory_id, "new_quantity": new_quantity}
                data_proc.load_api_data(url="admins/inventory/edit_quantity", method="put", json=json)
                st.success("Количество предметов успешно изменено")
                load_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка изменения количества предметов")


@st.fragment
def assign_items(src_df_inventory, src_df_usernames):
    with st.expander("Закрепление инвентаря за пользователем"):
        df_inventory = src_df_inventory.copy().sort_values(by=["item_name", "status"])
        df_inventory["options"] = df_inventory["item_name"] + " | " + df_inventory["status"]
        df_usernames = src_df_usernames.copy()

        item = st.selectbox("Выберите название товара", options=df_inventory["options"])
        name, status = item.split(" | ")
        inventory_id = df_inventory[(df_inventory["item_name"] == name)
                                    & (df_inventory["status"] == status)]["id"].values[0]
        inventory_id = int(inventory_id)

        max_val = df_inventory[df_inventory["id"] == inventory_id]["quantity"].values[0]
        new_quantity = st.number_input("Введите количество товара для назначения", min_value=1, max_value=max_val)

        owner = st.selectbox("Выберите владельца инвентаря", options=df_usernames["login"])
        user_id = df_usernames[df_usernames["login"] == owner]["id"].values[0]
        user_id = int(user_id)

        if st.button("Назначить владельца", type="primary"):
            try:
                json = {"inventory_id": inventory_id, "quantity": new_quantity, "user_id": user_id}
                data_proc.load_api_data(url="admins/inventory/assign", method="post", json=json)
                st.success("Владелец успешно назначен")
                load_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка назначения владельца")


@st.fragment
def show_stats(src_df):
    df = src_df.copy()

    col1, col2 = st.columns(2)
    data_dict = {"login": {"col": col1, "title": "Имя пользователя", "key": "login_stats"},
                 "item_name": {"col": col2, "title": "Название товара", "key": "item_name_stats"},
                 "status": {"col": col1, "title": "Состояние товара", "key": "status_stats"}}

    filter_dict = {}
    for f_key, f_val in data_dict.items():
        cur_filter_list = ["Все"] + sorted(filter(lambda x: x, df[f_key].unique()))
        selected_filter = f_val["col"].selectbox(f_val["title"],
                                                 cur_filter_list,
                                                 key=f_val["key"])

        if selected_filter != "Все":
            if f_key in df.columns:
                df = df[df[f_key] == selected_filter]
        filter_dict[f_key] = selected_filter

    df = df.sort_values(by=["login", "item_name", "status"]).reset_index(drop=True)
    df.index +=1
    st.dataframe(df, use_container_width=True)


def display():
    st.title("Управление инвентарем")
    data_dict = load_data()

    df_inventory = data_dict["df_inventory"]
    df_items = data_dict["df_items"]
    df_usernames = data_dict["df_usernames"]
    df_user_inventory = data_dict["df_user_inventory"]

    display_filter_block(df_inventory.drop(columns=["id", "item_id"]))
    extend_inventory(df_items)
    edit_inventory(df_inventory)
    assign_items(df_inventory, df_usernames)

    st.header("Статистика использования")
    show_stats(df_user_inventory.drop(columns=["id", "item_id"]))


display()
