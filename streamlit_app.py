import sys
import subprocess
import importlib
import os
import site

# Проверяем и устанавливаем зависимости с правами пользователя
def install_packages():
    packages = ['flask', 'streamlit']
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"Устанавливаем {package}...")
            try:
                # Пробуем установить в виртуальное окружение
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except:
                # Если не получилось, устанавливаем для текущего пользователя
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
                
                # Добавляем пользовательские site-packages в путь
                user_site = site.getusersitepackages()
                if user_site not in sys.path:
                    sys.path.append(user_site)

# Вызываем функцию установки
install_packages()

# Теперь безопасно импортируем остальные модули
from flask import Flask, render_template, request, jsonify, redirect, url_for
from uuid import uuid4
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from threading import Thread
import time

# Создаем Flask-приложение
flask_app = Flask(__name__)

# Временное хранилище данных
groups = {}
expenses = {}
members = {}

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/create_group', methods=['POST'])
def create_group():
    data = request.get_json()
    group_name = data['groupName']
    
    group_id = str(uuid4())
    groups[group_id] = {
        'name': group_name,
        'created_at': datetime.now()
    }
    expenses[group_id] = []
    members[group_id] = []
    
    return jsonify(group_id)

@flask_app.route('/group/<group_id>')
def group_page(group_id):
    group = groups.get(group_id)
    if not group:
        return "Группа не найдена", 404
    
    return render_template(
        'group.html',
        group=group,
        group_id=group_id,
        expenses=expenses[group_id],
        members=members[group_id]
    )

@flask_app.route('/get_group_data/<group_id>')
def get_group_data(group_id):
    group = groups.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    return jsonify({
        "name": group['name'],
        "members": members.get(group_id, []),
        "expenses": expenses.get(group_id, [])
    })

@flask_app.route('/add_expense/<group_id>', methods=['POST'])
def add_expense(group_id):
    data = request.get_json()
    new_expense = {
        'id': str(uuid4()),
        'description': data['description'],
        'amount': float(data['amount']),
        'payer': data['payer'],
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    if group_id in expenses:
        expenses[group_id].append(new_expense)
    else:
        expenses[group_id] = [new_expense]
    
    return jsonify(success=True)

@flask_app.route('/delete_member/<group_id>', methods=['POST'])
def delete_member(group_id):
    data = request.get_json()
    member_name = data['name']
    
    if group_id in members and member_name in members[group_id]:
        members[group_id].remove(member_name)
        expenses[group_id] = [e for e in expenses[group_id] if e['payer'] != member_name]
        return jsonify(success=True)
    return jsonify(success=False), 400

@flask_app.route('/join/<group_id>')
def join_group(group_id):
    group = groups.get(group_id)
    if not group:
        return "Группа не найдена", 404
    return redirect(url_for('group_page', group_id=group_id))

@flask_app.route('/add_member/<group_id>', methods=['POST'])
def add_member(group_id):
    data = request.get_json()
    member_name = data['name']
    
    if group_id in members:
        members[group_id].append(member_name)
    else:
        members[group_id] = [member_name]
    
    return jsonify(success=True)

# Запускаем Flask в отдельном потоке
def run_flask():
    flask_app.run(port=5000, debug=False, use_reloader=False, threaded=True)

# Создаем и запускаем поток Flask
if not hasattr(st, 'flask_thread'):
    st.flask_thread = Thread(target=run_flask, daemon=True)
    st.flask_thread.start()
    time.sleep(3)  # Даем больше времени на запуск сервера

# Streamlit интерфейс
st.title("Splitwise Clone")
components.iframe("http://localhost:5000", height=700)
