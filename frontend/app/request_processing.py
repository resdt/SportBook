import time

import pandas as pd
import streamlit as st

import utils.data_processing as data_proc


@st.cache_data(ttl=10 * 60, show_spinner=False)
def load_data():
    result = {}

    df_requests = pd.DataFrame(data_proc.load_api_data(url="admins/requests/get", method="get"))
    if not df_requests.empty:
        df_requests["created_at"] = pd.to_datetime(df_requests["created_at"], format="ISO8601")
        df_requests["updated_at"] = pd.to_datetime(df_requests["updated_at"], format="ISO8601")
    result["df_requests"] = df_requests

    return result


def show_filter_block(src_df):
    df = src_df.copy()

    col1, col2 = st.columns(2)
    data_dict = {"login": {"col": col1, "title": "Имя пользователя", "key": "login_reqs"},
                 "item_name": {"col": col2, "title": "Название товара", "key": "item_name_reqs"},
                 "request_type": {"col": col1, "title": "Тип заявки", "key": "request_type_reqs"},
                 "status": {"col": col2, "title": "Статус заявки", "key": "status_reqs"}}

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

    df = df.sort_values(by=["login", "status"]).reset_index(drop=True)
    df.index += 1
    st.dataframe(df, use_container_width=True)


@st.fragment
def process_requests(src_df_requests):
    with st.expander("Обработка заявок"):
        df_requests = src_df_requests.copy()
        df_requests = df_requests[df_requests["status"] == "на рассмотрении"]

        if df_requests.empty:
            return

        df_requests["quantity"] = df_requests["quantity"].astype(str)
        df_requests["options"] = (df_requests["login"] + " | "
                                  + df_requests["item_name"] + " | "
                                  + df_requests["request_type"] + " | "
                                  + df_requests["quantity"])
        df_requests["quantity"] = df_requests["quantity"].astype(int)

        request = st.selectbox("Выберите заявку", options=df_requests["options"])
        login, item_name, request_type, quantity = request.split(" | ")
        quantity = int(quantity)
        request_id = df_requests[(df_requests["login"] == login)
                                 & (df_requests["item_name"] == item_name)
                                 & (df_requests["request_type"] == request_type)
                                 & (df_requests["quantity"] == quantity)]["id"].values[0]
        request_id = int(request_id)

        action = None
        col1, col2, *_ = st.columns(5)
        with col1:
            if st.button("Отклонить"):
                action = "отклонено"
        with col2:
            if st.button("Одобрить"):
                action = "одобрено"
        if action is not None:
            try:
                json = {"request_id": request_id, "response": action}
                data_proc.load_api_data(url="admins/requests/process", method="post", json=json)
                st.success("Заявка успешно обработана")
                load_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка при обработке заявки")


def display():
    st.title("Заявки пользователей")
    data_dict = load_data()

    df_requests = data_dict["df_requests"]
    if not df_requests.empty:
        show_filter_block(df_requests.drop(columns="id"))
        process_requests(df_requests)


display()
