import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from functools import wraps
from db import get_db_connection, is_postgres

auth_bp = Blueprint('auth', __name__)


def fetch_one_dict(cursor):
    row = cursor.fetchone()
    if not row:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    raw_id = data.get('username')
    raw_pw = data.get('password')

    login_id = str(raw_id).strip() if raw_id else ""
    password = str(raw_pw).strip() if raw_pw else ""

    print(f"\n=== LOGIN DEBUG ===")
    print(f"React sent ID: '{login_id}'")
    print(f"React sent PW: '{password}'")
    print(f"===================\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    if is_postgres():
        cursor.execute("""
            SELECT * FROM users
            WHERE (LOWER(username) = LOWER(%s) OR LOWER(user_id) = LOWER(%s))
            AND password = %s
            LIMIT 1
        """, (login_id, login_id, password))
    else:
        cursor.execute("""
            SELECT * FROM users
            WHERE (LOWER(username) = LOWER(?) OR LOWER(user_id) = LOWER(?))
            AND password = ?
        """, (login_id, login_id, password))

    user = fetch_one_dict(cursor)
    conn.close()

    if user:
        print("[SUCCESS] Credentials matched a database row!")
        if user['status'] == 'Disabled':
            return jsonify({'error': 'Account is disabled. Contact Admin.'}), 403

        token = jwt.encode({
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            'token': token,
            'role': user['role'],
            'username': user['username'],
            'full_name': user['full_name']
        })

    print("[FAILED] Credentials did not match anything in the database.")
    return jsonify({'error': 'Invalid username or password'}), 401


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(data, *args, **kwargs)
    return decorated