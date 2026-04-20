from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from db import get_db_connection, is_postgres
from rpa_agent import run_automation_cycle

rpa_bp = Blueprint("rpa", __name__)


def rows_to_dicts(rows):
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(row)
        else:
            result.append(dict(row))
    return result


ALLOWED_ORIGINS = [
    "https://softdes-finalproj.vercel.app",
    "https://softdes-finalproj-98pf71sx2-edsonraysanjuans-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]


@rpa_bp.route("/run-bot", methods=["POST", "OPTIONS"])
@cross_origin(
    origins=ALLOWED_ORIGINS,
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
def run_bot():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    try:
        current_app.logger.info("RUN BOT: route entered")

        result = run_automation_cycle()

        current_app.logger.info(f"RUN BOT: function returned: {result}")

        return jsonify({
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "bot_name": result.get("bot_name", "Unknown Bot"),
            "checked_items": result.get("checked_items", 0),
            "processed_items": result.get("processed_items", 0),
            "logs_sent": result.get("logs_sent", 0),
            "items": result.get("items", [])
        }), 200 if result.get("success") else 500

    except Exception as e:
        current_app.logger.exception(f"RUN BOT ERROR: {e}")

        return jsonify({
            "success": False,
            "message": str(e),
            "bot_name": "Unknown Bot",
            "checked_items": 0,
            "processed_items": 0,
            "logs_sent": 0,
            "items": []
        }), 500


@rpa_bp.route("/log", methods=["POST", "OPTIONS"])
@cross_origin(
    origins=ALLOWED_ORIGINS,
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
def add_log():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    data = request.get_json() or {}
    bot_name = str(data.get("bot_name", "Unknown Bot")).strip()
    task = str(data.get("task_description", "No description provided")).strip()
    status = str(data.get("status", "Info")).strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres(conn):
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

        return jsonify({
            "success": True,
            "message": "Log added successfully"
        }), 201

    except Exception as e:
        current_app.logger.exception(f"ADD LOG ERROR: {e}")

        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if conn:
            conn.close()


@rpa_bp.route("/logs", methods=["GET"])
@cross_origin(
    origins=ALLOWED_ORIGINS,
    methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
)
def get_logs():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, bot_name, task_description, status
            FROM rpa_logs
            ORDER BY id DESC
            LIMIT 50
        """)

        logs = rows_to_dicts(cursor.fetchall())

        return jsonify({
            "success": True,
            "count": len(logs),
            "logs": logs
        }), 200

    except Exception as e:
        current_app.logger.exception(f"GET LOGS ERROR: {e}")

        return jsonify({
            "success": False,
            "error": str(e),
            "logs": []
        }), 500

    finally:
        if conn:
            conn.close()