import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER UNIQUE NOT NULL,
            month TEXT NOT NULL,
            incoming INTEGER NOT NULL,
            outgoing INTEGER NOT NULL,
            country TEXT NOT NULL,
            stock_level INTEGER NOT NULL,
            PRIMARY KEY(product_id AUTOINCREMENT)
        );
        """)
        self.conn.commit()

    def fetch_all_rows(self):
        self.cur.execute("SELECT product_id, month, incoming, outgoing,country,stock_level FROM products")
        return self.cur.fetchall()

    def fetch_by_product_id(self, product_id):
        self.cur.execute(
            "SELECT product_id, month, incoming, outgoing,country,stock_level FROM products WHERE product_id=?", (product_id,))
        return self.cur.fetchone()  # Return a single tuple instead of a list


    def insert(self, product_id, month, incoming, outgoing,country,stock_level):
        self.cur.execute("INSERT INTO products (product_id, month, incoming, outgoing,country,stock_level) VALUES (?, ?, ?, ?,?,?)",
                         (product_id, month, incoming, outgoing,country,stock_level))
        self.conn.commit()

    def remove(self, product_id):
        self.cur.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        self.conn.commit()

    def update(self,rowid,product_id, month, incoming, outgoing,country,stock_level):
        self.cur.execute("""
        UPDATE products
        SET
        product_id=?,
        month=?, 
        incoming=?, 
        outgoing=?,
        country=?,
        stock_level=?
        WHERE
            rowid=?
        """, (product_id,month, incoming, outgoing,country,stock_level,rowid))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
