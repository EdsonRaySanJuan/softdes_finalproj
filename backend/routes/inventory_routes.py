import os
import csv
import io
import sqlite3

from flask import Blueprint, jsonify, request, Response
from db import get_db_connection, is_postgres

inventory_bp = Blueprint("inventory", __name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")


def rows_to_dicts(rows):
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(row)
        else:
            result.append(dict(row))
    return result


def csv_file_path(filename):
    safe_name = os.path.basename(filename)
    return os.path.join(DATA_DIR, safe_name)


def compute_status(current_stock, reorder_level):
    status = "Normal"
    if current_stock <= 0:
        status = "Out of Stock"
    elif current_stock <= (reorder_level * 0.25):
        status = "Critical"
    elif current_stock <= reorder_level:
        status = "Low"
    return status


@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        search = str(request.args.get("search", "")).strip()
        category = str(request.args.get("category", "")).strip()
        status = str(request.args.get("status", "")).strip()

        query = """
            SELECT
                id,
                item_name,
                category,
                unit,
                current_stock,
                reorder_level,
                reorder_qty,
                status,
                supplier
            FROM inventory
            WHERE 1=1
        """
        params = []

        if search:
            if is_postgres():
                query += " AND LOWER(item_name) LIKE %s"
                params.append(f"%{search.lower()}%")
            else:
                query += " AND LOWER(item_name) LIKE ?"
                params.append(f"%{search.lower()}%")

        if category:
            if is_postgres():
                query += " AND LOWER(category) = %s"
                params.append(category.lower())
            else:
                query += " AND LOWER(category) = ?"
                params.append(category.lower())

        if status:
            if is_postgres():
                query += " AND LOWER(status) = %s"
                params.append(status.lower())
            else:
                query += " AND LOWER(status) = ?"
                params.append(status.lower())

        query += " ORDER BY category ASC, item_name ASC"

        cursor.execute(query, tuple(params) if is_postgres() else params)
        items = rows_to_dicts(cursor.fetchall())
        conn.close()

        return jsonify({
            "success": True,
            "count": len(items),
            "items": items
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/csv-list", methods=["GET"])
def get_csv_list():
    try:
        if not os.path.exists(DATA_DIR):
            return jsonify({
                "success": True,
                "files": []
            }), 200

        files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".csv")]
        files.sort()

        return jsonify({
            "success": True,
            "count": len(files),
            "files": files
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/csv-view/<path:filename>", methods=["GET"])
def view_csv_file(filename):
    try:
        file_path = csv_file_path(filename)

        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": f"{filename} not found"}), 404

        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))

        return jsonify({
            "success": True,
            "filename": os.path.basename(filename),
            "count": len(rows),
            "rows": rows
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/export-db-csv", methods=["GET"])
def export_inventory_db_to_csv():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM inventory
            ORDER BY category ASC, item_name ASC
        """)
        rows = cursor.fetchall()

        if not rows:
            conn.close()
            return jsonify({"success": False, "error": "No inventory data found"}), 404

        rows = rows_to_dicts(rows)
        conn.close()

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

        csv_data = output.getvalue()
        output.close()

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=inventory_export.csv"}
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/", methods=["POST"])
def add_item():
    try:
        data = request.get_json(force=True)

        item_name = str(data.get("item_name", "")).strip()
        category = str(data.get("category", "")).strip()
        unit = str(data.get("unit", "pcs")).strip()
        current_stock = int(data.get("current_stock", 0))
        reorder_level = int(data.get("reorder_level", 10))
        reorder_qty = int(data.get("reorder_qty", 0))
        supplier = str(data.get("supplier", "N/A")).strip()

        if not item_name or not category:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        status = compute_status(current_stock, reorder_level)

        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute("""
                INSERT INTO inventory (
                    item_name, category, unit, current_stock,
                    reorder_level, reorder_qty, status, supplier
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item_name, category, unit, current_stock,
                reorder_level, reorder_qty, status, supplier
            ))
        else:
            cursor.execute("""
                INSERT INTO inventory (
                    item_name, category, unit, current_stock,
                    reorder_level, reorder_qty, status, supplier
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_name, category, unit, current_stock,
                reorder_level, reorder_qty, status, supplier
            ))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Item added successfully!"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "error": "Item already exists in inventory"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute("SELECT * FROM inventory WHERE id = %s", (item_id,))
        else:
            cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))

        item = cursor.fetchone()
        if not item:
            conn.close()
            return jsonify({"success": False, "error": "Item not found"}), 404

        item = item if isinstance(item, dict) else dict(item)

        new_name = str(data.get("item_name", item["item_name"])).strip()
        new_cat = str(data.get("category", item["category"])).strip()
        new_unit = str(data.get("unit", item["unit"])).strip()
        new_stock = int(data.get("current_stock", item["current_stock"]))
        new_reorder_lvl = int(data.get("reorder_level", item["reorder_level"]))
        new_reorder_qty = int(data.get("reorder_qty", item.get("reorder_qty", 0)))
        new_supplier = str(data.get("supplier", item["supplier"])).strip()

        status = compute_status(new_stock, new_reorder_lvl)

        if is_postgres():
            cursor.execute("""
                UPDATE inventory
                SET item_name = %s,
                    category = %s,
                    unit = %s,
                    current_stock = %s,
                    reorder_level = %s,
                    reorder_qty = %s,
                    supplier = %s,
                    status = %s
                WHERE id = %s
            """, (
                new_name, new_cat, new_unit, new_stock,
                new_reorder_lvl, new_reorder_qty, new_supplier, status, item_id
            ))
        else:
            cursor.execute("""
                UPDATE inventory
                SET item_name = ?,
                    category = ?,
                    unit = ?,
                    current_stock = ?,
                    reorder_level = ?,
                    reorder_qty = ?,
                    supplier = ?,
                    status = ?
                WHERE id = ?
            """, (
                new_name, new_cat, new_unit, new_stock,
                new_reorder_lvl, new_reorder_qty, new_supplier, status, item_id
            ))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Item updated successfully!"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute("SELECT * FROM inventory WHERE id = %s", (item_id,))
        else:
            cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))

        item = cursor.fetchone()
        if not item:
            conn.close()
            return jsonify({"success": False, "error": "Item not found"}), 404

        if is_postgres():
            cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
        else:
            cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Item deleted successfully!"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@inventory_bp.route("/reorder-list", methods=["GET"])
def get_reorder_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                item_name,
                category,
                unit,
                current_stock,
                reorder_level,
                reorder_qty,
                status,
                supplier
            FROM inventory
            WHERE status IN ('Critical', 'Low', 'Out of Stock')
            ORDER BY current_stock ASC, item_name ASC
        """)

        items = rows_to_dicts(cursor.fetchall())
        conn.close()

        return jsonify({
            "success": True,
            "count": len(items),
            "items": items
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500