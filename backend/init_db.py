import sqlite3
import pandas as pd
import os

def setup_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db_path = os.path.join(data_dir, "cafe_new.db")

    csv_inventory_path = os.path.join(data_dir, "inventory.csv")
    csv_drink_recipes_path = os.path.join(data_dir, "drink_recipes.csv")
    csv_addon_recipes_path = os.path.join(data_dir, "addon_recipes.csv")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ==========================================
    # 1. USERS TABLE
    # ==========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            full_name TEXT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            status TEXT,
            last_login TEXT
        )
    ''')

    # Seed default admin
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, full_name, username, password, role, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('ADM001', 'System Boss', 'admin', 'admin123', 'Admin', 'Active'))
    print("✅ Users table ready. Default admin seeded.")

    # ==========================================
    # 2. INVENTORY TABLE
    # ==========================================
    cursor.execute('DROP TABLE IF EXISTS inventory')
    cursor.execute('''
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            category TEXT,
            unit TEXT,
            current_stock REAL,
            reorder_level REAL,
            reorder_qty REAL,
            status TEXT,
            supplier TEXT
        )
    ''')

    if os.path.exists(csv_inventory_path):
        df = pd.read_csv(csv_inventory_path)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['item_name'])
        df['unit'] = df['unit'].fillna('pcs')
        df['current_stock'] = pd.to_numeric(df['current_stock'], errors='coerce').fillna(0)
        df['reorder_level'] = pd.to_numeric(df['reorder_level'], errors='coerce').fillna(0)
        df['reorder_qty'] = pd.to_numeric(df['reorder_qty'], errors='coerce').fillna(0)
        df['supplier'] = 'Unknown'   # ← add default since CSV has no supplier column
        df['category'] = df['category'].fillna('')
        df = df.drop_duplicates(subset=['item_name'], keep='first')

        for _, row in df.iterrows():
            stock = float(row['current_stock'])
            reorder_lvl = float(row['reorder_level'])

            if stock <= 0:
                status = "Out of Stock"
            elif stock <= reorder_lvl * 0.25:
                status = "Critical"
            elif stock <= reorder_lvl:
                status = "Low"
            else:
                status = "Normal"

            cursor.execute('''
                INSERT OR IGNORE INTO inventory
                (item_name, category, unit, current_stock, reorder_level, reorder_qty, status, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(row['item_name']).strip(),
                row['category'],
                row['unit'],
                stock,
                reorder_lvl,
                float(row['reorder_qty']),
                status,
                row['supplier']
            ))
        print(f"✅ Inventory synced: {len(df)} items.")
    else:
        print(f"⚠️  inventory.csv not found at {csv_inventory_path}")

    # ==========================================
    # 3. SALES TABLE
    # ==========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            timestamp TEXT,
            item_name TEXT,
            category TEXT,
            size TEXT,
            qty INTEGER,
            unit_price REAL,
            line_total REAL,
            addons TEXT,
            payment_method TEXT,
            cash REAL,
            change REAL,
            table_no TEXT
        )
    ''')
    print("✅ Sales table ready.")

    # ==========================================
    # 4. RPA LOGS TABLE
    # ==========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rpa_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            bot_name TEXT,
            task_description TEXT,
            status TEXT
        )
    ''')
    print("✅ RPA logs table ready.")

    # ==========================================
    # 5. DRINK RECIPES TABLE
    # ==========================================
    cursor.execute('DROP TABLE IF EXISTS drink_recipes')
    cursor.execute('''
        CREATE TABLE drink_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_category TEXT,
            menu_item TEXT,
            size TEXT,
            ingredient_name TEXT,
            qty_used REAL,
            unit TEXT,
            recipe_type TEXT
        )
    ''')

    if os.path.exists(csv_drink_recipes_path):
        df = pd.read_csv(csv_drink_recipes_path)
        df.columns = df.columns.str.strip()
        df.to_sql('drink_recipes', conn, if_exists='append', index=False)
        print(f"✅ Drink recipes synced: {len(df)} rows.")
    else:
        print(f"⚠️  drink_recipes.csv not found at {csv_drink_recipes_path}")

    # ==========================================
    # 6. ADDON RECIPES TABLE
    # ==========================================
    cursor.execute('DROP TABLE IF EXISTS addon_recipes')
    cursor.execute('''
        CREATE TABLE addon_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            addon_name TEXT,
            ingredient_name TEXT,
            qty_used REAL,
            unit TEXT,
            stocks REAL
        )
    ''')

    if os.path.exists(csv_addon_recipes_path):
        df = pd.read_csv(csv_addon_recipes_path)
        df.columns = df.columns.str.strip()
        df.to_sql('addon_recipes', conn, if_exists='append', index=False)
        print(f"✅ Addon recipes synced: {len(df)} rows.")
    else:
        print(f"⚠️  addon_recipes.csv not found at {csv_addon_recipes_path}")

    conn.commit()
    conn.close()
    print("\n✅ Database setup complete → data/cafe_new.db")


if __name__ == "__main__":
    setup_database()