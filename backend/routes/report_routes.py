from flask import Blueprint, request, jsonify
from db import get_db_connection, is_postgres


report_bp = Blueprint("reports", __name__)


def dict_rows(rows):
    output = []
    for row in rows:
        if isinstance(row, dict):
            output.append(row)
        else:
            output.append(dict(row))
    return output


@report_bp.route("/", methods=["GET"])
def get_reports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COALESCE(SUM(line_total), 0) AS total_sales,
                COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                COALESCE(SUM(line_total) / NULLIF(COUNT(DISTINCT order_id), 0), 0) AS avg_order
            FROM sales
        """)
        stats = cursor.fetchone()
        stats = stats if isinstance(stats, dict) else dict(stats)

        cursor.execute("""
            SELECT category, COUNT(*) AS cnt
            FROM sales
            GROUP BY category
            ORDER BY cnt DESC
            LIMIT 1
        """)
        top = cursor.fetchone()
        conn.close()

        top_category = "N/A"
        if top:
            top = top if isinstance(top, dict) else dict(top)
            top_category = top["category"]

        return jsonify({
            "total_sales": float(stats["total_sales"] or 0),
            "total_orders": int(stats["total_orders"] or 0),
            "avg_order": float(stats["avg_order"] or 0),
            "top_category": top_category
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@report_bp.route("/range", methods=["GET"])
def report_by_range():
    try:
        start = request.args.get("start")
        end = request.args.get("end")

        conn = get_db_connection()
        cursor = conn.cursor()

        if start and end:
            if is_postgres():
                cursor.execute("""
                    SELECT
                        COALESCE(SUM(line_total), 0) AS total_sales,
                        COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                        COALESCE(SUM(line_total) / NULLIF(COUNT(DISTINCT order_id), 0), 0) AS avg_order
                    FROM sales
                    WHERE DATE(timestamp) BETWEEN %s AND %s
                """, (start, end))
            else:
                cursor.execute("""
                    SELECT
                        COALESCE(SUM(line_total), 0) AS total_sales,
                        COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                        COALESCE(SUM(line_total) / NULLIF(COUNT(DISTINCT order_id), 0), 0) AS avg_order
                    FROM sales
                    WHERE DATE(timestamp) BETWEEN ? AND ?
                """, (start, end))
        else:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(line_total), 0) AS total_sales,
                    COALESCE(COUNT(DISTINCT order_id), 0) AS total_orders,
                    COALESCE(SUM(line_total) / NULLIF(COUNT(DISTINCT order_id), 0), 0) AS avg_order
                FROM sales
            """)

        stats = cursor.fetchone()
        stats = stats if isinstance(stats, dict) else dict(stats)

        if start and end:
            if is_postgres():
                cursor.execute("""
                    SELECT category, COUNT(*) AS cnt
                    FROM sales
                    WHERE DATE(timestamp) BETWEEN %s AND %s
                    GROUP BY category
                    ORDER BY cnt DESC
                    LIMIT 1
                """, (start, end))
            else:
                cursor.execute("""
                    SELECT category, COUNT(*) AS cnt
                    FROM sales
                    WHERE DATE(timestamp) BETWEEN ? AND ?
                    GROUP BY category
                    ORDER BY cnt DESC
                    LIMIT 1
                """, (start, end))
        else:
            cursor.execute("""
                SELECT category, COUNT(*) AS cnt
                FROM sales
                GROUP BY category
                ORDER BY cnt DESC
                LIMIT 1
            """)

        top = cursor.fetchone()
        conn.close()

        top_category = "N/A"
        if top:
            top = top if isinstance(top, dict) else dict(top)
            top_category = top["category"]

        return jsonify({
            "total_sales": float(stats["total_sales"] or 0),
            "total_orders": int(stats["total_orders"] or 0),
            "avg_order": float(stats["avg_order"] or 0),
            "top_category": top_category
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@report_bp.route("/daily", methods=["GET"])
def daily_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                DATE(timestamp) AS date,
                COUNT(DISTINCT order_id) AS orders,
                COALESCE(SUM(line_total), 0) AS total_sales,
                category
            FROM sales
            GROUP BY DATE(timestamp), category
            ORDER BY DATE(timestamp) DESC, total_sales DESC
        """)

        rows = dict_rows(cursor.fetchall())
        conn.close()

        daily = {}
        for row in rows:
            date = str(row["date"])
            if date not in daily:
                daily[date] = {
                    "date": date,
                    "orders": int(row["orders"]),
                    "total_sales": float(row["total_sales"]),
                    "top_category": row["category"],
                    "avg_handling": "02:15"
                }

        return jsonify(list(daily.values()))

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@report_bp.route("/chart", methods=["GET"])
def chart_data():
    try:
        range_type = request.args.get("range", "7")
        days_map = {"1": 1, "3": 3, "7": 7, "30": 30}
        days = days_map.get(range_type, 7)

        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute("""
                SELECT DATE(timestamp) AS date, COALESCE(SUM(line_total), 0) AS sales
                FROM sales
                WHERE DATE(timestamp) >= CURRENT_DATE - (%s * INTERVAL '1 day')
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            """, (days,))
        else:
            cursor.execute("""
                SELECT DATE(timestamp) AS date, COALESCE(SUM(line_total), 0) AS sales
                FROM sales
                WHERE DATE(timestamp) >= DATE('now', ?)
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            """, (f"-{days} days",))

        rows = dict_rows(cursor.fetchall())
        conn.close()

        result = [{"date": str(r["date"]), "sales": float(r["sales"])} for r in rows]
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500