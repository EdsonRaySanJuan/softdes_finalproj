import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from db import init_db, get_db_connection, is_postgres
from routes.report_routes import report_bp
from routes.dashboard_routes import dashboard_bp
from routes.order_routes import order_bp
from routes.inventory_routes import inventory_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.rpa_routes import rpa_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

@app.route("/api/debug/db-check", methods=["GET"])
def debug_db_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS user_count FROM users")
        row = cursor.fetchone()
        conn.close()

        if isinstance(row, dict):
            user_count = row["user_count"]
        else:
            user_count = row["user_count"] if "user_count" in row.keys() else row[0]

        return jsonify({
            "using_postgres": is_postgres(),
            "user_count": int(user_count)
        }), 200

    except Exception as e:
        return jsonify({
            "using_postgres": is_postgres(),
            "error": str(e)
        }), 500