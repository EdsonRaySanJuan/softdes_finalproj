from flask import Blueprint, jsonify, request
from datetime import timedelta, datetime
from db import get_db_connection, is_postgres

dashboard_bp = Blueprint('dashboard', __name__)


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
                WHERE DATE(datetime) >= %s
            """, (start_date,))
        else:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(line_total), 0) AS total_revenue,
                    COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                    COALESCE(SUM(qty), 0) AS items_sold
                FROM sales
                WHERE DATE(datetime) >= ?
            """, (str(start_date),))

        stats = cursor.fetchone()
        stats = stats if isinstance(stats, dict) else dict(stats)

        if is_postgres():
            cursor.execute("""
                SELECT datetime, order_id, item_name, qty, line_total, payment_method
                FROM sales
                WHERE DATE(datetime) >= %s
                ORDER BY datetime DESC
                LIMIT 5
            """, (start_date,))
        else:
            cursor.execute("""
                SELECT datetime, order_id, item_name, qty, line_total, payment_method
                FROM sales
                WHERE DATE(datetime) >= ?
                ORDER BY datetime DESC
                LIMIT 5
            """, (str(start_date),))

        recent = dict_rows(cursor.fetchall())
        conn.close()

        recent_list = []
        for row in recent:
            recent_list.append({
                "datetime": str(row["datetime"])[:16],
                "order_id": int(row["order_id"]) if row["order_id"] is not None else 0,
                "item_name": row["item_name"],
                "qty": int(row["qty"]),
                "line_total": float(row["line_total"]),
                "payment_method": row["payment_method"]
            })

        return jsonify({
            "total_revenue": float(stats["total_revenue"] or 0),
            "total_orders": int(stats["total_orders"] or 0),
            "items_sold": int(stats["items_sold"] or 0),
            "alerts": 0,
            "recent_orders": recent_list
        })

    except Exception as e:
        print(f"Dashboard Error: {e}")
        return jsonify({"error": str(e)}), 500