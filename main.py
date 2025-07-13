import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:eHi-fyP&qYT5wb4@db.bcobuebwqxoipouzjxye.supabase.co:5432/postgres')

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
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
    cur.close()
    conn.close()

init_db()

@app.route('/get_profile')
def get_profile():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT gender, age, weight, height, goal FROM users WHERE user_id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify(dict(zip(['gender', 'age', 'weight', 'height', 'goal'], row)))
    else:
        return jsonify({})

@app.route('/save_profile', methods=['POST'])
def save_profile():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, gender, age, weight, height, goal)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            gender = EXCLUDED.gender,
            age = EXCLUDED.age,
            weight = EXCLUDED.weight,
            height = EXCLUDED.height,
            goal = EXCLUDED.goal
    ''', (
        data.get('user_id'),
        data.get('gender'),
        data.get('age'),
        data.get('weight'),
        data.get('height'),
        data.get('goal')
    ))
    conn.commit()
    cur.close()
    conn.close()
    print('✅ Получены и сохранены данные:', data)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
