from .database import Database
from .tiresUtils import normalize_tire_size

class InventorySystem:
    def __init__(self, db_name="inventory.db"):
        self.database = Database(db_name)


    def add_used_tire(self, size, quantity):
        size = normalize_tire_size(size)

        if size is None:
            print("Invalid tire size. Use format such as 225/45R17.")
            return False

        if quantity <= 0:
            print("Quantity must be greater than 0.")
            return False

        self.database.add_used_tire(size, quantity)

        return True

    def add_new_tire(self, barcode, brand, size, quantity):
        barcode = barcode.strip() if barcode else None
        brand = brand.strip()
        size = normalize_tire_size(size)

        if not brand:
            print("Brand cannot be empty.")
            return False

        if size is None:
            print("Invalid tire size. Use format such as 225/45R17.")
            return False

        if quantity <= 0:
            print("Quantity must be greater than 0.")
            return False

        self.database.add_new_tire(
            barcode,
            brand,
            size,
            quantity
        )

        return True


    def find_tire(self, tire_id):
        return self.database.find_tire(tire_id)

    def find_by_barcode(self, barcode):
        barcode = barcode.strip()

        if not barcode:
            return None

        return self.database.find_by_barcode(barcode)


    def sell_tire(self, tire_id, quantity):
        if quantity <= 0:
            print("Quantity must be greater than 0.")
            return False

        result = self.database.sell_tire(
            tire_id,
            quantity
        )

        if result == "not_found":
            print("Tire not found.")
            return False

        if result == "insufficient":
            print("Not enough inventory.")
            return False

        return True


    def get_inventory(self):
        return self.database.get_inventory()


    def get_todays_sales(self):
        return self.database.get_todays_sales()


    def get_sales_by_date(self, target_date):
        return self.database.get_sales_by_date(target_date)

    def search_by_size(self, size):
        size = normalize_tire_size(size)

        if size is None:
            return []

        return self.database.search_by_size(size)

    def sell_new_tire(self, barcode, quantity):
        barcode = barcode.strip()

        if not barcode:
            print("Barcode cannot be empty.")
            return False

        tire = self.find_by_barcode(barcode)

        if tire is None:
            print("Tire not found.")
            return False

        return self.sell_tire(
            tire["id"],
            quantity
        )


    def sell_used_tire(self, size, quantity):
        size = normalize_tire_size(size)

        if size is None:
            print("Invalid tire size.")
            return False

        results = self.search_by_size(size)

        used_tire = None

        for tire in results:
            if tire["condition"] == "Used":
                used_tire = tire
                break

        if used_tire is None:
            print("Used tire not found.")
            return False

        return self.sell_tire(
            used_tire["id"],
            quantity
        )
    def update_tire_info(
            self,
            tire_id,
            brand,
            size,
            barcode
        ):
            tire = self.find_tire(tire_id)
    
            if tire is None:
                print("Tire not found.")
                return False
    
            size = normalize_tire_size(size)
    
            if size is None:
                print(
                    "Invalid tire size. "
                "   Use format such as 225/45R17."
                )
                return False
    
        # Used tires do not use brand or barcode
            if tire["condition"] == "Used":
                brand = None
                barcode = None
    
            else:
                brand = brand.strip()
    
                if not brand:
                    print("Brand cannot be empty.")
                    return False
    
                barcode = barcode.strip() if barcode else None
    
            # Make sure another new tire doesn't already
            # use this barcode.
                if barcode:
                    existing = self.find_by_barcode(barcode)
    
                    if (
                        existing is not None
                        and existing["id"] != tire_id
                    ):
                        print(
                            "Another tire already uses "
                            "that barcode."
                        )
                        return False
    
            return self.database.update_tire_info(
                tire_id,
                brand,
                size,
                barcode
            )
    def backup_database(self, backup_path):
        try:
            return self.database.backup_database(
                backup_path
            )

        except Exception as error:
            print(f"Backup failed: {error}")
            return False
        
    def close(self):
        self.database.close()