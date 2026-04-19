from datetime import datetime
from flask import Blueprint, request, jsonify
from db import get_db_connection, is_postgres

rpa_bp = Blueprint('rpa', __name__)


def rows_to_dicts(rows):
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(row)
        else:
            result.append(dict(row))
    return result


@rpa_bp.route("/log", methods=["POST"])
def add_log():
    data = request.get_json() or {}
    bot_name = data.get("bot_name", "Unknown Bot")
    task = data.get("task_description", "No description provided")
    status = data.get("status", "Info")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute("""
                INSERT INTO rpa_logs (timestamp, bot_name, task_description, status)
                VALUES (%s, %s, %s, %s)
            """, (timestamp, bot_name, task, status))
        else:
            cursor.execute("""
                INSERT INTO rpa_logs (timestamp, bot_name, task_description, status)
                VALUES (?, ?, ?, ?)
            """, (timestamp, bot_name, task, status))

        conn.commit()
        conn.close()
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rpa_bp.route("/logs", methods=["GET"])
def get_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rpa_logs ORDER BY id DESC LIMIT 50")
        logs = rows_to_dicts(cursor.fetchall())
        conn.close()
        return jsonify(logs)
    except Exception:
        return jsonify([])