from Classes.inventorySystem import InventorySystem
from datetime import datetime


# =========================================================
# DISPLAY INVENTORY
# =========================================================

def display_inventory(system, include_zero=False):
    inventory = system.get_inventory()

    if not include_zero:
        inventory = [
            tire
            for tire in inventory
            if tire["quantity"] > 0
        ]

    if include_zero:
        print("\n--- ALL INVENTORY RECORDS ---")
    else:
        print("\n--- CURRENT INVENTORY ---")

    if not inventory:
        print("No tires in inventory.")
        return

    for tire in inventory:
        brand = tire["brand"] or "N/A"
        barcode = tire["barcode"] or "N/A"

        print(
            f"ID: {tire['id']} | "
            f"{tire['condition']} | "
            f"Size: {tire['size']} | "
            f"Brand: {brand} | "
            f"Barcode: {barcode} | "
            f"Qty: {tire['quantity']}"
        )


# =========================================================
# ADD NEW TIRE
# =========================================================

def add_new_tire(system):
    print("\n--- ADD NEW TIRE ---")

    barcode = input(
        "Scan/enter barcode "
        "(press Enter if none): "
    ).strip()

    # Barcode exists: check if tire already exists.
    if barcode:
        existing_tire = system.find_by_barcode(barcode)

        if existing_tire:
            print("\nTire found:")
            print(f"Brand: {existing_tire['brand']}")
            print(f"Size: {existing_tire['size']}")
            print(
                f"Current Quantity: "
                f"{existing_tire['quantity']}"
            )

            try:
                quantity = int(
                    input("Quantity being added: ")
                )
            except ValueError:
                print("Quantity must be a whole number.")
                return

            if system.add_new_tire(
                barcode,
                existing_tire["brand"],
                existing_tire["size"],
                quantity
            ):
                updated = system.find_by_barcode(barcode)

                print("Inventory updated.")
                print(
                    f"New Quantity: "
                    f"{updated['quantity']}"
                )

            return

    if barcode:
        print(
            "\nBarcode not found. "
            "Creating a new tire."
        )
    else:
        print(
            "\nNo barcode provided. "
            "Creating tire manually."
        )

    brand = input("Brand: ").strip()

    if not brand:
        print("Brand cannot be empty.")
        return

    size = input(
        "Size (example 225/45R17): "
    ).strip()

    if not size:
        print("Tire size cannot be empty.")
        return

    try:
        quantity = int(input("Quantity: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    if system.add_new_tire(
        barcode,
        brand,
        size,
        quantity
    ):
        print("New tire added.")


# =========================================================
# ADD USED TIRE
# =========================================================

def add_used_tire(system):
    print("\n--- ADD USED TIRE ---")

    size = input(
        "Size (example 225/45R17): "
    ).strip()

    if not size:
        print("Tire size cannot be empty.")
        return

    try:
        quantity = int(input("Quantity: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    if system.add_used_tire(size, quantity):
        print("Used tire inventory updated.")


# =========================================================
# SELL NEW TIRE BY BARCODE
# =========================================================

def sell_new_tire_by_barcode(system):
    print("\n--- SELL NEW TIRE BY BARCODE ---")

    barcode = input("Scan/enter barcode: ").strip()

    if not barcode:
        print("Barcode cannot be empty.")
        return

    tire = system.find_by_barcode(barcode)

    if tire is None:
        print("No new tire found with that barcode.")
        return

    if tire["quantity"] <= 0:
        print("That tire is currently out of stock.")
        return

    print("\nTire found:")
    print(f"Brand: {tire['brand']}")
    print(f"Size: {tire['size']}")
    print(f"Current Quantity: {tire['quantity']}")

    try:
        quantity = int(input("Quantity sold: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    if system.sell_new_tire(barcode, quantity):
        updated = system.find_by_barcode(barcode)

        print("Sale recorded.")
        print(
            f"Remaining Quantity: "
            f"{updated['quantity']}"
        )


# =========================================================
# SELL NEW TIRE MANUALLY
# =========================================================

def sell_new_tire_manually(system):
    print("\n--- MANUAL NEW TIRE SEARCH ---")

    size = input(
        "Enter tire size "
        "(example 225/45R17): "
    ).strip()

    if not size:
        print("Tire size cannot be empty.")
        return

    results = system.search_by_size(size)

    # Only available new tires
    new_tires = [
        tire
        for tire in results
        if tire["condition"] == "New"
        and tire["quantity"] > 0
    ]

    if not new_tires:
        print("No new tires found in that size.")
        return

    print("\nNew tires found:")

    for tire in new_tires:
        brand = tire["brand"] or "N/A"
        barcode = tire["barcode"] or "N/A"

        print(
            f"ID: {tire['id']} | "
            f"Brand: {brand} | "
            f"Size: {tire['size']} | "
            f"Barcode: {barcode} | "
            f"Qty: {tire['quantity']}"
        )

    try:
        tire_id = int(
            input("\nEnter Tire ID to sell: ")
        )
    except ValueError:
        print("Tire ID must be a number.")
        return

    selected = None

    for tire in new_tires:
        if tire["id"] == tire_id:
            selected = tire
            break

    if selected is None:
        print(
            "That Tire ID is not one of "
            "the displayed results."
        )
        return

    print("\nSelected:")
    print(f"Brand: {selected['brand']}")
    print(f"Size: {selected['size']}")
    print(
        f"Current Quantity: "
        f"{selected['quantity']}"
    )

    try:
        quantity = int(input("Quantity sold: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    if system.sell_tire(tire_id, quantity):
        updated = system.find_tire(tire_id)

        print("Sale recorded.")
        print(
            f"Remaining Quantity: "
            f"{updated['quantity']}"
        )


# =========================================================
# SELL NEW TIRE MENU
# =========================================================

def sell_new_tire(system):
    print("\n--- SELL NEW TIRE ---")

    print("""
1. Scan / Enter Barcode
2. Search Manually by Size
0. Cancel
""")

    choice = input("Select an option: ").strip()

    if choice == "1":
        sell_new_tire_by_barcode(system)

    elif choice == "2":
        sell_new_tire_manually(system)

    elif choice == "0":
        return

    else:
        print("Invalid option.")


# =========================================================
# SELL USED TIRE
# =========================================================

def sell_used_tire(system):
    print("\n--- SELL USED TIRE ---")

    size = input(
        "Enter tire size "
        "(example 225/45R17): "
    ).strip()

    if not size:
        print("Tire size cannot be empty.")
        return

    results = system.search_by_size(size)

    used_tire = None

    for tire in results:
        if (
            tire["condition"] == "Used"
            and tire["quantity"] > 0
        ):
            used_tire = tire
            break

    if used_tire is None:
        print(
            "No used tires currently "
            "in stock in that size."
        )
        return

    print("\nUsed tire found:")
    print(f"Size: {used_tire['size']}")
    print(
        f"Current Quantity: "
        f"{used_tire['quantity']}"
    )

    try:
        quantity = int(input("Quantity sold: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    if system.sell_used_tire(size, quantity):
        results = system.search_by_size(size)

        for tire in results:
            if tire["condition"] == "Used":
                print("Sale recorded.")
                print(
                    f"Remaining Quantity: "
                    f"{tire['quantity']}"
                )
                return


# =========================================================
# SELL MENU
# =========================================================

def sell_tire(system):
    print("\n--- SELL TIRE ---")

    print("""
1. New Tire
2. Used Tire
0. Cancel
""")

    choice = input("Select tire type: ").strip()

    if choice == "1":
        sell_new_tire(system)

    elif choice == "2":
        sell_used_tire(system)

    elif choice == "0":
        return

    else:
        print("Invalid option.")


# =========================================================
# SEARCH
# =========================================================

def search_tires(system):
    print("\n--- SEARCH BY SIZE ---")

    size = input("Enter tire size: ").strip()

    if not size:
        print("Tire size cannot be empty.")
        return

    results = system.search_by_size(size)

    # Normal searches show currently available stock
    results = [
        tire
        for tire in results
        if tire["quantity"] > 0
    ]

    if not results:
        print("No tires currently in stock in that size.")
        return

    print(f"\nResults for {size}:")

    for tire in results:
        brand = tire["brand"] or "N/A"
        barcode = tire["barcode"] or "N/A"

        print(
            f"ID: {tire['id']} | "
            f"{tire['condition']} | "
            f"Brand: {brand} | "
            f"Barcode: {barcode} | "
            f"Qty: {tire['quantity']}"
        )


# =========================================================
# TODAY'S SALES
# =========================================================

def display_todays_sales(system):
    print("\n--- TODAY'S SALES ---")

    sales = system.get_todays_sales()

    if not sales:
        print("No sales recorded today.")
        return

    for sale in sales:
        brand = sale["brand"] or "N/A"

        print(
            f"Tire ID: {sale['tire_id']} | "
            f"{sale['condition']} | "
            f"Size: {sale['size']} | "
            f"Brand: {brand} | "
            f"Qty Sold: {sale['quantity']} | "
            f"Date: {sale['date_sold']}"
        )


# =========================================================
# SALES BY DATE
# =========================================================

def display_sales_by_date(system):
    print("\n--- SALES BY DATE ---")

    date_input = input(
        "Enter date (YYYY-MM-DD): "
    ).strip()

    if not date_input:
        print("Date cannot be empty.")
        return

    try:
        target_date = datetime.strptime(
            date_input,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        return

    sales = system.get_sales_by_date(target_date)

    if not sales:
        print("No sales found for that date.")
        return

    print(f"\nSales for {target_date}:")

    for sale in sales:
        brand = sale["brand"] or "N/A"

        print(
            f"Tire ID: {sale['tire_id']} | "
            f"{sale['condition']} | "
            f"Size: {sale['size']} | "
            f"Brand: {brand} | "
            f"Qty Sold: {sale['quantity']} | "
            f"Date: {sale['date_sold']}"
        )


# =========================================================
# EDIT TIRE INFORMATION
# =========================================================

def edit_tire(system):
    print("\n--- EDIT TIRE INFORMATION ---")

    # Include zero-stock records because old records
    # may still need corrections.
    display_inventory(system, include_zero=True)

    try:
        tire_id = int(input("\nEnter Tire ID to edit: "))
    except ValueError:
        print("Tire ID must be a number.")
        return

    tire = system.find_tire(tire_id)

    if tire is None:
        print("Tire not found.")
        return

    print("\nCurrent Information:")
    print(f"Condition: {tire['condition']}")
    print(f"Size: {tire['size']}")
    print(f"Brand: {tire['brand'] or 'N/A'}")
    print(f"Barcode: {tire['barcode'] or 'N/A'}")
    print(f"Quantity: {tire['quantity']}")

    print(
        "\nPress Enter to keep the current value."
    )

    size = input(
        f"Size [{tire['size']}]: "
    ).strip()

    if not size:
        size = tire["size"]

    if tire["condition"] == "New":
        brand = input(
            f"Brand [{tire['brand']}]: "
        ).strip()

        if not brand:
            brand = tire["brand"]

        old_barcode = tire["barcode"] or ""

        barcode = input(
            f"Barcode "
            f"[{old_barcode or 'None'}]: "
        ).strip()

        # Blank means keep existing barcode
        if not barcode:
            barcode = old_barcode

    else:
        brand = None
        barcode = None

    if system.update_tire_info(
        tire_id,
        brand,
        size,
        barcode
    ):
        print("Tire information updated.")


# =========================================================
# MAIN
# =========================================================

def main():
    system = InventorySystem()

    try:
        while True:
            print("""
====================================
        TIRE INVENTORY SYSTEM
====================================

1. Add New Tires
2. Add Used Tires
3. Sell Tires
4. View Current Inventory
5. Search by Tire Size
6. View Today's Sales
7. View Sales by Date
8. Edit Tire Information
9. View All Inventory Records
0. Exit
""")

            choice = input(
                "Select an option: "
            ).strip()

            if choice == "1":
                add_new_tire(system)

            elif choice == "2":
                add_used_tire(system)

            elif choice == "3":
                sell_tire(system)

            elif choice == "4":
                display_inventory(system)

            elif choice == "5":
                search_tires(system)

            elif choice == "6":
                display_todays_sales(system)

            elif choice == "7":
                display_sales_by_date(system)

            elif choice == "8":
                edit_tire(system)

            elif choice == "9":
                display_inventory(
                    system,
                    include_zero=True
                )

            elif choice == "0":
                print("Closing inventory system.")
                break

            else:
                print("Invalid option.")

    finally:
        system.close()


if __name__ == "__main__":
    main()