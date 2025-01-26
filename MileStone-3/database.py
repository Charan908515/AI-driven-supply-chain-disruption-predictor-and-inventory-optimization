import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            month TEXT NOT NULL,
            cost_price INTEGER NOT NULL,
            selling_price INTEGER NOT NULL,
            country TEXT NOT NULL,
            stock_level INTEGER NOT NULL
            
        );
        """)
        self.conn.commit()

    def fetch_all_rows(self):
        self.cur.execute("SELECT product_id, company, month, cost_price, selling_price, country, stock_level FROM products")
        return self.cur.fetchall()

    def fetch_by_product_id(self, product_id):
        self.cur.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
        return self.cur.fetchone()

    def insert(self, product_id, company, month, cost_price, selling_price, country, stock_level):
        self.cur.execute(
            "INSERT INTO products (product_id, company, month, cost_price, selling_price, country, stock_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (product_id, company, month, cost_price, selling_price, country, stock_level)
        )
        self.conn.commit()

    def remove(self, product_id):
        self.cur.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        self.conn.commit()

    def update(self, rowid, product_id, company, month, cost_price, selling_price, country, stock_level):
        self.cur.execute("""
        UPDATE products
        SET product_id=?, company=?, month=?, cost_price=?, selling_price=?, country=?, stock_level=?
        WHERE rowid=?
        """, (product_id, company, month, cost_price, selling_price, country, stock_level, rowid))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


class Adjusted_database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS adjusted_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INT NOT NULL,
            company TEXT NOT NULL,
            country TEXT NOT NULL,
            stock_level INT NOT NULL,
            stock_adjusted INT NOT NULL,
            adjustment FLOAT NOT NULL,
            month TEXT NOT NULL,
            reason TEXT NOT NULL,
            alert TEXT NOT NULL
                         
        );
        """)
        self.conn.commit()

    def fetch_all_rows(self):
        self.cur.execute("SELECT product_id, company, country, stock_level, stock_adjusted, adjustment, month, reason,alert FROM adjusted_inventory")
        return self.cur.fetchall()

    def insert(self, product_id, company, country, stock_level, stock_adjusted, adjustment, month, reason,alert):
        self.cur.execute("""
        INSERT INTO adjusted_inventory (product_id, company, country, stock_level, stock_adjusted, adjustment, month, reason,alert)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
        """, (product_id, company, country, stock_level, stock_adjusted, adjustment, month, reason,alert))
        self.conn.commit()

    def remove(self, product_id):
        self.cur.execute("DELETE FROM adjusted_inventory WHERE product_id=?", (product_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


# Create a new database connection for damaged logs
class DamagedLogDatabase:
    def _init_(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS damaged_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            country TEXT NOT NULL,
            damage_reason TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            reported_date TEXT NOT NULL
        );
        """)
        self.conn.commit()

    def insert(self, product_id, company, country, damage_reason, quantity, reported_date):
        self.cur.execute("""
        INSERT INTO damaged_logs (product_id, company, country, damage_reason, quantity, reported_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, company, country, damage_reason, quantity, reported_date))
        self.conn.commit()

    def fetch_all_rows(self):
        self.cur.execute("SELECT * FROM damaged_logs")
        return self.cur.fetchall()

    def _del_(self):
        self.conn.close()
