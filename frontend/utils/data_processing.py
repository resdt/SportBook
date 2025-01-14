import os
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL")


def load_api_data(url: str, method: str, json: dict = {}):
    with st.spinner("Пожалуйста, подождите... данные обновляются."):
        try:
            if method == "post":
                response = (requests.post(f"{API_BASE_URL}/{url}", json=json) if json
                            else requests.post(f"{API_BASE_URL}/{url}"))
                response.raise_for_status()
                data = response.json()
                return data
            elif method == "get":
                response = requests.get(f"{API_BASE_URL}/{url}")
                response.raise_for_status()
                data = response.json()
                return data
            elif method == "put":
                response = (requests.put(f"{API_BASE_URL}/{url}", json=json) if json
                            else requests.put(f"{API_BASE_URL}/{url}"))
                response.raise_for_status()
                data = response.json()
                return data
        except Exception as e:
            print(e)
            st.error("Ошибка подключения к серверу")
            st.stop()
