import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="inventory.db"):
        self.connection = sqlite3.connect(db_name)

        # Allows rows to be accessed like dictionaries:
        # row["size"], row["quantity"], etc.
        self.connection.row_factory = sqlite3.Row

        # SQLite doesn't enforce foreign keys unless enabled
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.cursor = self.connection.cursor()

        self.create_tables()


    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT,
                brand TEXT,
                size TEXT NOT NULL,
                condition TEXT NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tire_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                date_sold TEXT NOT NULL,
                FOREIGN KEY (tire_id) REFERENCES tires(id)
            )
        """)

        self.connection.commit()


    def add_used_tire(self, size, quantity):
        # Used tires are grouped by size
        existing_tire = self.cursor.execute("""
            SELECT id
            FROM tires
            WHERE condition = 'Used' AND size = ?
        """, (size,)).fetchone()

        if existing_tire:
            self.cursor.execute("""
                UPDATE tires
                SET quantity = quantity + ?
                WHERE id = ?
            """, (quantity, existing_tire["id"]))

            tire_id = existing_tire["id"]

        else:
            self.cursor.execute("""
                INSERT INTO tires (
                    barcode,
                    brand,
                    size,
                    condition,
                    quantity
                )
                VALUES (NULL, NULL, ?, 'Used', ?)
            """, (size, quantity))

            tire_id = self.cursor.lastrowid

        self.connection.commit()

        return tire_id


    def add_new_tire(self, barcode, brand, size, quantity):
        if barcode:
            existing_tire = self.cursor.execute("""
                SELECT id
                FROM tires
                WHERE condition = 'New'
                  AND barcode = ?
            """, (barcode,)).fetchone()
        else:
            existing_tire = self.cursor.execute("""
                SELECT id
                FROM tires
                WHERE condition = 'New'
                  AND barcode IS NULL
                  AND LOWER(brand) = LOWER(?)
                  AND size = ?
            """, (brand, size)).fetchone()

        if existing_tire:
            self.cursor.execute("""
                UPDATE tires
                SET quantity = quantity + ?
                WHERE id = ?
            """, (quantity, existing_tire["id"]))

            tire_id = existing_tire["id"]
        else:
            self.cursor.execute("""
                INSERT INTO tires (
                    barcode,
                    brand,
                    size,
                    condition,
                    quantity
                )
                VALUES (?, ?, ?, 'New', ?)
            """, (
                barcode,
                brand,
                size,
                quantity
            ))

            tire_id = self.cursor.lastrowid

        self.connection.commit()

        return tire_id


    def get_inventory(self):
        rows = self.cursor.execute("""
            SELECT id, barcode, brand, size, condition, quantity
            FROM tires
            ORDER BY id
        """).fetchall()

        return [dict(row) for row in rows]


    def find_tire(self, tire_id):
        row = self.cursor.execute("""
            SELECT id, barcode, brand, size, condition, quantity
            FROM tires
            WHERE id = ?
        """, (tire_id,)).fetchone()

        if row is None:
            return None

        return dict(row)

    def update_tire_info(self, tire_id, brand, size, barcode):
        self.cursor.execute("""
            UPDATE tires
            SET brand = ?,
                size = ?,
                barcode = ?
            WHERE id = ?
        """, (
            brand,
            size,
            barcode,
            tire_id
        ))

        self.connection.commit()

        return self.cursor.rowcount > 0

    def find_by_barcode(self, barcode):
        row = self.cursor.execute("""
            SELECT id, barcode, brand, size, condition, quantity
            FROM tires
            WHERE barcode = ? AND condition = 'New'
        """, (barcode,)).fetchone()

        if row is None:
            return None

        return dict(row)


    def sell_tire(self, tire_id, quantity):
        tire = self.cursor.execute("""
            SELECT quantity
            FROM tires
            WHERE id = ?
        """, (tire_id,)).fetchone()

        if tire is None:
            return "not_found"

        if tire["quantity"] < quantity:
            return "insufficient"

        date_sold = datetime.now().isoformat(timespec="seconds")

        try:
            self.cursor.execute("""
                UPDATE tires
                SET quantity = quantity - ?
                WHERE id = ?
            """, (quantity, tire_id))

            self.cursor.execute("""
                INSERT INTO sales (
                    tire_id,
                    quantity,
                    date_sold
                )
                VALUES (?, ?, ?)
            """, (tire_id, quantity, date_sold))

            self.connection.commit()

        except sqlite3.Error:
            self.connection.rollback()
            raise

        return "success"


    def get_todays_sales(self):
        today = datetime.now().date().isoformat()

        rows = self.cursor.execute("""
            SELECT
                sales.id,
                sales.tire_id,
                sales.quantity,
                sales.date_sold,
                tires.barcode,
                tires.brand,
                tires.size,
                tires.condition
            FROM sales
            JOIN tires ON sales.tire_id = tires.id
            WHERE date(sales.date_sold) = ?
            ORDER BY sales.date_sold
        """, (today,)).fetchall()

        return [dict(row) for row in rows]


    def get_sales_by_date(self, target_date):
        if hasattr(target_date, "isoformat"):
            target_date = target_date.isoformat()

        rows = self.cursor.execute("""
            SELECT
                sales.id,
                sales.tire_id,
                sales.quantity,
                sales.date_sold,
                tires.barcode,
                tires.brand,
                tires.size,
                tires.condition
            FROM sales
            JOIN tires ON sales.tire_id = tires.id
            WHERE date(sales.date_sold) = ?
            ORDER BY sales.date_sold
        """, (target_date,)).fetchall()

        return [dict(row) for row in rows]

    def search_by_size(self, size):
        rows = self.cursor.execute("""
            SELECT id, barcode, brand, size, condition, quantity
            FROM tires
            WHERE size = ?
            ORDER BY condition, brand
        """, (size,)).fetchall()

        return [dict(row) for row in rows]

    def backup_database(self, backup_path):
        backup_connection = sqlite3.connect(backup_path)

        try:
            self.connection.backup(backup_connection)

        finally:
            backup_connection.close()

        return True

    def close(self):
        self.connection.close()