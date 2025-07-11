from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'users.db'))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
        data['user_id'],
        data['gender'],
        data['age'],
        data['weight'],
        data['height'],
        data['goal']
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)