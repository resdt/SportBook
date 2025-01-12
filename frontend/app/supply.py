import pandas as pd
import streamlit as st

import utils.data_processing as data_proc


@st.cache_data(ttl=10 * 60 * 60, show_spinner=False)
def load_data():
    result = {}

    df_supply = pd.DataFrame(data_proc.load_api_data(url="admins/supply", method="get"))
    result["df_supply"] = df_supply

    return result


@st.fragment
def display_supply():
    df_supply = st.session_state.df_supply
    df_supply["price"] = df_supply["price"].astype(str)
    df_supply["provider_options"] = df_supply["provider_name"] + " | " + df_supply["price"]
    df_supply["price"] = df_supply["price"].astype(float)
    df_display = st.session_state.df_display

    col1, col2 = st.columns(2)
    with col1:
        product_name = st.selectbox(label="Выберите название товара", options=df_supply["name"].unique())
    with col2:
        quantity = st.number_input(label="Выберите количество товара", min_value=1)

    provider, price = st.selectbox("Выберите поставщика", options=df_supply["provider_options"]).split(" | ")
    price = float(price)

    if st.button("Добавить", use_container_width=True):
        new_row = pd.DataFrame({"Название товара": [product_name],
                                "Количество товара": [quantity],
                                "Поставщик": [provider],
                                "Цена": [price]})
        df_display = pd.concat([df_display, new_row], ignore_index=True)
        df_display.reset_index(drop=True, inplace=True)
        df_display.index += 1
        st.session_state.df_display = df_display

    if not df_display.empty:
        total_price = df_display["Цена"].sum()
        st.metric("Товаров на сумму: ", f"{total_price: .2f} ₽")
        st.dataframe(df_display, use_container_width=True)
        if st.button("Очистить"):
            df_display = pd.DataFrame()
            st.rerun()


def display():
    st.title("Планирование закупок")
    data_dict = load_data()

    df_supply = data_dict["df_supply"]

    st.session_state.df_supply = df_supply
    st.session_state.df_display = pd.DataFrame(columns=["Название товара", "Количество товара", "Поставщик", "Цена"])
    display_supply()


display()
