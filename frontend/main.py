import streamlit as st


def main():
    if "login" not in st.session_state:
        st.session_state.login = False

    is_logged_in = st.session_state.login
    pages = {}
    if not is_logged_in:
        pages = [st.Page("app/login.py", title="Авторизация", icon=":material/login:")]
    else:
        user_type = st.session_state.user_type
        pages.update({"": [st.Page("app/home.py", title="Главная страница", icon=":material/home:"),
                           st.Page("app/logout.py", title="Выйти", icon=":material/logout:")]})
        if user_type == "admin":
            pages.update({"Администратор": [st.Page("app/user_management.py", title="Управление пользователями", icon=":material/manage_accounts:"),
                                            st.Page("app/inventory_management.py", title="Управление инвентарем", icon=":material/inventory:"),
                                            st.Page("app/request_processing.py", title="Заявки", icon=":material/request_quote:"),
                                            st.Page("app/supply.py", title="Закупки", icon=":material/forklift:")],
                          "Панель управления": [st.Page("app/user_inventory.py", title="Мой инвентарь", icon=":material/inventory_2:")]})
        elif user_type == "user":
            pages.update({"Панель управления": [st.Page("app/user_inventory.py", title="Мой инвентарь", icon=":material/inventory_2:")]})
    display_pages = st.navigation(pages)
    display_pages.run()


if __name__ == "__main__":
    main()
