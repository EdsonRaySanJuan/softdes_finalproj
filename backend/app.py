import os
import pandas as pd
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

ALLOWED_ORIGINS = [
    "https://softdes-finalproj.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]

def is_allowed_origin(origin):
    if not origin:
        return False

    if origin in ALLOWED_ORIGINS:
        return True

    if origin.startswith("https://softdes-finalproj-") and origin.endswith(".vercel.app"):
        return True

    return False

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")
        response = jsonify({"ok": True})

        if is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        return response, 200

CORS(
    app,
    resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True
)

init_db()

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

@app.route("/api/debug/seed-admin", methods=["GET"])
def seed_admin():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute("""
                INSERT INTO users (user_id, full_name, username, password, role, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, ("ADM001", "System Boss", "admin", "admin123", "Admin", "Active"))
        else:
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, full_name, username, password, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("ADM001", "System Boss", "admin", "admin123", "Admin", "Active"))

        conn.commit()

        if is_postgres():
            cursor.execute("""
                SELECT user_id, full_name, username, role, status
                FROM users
                WHERE user_id = %s
            """, ("ADM001",))
        else:
            cursor.execute("""
                SELECT user_id, full_name, username, role, status
                FROM users
                WHERE user_id = ?
            """, ("ADM001",))

        row = cursor.fetchone()
        conn.close()

        if row:
            row = row if isinstance(row, dict) else dict(row)

        return jsonify({
            "success": True,
            "message": "Admin user seeded successfully",
            "user": row
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/debug/inventory", methods=["GET"])
def debug_inventory():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, item_name, current_stock, reorder_level, status, supplier
            FROM inventory
            ORDER BY item_name ASC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append(row if isinstance(row, dict) else dict(row))

        return jsonify({
            "using_postgres": is_postgres(),
            "inventory_count": len(result),
            "items": result
        }), 200

    except Exception as e:
        return jsonify({
            "using_postgres": is_postgres(),
            "error": str(e)
        }), 500

@app.route("/api/debug/seed-inventory", methods=["GET"])
def seed_inventory():
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, "cafe_ingredients_inventory.csv")

        if not os.path.exists(csv_path):
            return jsonify({
                "success": False,
                "error": f"CSV not found at {csv_path}"
            }), 404

        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["ingredient_name", "stock_qty", "reorder_level"])

        df["supplier"] = df["supplier"].fillna("Unknown")
        df["unit"] = df["unit"].fillna("pcs")
        df["ingredient_name"] = df["ingredient_name"].astype(str).str.strip()
        df["storage_type"] = df["storage_type"].fillna("General")
        df = df.drop_duplicates(subset=["ingredient_name"], keep="first")

        conn = get_db_connection()
        cursor = conn.cursor()

        inserted_or_updated = 0

        for _, row in df.iterrows():
            item_name = str(row["ingredient_name"]).strip()
            category = str(row["storage_type"]).strip()
            unit = str(row["unit"]).strip()
            current_stock = int(float(row["stock_qty"]))
            reorder_level = int(float(row["reorder_level"]))
            reorder_qty = int(float(row["reorder_qty"])) if "reorder_qty" in row and pd.notna(row["reorder_qty"]) else 0
            supplier = str(row["supplier"]).strip()

            status = "Normal"
            if current_stock <= 0:
                status = "Out of Stock"
            elif current_stock <= (reorder_level * 0.25):
                status = "Critical"
            elif current_stock <= reorder_level:
                status = "Low"

            if is_postgres():
                cursor.execute("""
                    INSERT INTO inventory (
                        item_name, category, unit, current_stock,
                        reorder_level, reorder_qty, status, supplier
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (item_name)
                    DO UPDATE SET
                        category = EXCLUDED.category,
                        unit = EXCLUDED.unit,
                        current_stock = EXCLUDED.current_stock,
                        reorder_level = EXCLUDED.reorder_level,
                        reorder_qty = EXCLUDED.reorder_qty,
                        status = EXCLUDED.status,
                        supplier = EXCLUDED.supplier
                """, (
                    item_name, category, unit, current_stock,
                    reorder_level, reorder_qty, status, supplier
                ))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO inventory (
                        item_name, category, unit, current_stock,
                        reorder_level, reorder_qty, status, supplier
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_name, category, unit, current_stock,
                    reorder_level, reorder_qty, status, supplier
                ))

            inserted_or_updated += 1

        conn.commit()

        cursor.execute("SELECT COUNT(*) AS inventory_count FROM inventory")
        row = cursor.fetchone()
        conn.close()

        if isinstance(row, dict):
            inventory_count = row["inventory_count"]
        else:
            inventory_count = row["inventory_count"] if "inventory_count" in row.keys() else row[0]

        return jsonify({
            "success": True,
            "message": "Inventory seeded successfully",
            "csv_path": csv_path,
            "processed_rows": int(inserted_or_updated),
            "inventory_count": int(inventory_count),
            "using_postgres": is_postgres()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "using_postgres": is_postgres(),
            "error": str(e)
        }), 500

app.register_blueprint(report_bp, url_prefix="/api/reports")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(order_bp, url_prefix="/api/orders")
app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(rpa_bp, url_prefix="/api/rpa")

@app.route("/")
def home():
    return {"message": "Cafe POS Backend is running", "status": "online"}

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)