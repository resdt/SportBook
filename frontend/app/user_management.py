import hashlib
import time

import requests
import streamlit as st

import envars
import utils.data_processing as data_proc


def change_username_input_state():
    if "login_changed" not in st.session_state:
        st.session_state.login_changed = True
    else:
        st.session_state.login_changed = not st.session_state.login_changed


@st.fragment
def show_sign_up():
    login = st.text_input("Введите имя пользователя", on_change=change_username_input_state)
    valid_login = st.session_state.valid_login
    if login and st.session_state.login_changed:
        change_username_input_state()
        response = requests.post(f"{envars.API_BASE_URL}/app/check_username?login={login}")
        data = response.json()
        valid_login = data["validity"]
        st.session_state.valid_login = valid_login
    if not valid_login and login:
        st.error("Имя пользователя уже используется")
    password = st.text_input("Введите пароль")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user_type = st.selectbox(label="Выберите тип пользователя", options=["user", "admin"])

    if st.button("Подтвердить", type="primary", use_container_width=True):
        if all([login,
                password,
                hashed_password,
                valid_login,
                user_type]):
            try:
                json = {"login": login, "hashed_password": hashed_password, "user_type": user_type}
                data_proc.load_api_data(url="admins/add_user", json=json)
                st.success("Вы успешно добавили пользователя")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка добавления пользователя")
        else:
            st.error("Не все поля запонены")


def display():
    st.title("Управление пользователями")
    st.session_state.login_changed = True
    st.session_state.valid_login = False
    show_sign_up()


display()
