import hashlib
import time

import streamlit as st

import utils.data_processing as data_proc


@st.fragment
def show_sign_up():
    def change_input_state():
        st.session_state.login_changed = True

    login = st.text_input("Введите имя пользователя", on_change=change_input_state).strip().lower()
    valid_login = st.session_state.valid_login
    if login and st.session_state.login_changed:
        st.session_state.login_changed = False
        data = data_proc.load_api_data(url=f"app/check_username?login={login}", method="post")
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
                data_proc.load_api_data(url="admins/add_user", method="post", json=json)
                st.success("Вы успешно добавили пользователя")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                print(e)
                st.error("Ошибка добавления пользователя")
        else:
            st.error("Не все поля заполнены")


def display():
    st.title("Управление пользователями")
    st.session_state.login_changed = False
    st.session_state.valid_login = False
    show_sign_up()


display()
