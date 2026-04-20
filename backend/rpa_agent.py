import os
import time
import requests
from datetime import datetime

from db import get_db_connection, is_postgres


API_URL = os.getenv("API_BASE_URL", "https://softdes-finalproj.onrender.com/api").rstrip("/")
BOT_NAME = os.getenv("RPA_BOT_NAME", "Inventory-Master-V1")
SLEEP_SECONDS = int(os.getenv("RPA_INTERVAL_SECONDS", "60"))

GET_TIMEOUT = (5, 45)


def save_log(bot_name, task_description, status):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_postgres(conn):
            cursor.execute("""
                INSERT INTO rpa_logs (timestamp, bot_name, task_description, status)
                VALUES (%s, %s, %s, %s)
            """, (timestamp, bot_name, task_description, status))
        else:
            cursor.execute("""
                INSERT INTO rpa_logs (timestamp, bot_name, task_description, status)
                VALUES (?, ?, ?, ?)
            """, (timestamp, bot_name, task_description, status))

        conn.commit()
        return True

    except Exception as e:
        print(f"save_log error: {e}", flush=True)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False

    finally:
        if conn:
            conn.close()


def run_automation_cycle():
    results = {
        "success": True,
        "bot_name": BOT_NAME,
        "checked_items": 0,
        "processed_items": 0,
        "logs_sent": 0,
        "items": [],
        "message": ""
    }

    try:
        response = requests.get(
            f"{API_URL}/inventory/reorder-list",
            timeout=GET_TIMEOUT
        )
        response.raise_for_status()

        payload = response.json()
        reorder_list = payload.get("items", []) if isinstance(payload, dict) else []
        results["checked_items"] = len(reorder_list)

        if not reorder_list:
            results["message"] = "Everything looks good. No reorders needed."
            return results

        for item in reorder_list:
            item_name = item.get("item_name", "Unknown Item")
            supplier = item.get("supplier") or "N/A"
            reorder_qty = item.get("reorder_qty", 0)
            unit = item.get("unit", "")
            current_stock = item.get("current_stock", 0)
            status = item.get("status", "Unknown")

            task_msg = (
                f"Automatically sent PO to {supplier} for {reorder_qty} {unit} "
                f"of {item_name}. Current stock: {current_stock}. Status: {status}."
            )

            saved = save_log(
                BOT_NAME,
                task_msg,
                "Completed"
            )

            results["processed_items"] += 1
            if saved:
                results["logs_sent"] += 1

            results["items"].append({
                "item_name": item_name,
                "supplier": supplier,
                "reorder_qty": reorder_qty,
                "unit": unit,
                "current_stock": current_stock,
                "status": status
            })

        results["message"] = f"Processed {results['processed_items']} reorder item(s)."
        return results

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "bot_name": BOT_NAME,
            "checked_items": results["checked_items"],
            "processed_items": results["processed_items"],
            "logs_sent": results["logs_sent"],
            "items": results["items"],
            "message": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "bot_name": BOT_NAME,
            "checked_items": results["checked_items"],
            "processed_items": results["processed_items"],
            "logs_sent": results["logs_sent"],
            "items": results["items"],
            "message": f"Bot error: {str(e)}"
        }


if __name__ == "__main__":
    while True:
        result = run_automation_cycle()
        print(result)
        time.sleep(SLEEP_SECONDS)