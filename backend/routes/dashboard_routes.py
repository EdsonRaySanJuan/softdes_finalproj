from flask import Blueprint, jsonify, request
from datetime import timedelta, datetime
from db import get_db_connection, is_postgres


dashboard_bp = Blueprint("dashboard", __name__)


def dict_rows(rows):
    output = []
    for row in rows:
        if isinstance(row, dict):
            output.append(row)
        else:
            output.append(dict(row))
    return output


@dashboard_bp.route("/stats", methods=["GET"])
def get_stats():
    try:
        range_days = int(request.args.get("range", 1))
        if range_days < 1:
            range_days = 1

        conn = get_db_connection()
        cursor = conn.cursor()

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=range_days - 1)

        if is_postgres():
            cursor.execute("""
                SELECT
                    COALESCE(SUM(line_total), 0) AS total_revenue,
                    COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                    COALESCE(SUM(qty), 0) AS items_sold
                FROM sales
                WHERE DATE(timestamp) >= %s
            """, (start_date,))
        else:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(line_total), 0) AS total_revenue,
                    COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                    COALESCE(SUM(qty), 0) AS items_sold
                FROM sales
                WHERE DATE(timestamp) >= ?
            """, (str(start_date),))

        stats = cursor.fetchone()
        stats = stats if isinstance(stats, dict) else dict(stats)

        if is_postgres():
            cursor.execute("""
                SELECT timestamp, order_id, item_name, qty, line_total, payment_method
                FROM sales
                WHERE DATE(timestamp) >= %s
                ORDER BY timestamp DESC
                LIMIT 5
            """, (start_date,))
        else:
            cursor.execute("""
                SELECT timestamp, order_id, item_name, qty, line_total, payment_method
                FROM sales
                WHERE DATE(timestamp) >= ?
                ORDER BY timestamp DESC
                LIMIT 5
            """, (str(start_date),))

        recent = dict_rows(cursor.fetchall())
        conn.close()

        recent_list = []
        for row in recent:
            recent_list.append({
                "timestamp": str(row["timestamp"])[:16] if row.get("timestamp") else "",
                "order_id": int(row["order_id"]) if row.get("order_id") is not None else 0,
                "item_name": row.get("item_name", ""),
                "qty": int(row["qty"] or 0),
                "line_total": float(row["line_total"] or 0),
                "payment_method": row.get("payment_method", "")
            })

        return jsonify({
            "total_revenue": float(stats["total_revenue"] or 0),
            "total_orders": int(stats["total_orders"] or 0),
            "items_sold": int(stats["items_sold"] or 0),
            "alerts": 0,
            "recent_orders": recent_list
        }), 200

    except Exception as e:
        print(f"Dashboard Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500