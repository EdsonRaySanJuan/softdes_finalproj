from datetime import datetime
from flask import Blueprint, request, jsonify
from db import get_db_connection, is_postgres

order_bp = Blueprint("orders", __name__)


def dict_row(row):
    if not row:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


def get_next_order_id(conn, cursor):
    cursor.execute("SELECT COALESCE(MAX(order_id), 0) AS max_id FROM sales")
    row = cursor.fetchone()
    row = dict_row(row)
    return int(row["max_id"]) + 1


@order_bp.route("/", methods=["POST"])
def create_order():
    try:
        data = request.get_json(force=True)

        items = data.get("items", [])
        total = float(data.get("total", 0))
        cash = float(data.get("cash", 0))
        change = float(data.get("change", 0))
        table = data.get("table", "Walk-in")
        payment_method = data.get("payment_method", "Cash")

        if not items:
            return jsonify({"error": "Cart is empty"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        order_id = get_next_order_id(conn, cursor)
        now = datetime.now()
        dt_str = now.strftime("%Y-%m-%d %H:%M:%S")
        time_str = now.strftime("%H:%M:%S")

        rows_written = 0
        line_index = 1

        for item in items:
            name = item.get("name", "")
            size = item.get("size", "")
            qty = int(item.get("qty", 1))
            unit_price = float(item.get("unitPrice", 0))

            addons_list = item.get("addons", []) or []
            addons_names = ", ".join(a.get("name", "") for a in addons_list)
            addons_total = sum(float(a.get("price", 0)) for a in addons_list)
            line_total = (unit_price * qty) + addons_total
            item_id = f"{order_id}-{line_index}"

            if is_postgres():
                cursor.execute("""
                    INSERT INTO sales (
                        order_id, order_line_id, datetime, item_id, item_name,
                        category, size, qty, unit_price, addons, addons_total,
                        line_total, payment_method, time_of_order
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    order_id, line_index, dt_str, item_id, name,
                    table, size, qty, unit_price, addons_names,
                    addons_total, line_total, payment_method, time_str
                ))
            else:
                cursor.execute("""
                    INSERT INTO sales (
                        order_id, order_line_id, datetime, item_id, item_name,
                        category, size, qty, unit_price, addons, addons_total,
                        line_total, payment_method, time_of_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_id, line_index, dt_str, item_id, name,
                    table, size, qty, unit_price, addons_names,
                    addons_total, line_total, payment_method, time_str
                ))

            if is_postgres():
                cursor.execute("""
                    UPDATE inventory
                    SET current_stock = current_stock - %s
                    WHERE item_name = %s
                """, (qty, name))
            else:
                cursor.execute("""
                    UPDATE inventory
                    SET current_stock = current_stock - ?
                    WHERE item_name = ?
                """, (qty, name))

            if is_postgres():
                cursor.execute("""
                    SELECT current_stock, reorder_level
                    FROM inventory
                    WHERE item_name = %s
                """, (name,))
            else:
                cursor.execute("""
                    SELECT current_stock, reorder_level
                    FROM inventory
                    WHERE item_name = ?
                """, (name,))

            result = cursor.fetchone()

            if result:
                result = dict_row(result)
                current_stock = int(result["current_stock"])
                reorder_level = int(result["reorder_level"])

                if current_stock <= reorder_level:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if is_postgres():
                        cursor.execute("""
                            INSERT INTO rpa_logs (timestamp, bot_name, task_description, status)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            now_str,
                            "InventoryBot",
                            f"Reorder triggered for {name}",
                            "Pending"
                        ))
                    else:
                        cursor.execute("""
                            INSERT INTO rpa_logs (timestamp, bot_name, task_description, status)
                            VALUES (?, ?, ?, ?)
                        """, (
                            now_str,
                            "InventoryBot",
                            f"Reorder triggered for {name}",
                            "Pending"
                        ))

            rows_written += 1
            line_index += 1

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "order_id": order_id,
            "total": total,
            "cash": cash,
            "change": change,
            "lines_written": rows_written,
            "message": "Order processed + inventory updated + RPA triggered if needed"
        }), 201

    except Exception as e:
        print("Order Error:", e)
        return jsonify({"error": str(e)}), 500


@order_bp.route("/", methods=["GET"])
def list_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT order_id, MAX(datetime) AS datetime, SUM(line_total) AS total
            FROM sales
            GROUP BY order_id
            ORDER BY MAX(datetime) DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            row = dict_row(row)
            result.append({
                "order_id": row["order_id"],
                "datetime": str(row["datetime"]),
                "total": float(row["total"])
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500