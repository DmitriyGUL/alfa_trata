from flask import Flask, render_template, request, jsonify, redirect, url_for
from uuid import uuid4
from datetime import datetime  

app = Flask(__name__)

# Временное хранилище данных (в реальном приложении используйте БД)
groups = {}
expenses = {}
members = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.get_json()
    group_name = data['groupName']
    
    # Создаем уникальный ID группы
    group_id = str(uuid4())
    
    # Сохраняем группу
    groups[group_id] = {
        'name': group_name,
        'created_at': datetime.now()
    }
    
    # Инициализируем хранилища для группы
    expenses[group_id] = []
    members[group_id] = []
    
    return jsonify(group_id)

@app.route('/group/<group_id>')
def group_page(group_id):
    # Получаем данные группы
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

# Добавляем новый endpoint для получения данных группы
@app.route('/get_group_data/<group_id>')
def get_group_data(group_id):
    group = groups.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    return jsonify({
        "name": group['name'],
        "members": members.get(group_id, []),
        "expenses": expenses.get(group_id, [])
    })

@app.route('/add_expense/<group_id>', methods=['POST'])
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

@app.route('/delete_member/<group_id>', methods=['POST'])
def delete_member(group_id):
    data = request.get_json()
    member_name = data['name']
    
    # Удаляем участника из группы
    if group_id in members and member_name in members[group_id]:
        members[group_id].remove(member_name)
        
        # Удаляем траты этого участника (в реальном приложении нужно аккуратнее)
        expenses[group_id] = [e for e in expenses[group_id] if e['payer'] != member_name]
        
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/join/<group_id>')
def join_group(group_id):
    group = groups.get(group_id)
    if not group:
        return "Группа не найдена", 404
    
    # В реальном приложении здесь должна быть логика добавления пользователя в группу
    return redirect(url_for('group_page', group_id=group_id))

@app.route('/add_member/<group_id>', methods=['POST'])
def add_member(group_id):
    data = request.get_json()
    member_name = data['name']
    
    if group_id in members:
        members[group_id].append(member_name)
    else:
        members[group_id] = [member_name]
    
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)  # Запуск приложения с включенным режимом отладки