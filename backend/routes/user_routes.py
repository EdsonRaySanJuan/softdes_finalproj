import sqlite3
from flask import Blueprint, request, jsonify
from db import get_db_connection, is_postgres

user_bp = Blueprint('users', __name__)


def rows_to_dicts(rows):
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(row)
        else:
            result.append(dict(row))
    return result


@user_bp.route("/", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, full_name, username, role, status FROM users")
    users = rows_to_dicts(cursor.fetchall())
    conn.close()
    return jsonify(users)


@user_bp.route("/", methods=["POST"])
def add_user():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if is_postgres():
            cursor.execute("""
                INSERT INTO users (user_id, full_name, username, password, role, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data.get('user_id'),
                data.get('full_name'),
                data.get('username'),
                data.get('password'),
                data.get('role'),
                data.get('status', 'Active')
            ))
        else:
            cursor.execute("""
                INSERT INTO users (user_id, full_name, username, password, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data.get('user_id'),
                data.get('full_name'),
                data.get('username'),
                data.get('password'),
                data.get('role'),
                data.get('status', 'Active')
            ))

        conn.commit()
        return jsonify({"success": True}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or ID already exists!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id == 'ADM001' or user_id.lower() == 'admin':
        return jsonify({"error": "Cannot delete the master admin account!"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if is_postgres():
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found."}), 404

        return jsonify({"success": True, "message": "User deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()