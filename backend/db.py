import os
import sqlite3
import psycopg2
import psycopg2.extras


def get_database_url():
    return os.getenv("DATABASE_URL")


def is_postgres():
    db_url = get_database_url()
    return bool(db_url and db_url.startswith(("postgres://", "postgresql://")))


def get_db_connection():
    db_url = get_database_url()

    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        conn = psycopg2.connect(
            db_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return conn

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "data", "cafe.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if is_postgres():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id SERIAL PRIMARY KEY,
                order_id INTEGER,
                order_line_id INTEGER,
                datetime TIMESTAMP,
                item_id TEXT,
                item_name TEXT,
                category TEXT,
                size TEXT,
                qty INTEGER,
                unit_price NUMERIC(10,2),
                addons TEXT,
                addons_total NUMERIC(10,2),
                line_total NUMERIC(10,2),
                payment_method TEXT,
                time_of_order TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                item_name TEXT UNIQUE,
                category TEXT,
                unit TEXT,
                current_stock INTEGER,
                reorder_level INTEGER,
                reorder_qty INTEGER,
                status TEXT,
                supplier TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                full_name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                status TEXT,
                last_login TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rpa_logs (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                bot_name TEXT,
                task_description TEXT,
                status TEXT
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                order_id INTEGER,
                order_line_id INTEGER,
                datetime TEXT,
                item_id TEXT,
                item_name TEXT,
                category TEXT,
                size TEXT,
                qty INTEGER,
                unit_price REAL,
                addons TEXT,
                addons_total REAL,
                line_total REAL,
                payment_method TEXT,
                time_of_order TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE,
                category TEXT,
                unit TEXT,
                current_stock INTEGER,
                reorder_level INTEGER,
                reorder_qty INTEGER,
                status TEXT,
                supplier TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                full_name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                status TEXT,
                last_login TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rpa_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                bot_name TEXT,
                task_description TEXT,
                status TEXT
            )
        """)

    conn.commit()
    conn.close()