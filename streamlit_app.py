# streamlit_app.py
import streamlit as st
import streamlit.components.v1 as components
from flask_app import app  # Импортируем Flask-приложение
from threading import Thread
import time

# Запускаем Flask в отдельном потоке
def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

# Старт Flask только один раз
if not hasattr(st, 'flask_thread'):
    st.flask_thread = Thread(target=run_flask, daemon=True)
    st.flask_thread.start()
    time.sleep(1)  # Даем время на запуск

# Встраиваем Flask-приложение через iframe
st.title("Splitwise Clone")
components.iframe("http://localhost:5000", height=800)
