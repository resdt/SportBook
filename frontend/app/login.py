import streamlit as st
import hashlib
import time

import utils.data_processing as data_proc


def change_input_state():
    if "login_changed" not in st.session_state:
        st.session_state.login_changed = True
    else:
        st.session_state.login_changed = not st.session_state.login_changed


@st.dialog("Регистрация")
def sign_up():
    login = st.text_input("Введите имя пользователя", on_change=change_input_state)
    if "valid_login" not in st.session_state:
        st.session_state.valid_login = False
    valid_login = st.session_state.valid_login

    if login and st.session_state.login_changed:
        change_input_state()
        data = data_proc.load_api_data(url=f"app/check_username?login={login}", method="post")
        valid_login = data["validity"]
        st.session_state.valid_login = valid_login
    if not valid_login and login:
        st.error("Имя пользователя уже используется")
    password = st.text_input("Введите пароль")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if st.button("Зарегистрироваться", use_container_width=True):
        if all([login,
                password,
                hashed_password,
                valid_login]):
            try:
                json = {"login": login, "hashed_password": hashed_password}
                data_proc.load_api_data(url="app/sign_up", method="post", json=json)
                st.success("Вы успешно зарегистрировались")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка добавления пользователя")
        else:
            st.error("Не все поля запонены")


def display():
    st.title("SportBook")
    with st.form("login_form"):
        username = st.text_input("Логин").strip().lower()
        password = st.text_input("Пароль", type="password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if st.form_submit_button("Войти"):
            json = {"login": username, "hashed_password": hashed_password}
            data = data_proc.load_api_data(url="app/login", method="post", json=json)

            if not data["success"]:
                st.error("Неправильный логин или пароль")
                st.stop()

            st.session_state.user_type = data["user_type"]
            st.session_state.user_id = data["user_id"]
            st.session_state.login = True
            st.rerun()
        st.form_submit_button("Зарегистрироваться", type="primary", on_click=sign_up)


display()
