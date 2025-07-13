from flask import Flask, request, jsonify
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DB_PATH = '/tmp/users.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            gender TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            goal TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 💥 ВЫЗЫВАЕМ init_db ПРИ КАЖДОМ ЗАПУСКЕ, НЕ ТОЛЬКО ЛОКАЛЬНО
init_db()

@app.route('/get_profile')
def get_profile():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    user = conn.execute('SELECT gender, age, weight, height, goal FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    else:
        return jsonify({})

@app.route('/save_profile', methods=['POST'])
def save_profile():
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO users (user_id, gender, age, weight, height, goal)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            gender=excluded.gender,
            age=excluded.age,
            weight=excluded.weight,
            height=excluded.height,
            goal=excluded.goal
    ''', (
        data.get('user_id'),
        data.get('gender'),
        data.get('age'),
        data.get('weight'),
        data.get('height'),
        data.get('goal')
    ))
    conn.commit()
    conn.close()
    print('✅ Получены и сохранены данные:', data)
    return jsonify({"status": "ok"})



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
