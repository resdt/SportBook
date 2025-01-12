import requests
import streamlit as st

import envars


def load_api_data(url: str, json: dict = {}, method: str = "post"):
    with st.spinner("Пожалуйста, подождите... данные обновляются."):
        try:
            if method == "post":
                response = (requests.post(f"{envars.API_BASE_URL}/{url}", json=json) if json
                            else requests.post(f"{envars.API_BASE_URL}/{url}"))
                response.raise_for_status()
                data = response.json()
                return data
            elif method == "get":
                response = requests.get(f"{envars.API_BASE_URL}/{url}")
                response.raise_for_status()
                data = response.json()
                return data
            elif method == "put":
                response = (requests.put(f"{envars.API_BASE_URL}/{url}", json=json) if json
                            else requests.put(f"{envars.API_BASE_URL}/{url}"))
                response.raise_for_status()
                data = response.json()
                return data
        except Exception as e:
            print(e)
            st.error("Ошибка подключения к серверу")
            st.stop()
