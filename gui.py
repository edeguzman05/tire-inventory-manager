import json
import os
import re

from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

from Classes.inventorySystem import InventorySystem


# =========================================================
# APPLICATION FILE LOCATIONS
# =========================================================

LOCAL_APP_DATA = os.getenv("LOCALAPPDATA") or str(Path.home())

APP_DATA = Path(LOCAL_APP_DATA) / "TireInventory"

APP_DATA.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = APP_DATA / "inventory.db"
SETTINGS_PATH = APP_DATA / "settings.json"


# =========================================================
# STORE SETTINGS
# =========================================================

def load_store_name():
    if not SETTINGS_PATH.exists():
        return None

    try:
        with open(
            SETTINGS_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            settings = json.load(file)

        store_name = settings.get("store_name")

        if store_name:
            return store_name.strip()

    except (
        OSError,
        json.JSONDecodeError
    ):
        pass

    return None


def save_store_name(store_name):
    settings = {
        "store_name": store_name
    }

    with open(
        SETTINGS_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            settings,
            file,
            indent=4
        )


def safe_filename(text):
    text = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        text
    )

    text = text.strip("_")

    if not text:
        return "Store"

    return text


# =========================================================
# MAIN APPLICATION
# =========================================================

class TireInventoryApp:

    def __init__(self, root):
        self.root = root
        self.cancelled = False

        # Hide the blank Tk window while first-time
        # store setup is taking place.
        self.root.withdraw()

        # -------------------------------------------------
        # STORE NAME
        # -------------------------------------------------

        self.store_name = load_store_name()

        if not self.store_name:

            self.store_name = simpledialog.askstring(
                "Store Setup",
                (
                    "Welcome to Tire Inventory.\n\n"
                    "Enter the name of this store/location:"
                ),
                parent=self.root
            )

            # Closing/cancelling first-time setup exits
            # instead of creating an unnamed store.
            if self.store_name is None:
                self.cancelled = True
                self.root.destroy()
                return

            self.store_name = self.store_name.strip()

            if not self.store_name:
                messagebox.showwarning(
                    "Invalid Store Name",
                    "Store name cannot be empty.",
                    parent=self.root
                )

                self.cancelled = True
                self.root.destroy()
                return

            save_store_name(
                self.store_name
            )

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.root.title(
            f"Tire Inventory - {self.store_name}"
        )

        self.root.minsize(
            950,
            600
        )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        self.system = InventorySystem(
            str(DATABASE_PATH)
        )

        self.show_all = tk.BooleanVar(
            value=False
        )

        # Build exactly once.
        self.build_gui()

        # Load inventory.
        self.refresh_inventory()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_program
        )

        # Reveal finished GUI.
        self.root.deiconify()

        # Maximize on Windows.
        try:
            self.root.state("zoomed")

        except tk.TclError:
            self.root.geometry("1200x720")


    # =====================================================
    # BUILD GUI
    # =====================================================

    def build_gui(self):

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = ttk.Label(
            self.root,
            text="Tire Inventory System",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=(15, 2)
        )


        self.store_label = ttk.Label(
            self.root,
            text=self.store_name,
            font=("Arial", 14)
        )

        self.store_label.pack(
            pady=(0, 12)
        )


        # -------------------------------------------------
        # MAIN BUTTONS
        # -------------------------------------------------

        button_frame = ttk.Frame(
            self.root
        )

        button_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )


        ttk.Button(
            button_frame,
            text="Add New Tires",
            command=self.add_new_tire
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Add Used Tires",
            command=self.add_used_tire
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Sell Selected",
            command=self.sell_selected
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Edit Selected",
            command=self.edit_selected
        ).grid(
            row=0,
            column=3,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Today's Sales",
            command=self.show_todays_sales
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Sales By Date",
            command=self.show_sales_by_date
        ).grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Backup Inventory",
            command=self.backup_inventory
        ).grid(
            row=1,
            column=2,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Refresh Inventory",
            command=self.refresh_inventory
        ).grid(
            row=1,
            column=3,
            padx=5,
            pady=5,
            sticky="ew"
        )


        ttk.Button(
            button_frame,
            text="Change Store Name",
            command=self.change_store_name
        ).grid(
            row=2,
            column=0,
            columnspan=4,
            padx=5,
            pady=5,
            sticky="ew"
        )


        for column in range(4):
            button_frame.columnconfigure(
                column,
                weight=1
            )


        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        search_frame = ttk.LabelFrame(
            self.root,
            text="Search Inventory"
        )

        search_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )


        ttk.Label(
            search_frame,
            text="Tire Size:"
        ).grid(
            row=0,
            column=0,
            padx=(10, 5),
            pady=10
        )


        self.size_search = ttk.Entry(
            search_frame,
            width=18
        )

        self.size_search.grid(
            row=0,
            column=1,
            padx=5,
            pady=10
        )

        self.size_search.bind(
            "<Return>",
            lambda event: self.search_by_size()
        )


        ttk.Button(
            search_frame,
            text="Search Size",
            command=self.search_by_size
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=10
        )


        ttk.Label(
            search_frame,
            text="Barcode:"
        ).grid(
            row=0,
            column=3,
            padx=(25, 5),
            pady=10
        )


        self.barcode_search = ttk.Entry(
            search_frame,
            width=24
        )

        self.barcode_search.grid(
            row=0,
            column=4,
            padx=5,
            pady=10
        )


        # Most USB barcode scanners send Enter after
        # transmitting the barcode.
        self.barcode_search.bind(
            "<Return>",
            lambda event: self.find_by_barcode()
        )


        ttk.Button(
            search_frame,
            text="Find Barcode",
            command=self.find_by_barcode
        ).grid(
            row=0,
            column=5,
            padx=5,
            pady=10
        )


        ttk.Button(
            search_frame,
            text="Clear Search",
            command=self.clear_search
        ).grid(
            row=0,
            column=6,
            padx=10,
            pady=10
        )


        # -------------------------------------------------
        # INVENTORY OPTIONS
        # -------------------------------------------------

        option_frame = ttk.Frame(
            self.root
        )

        option_frame.pack(
            fill="x",
            padx=20
        )


        ttk.Checkbutton(
            option_frame,
            text="Show zero-stock records",
            variable=self.show_all,
            command=self.refresh_inventory
        ).pack(
            side="left"
        )


        # -------------------------------------------------
        # INVENTORY TABLE
        # -------------------------------------------------

        table_frame = ttk.Frame(
            self.root
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )


        columns = (
            "id",
            "condition",
            "brand",
            "size",
            "barcode",
            "quantity"
        )


        self.inventory_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )


        headings = {
            "id": "ID",
            "condition": "Condition",
            "brand": "Brand",
            "size": "Size",
            "barcode": "Barcode",
            "quantity": "Quantity"
        }


        for column, heading in headings.items():

            self.inventory_table.heading(
                column,
                text=heading
            )


        self.inventory_table.column(
            "id",
            width=60,
            anchor="center"
        )

        self.inventory_table.column(
            "condition",
            width=100,
            anchor="center"
        )

        self.inventory_table.column(
            "brand",
            width=190
        )

        self.inventory_table.column(
            "size",
            width=150,
            anchor="center"
        )

        self.inventory_table.column(
            "barcode",
            width=210,
            anchor="center"
        )

        self.inventory_table.column(
            "quantity",
            width=100,
            anchor="center"
        )


        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.inventory_table.yview
        )


        horizontal_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.inventory_table.xview
        )


        self.inventory_table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )


        self.inventory_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


        vertical_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )


        horizontal_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )


        table_frame.rowconfigure(
            0,
            weight=1
        )


        table_frame.columnconfigure(
            0,
            weight=1
        )


        # -------------------------------------------------
        # STATUS BAR
        # -------------------------------------------------

        self.status = ttk.Label(
            self.root,
            text=""
        )

        self.status.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )


    # =====================================================
    # REFRESH INVENTORY
    # =====================================================

    def refresh_inventory(
        self,
        records=None
    ):

        for row in self.inventory_table.get_children():
            self.inventory_table.delete(row)


        if records is None:
            records = self.system.get_inventory()


        if not self.show_all.get():

            records = [
                tire
                for tire in records
                if tire["quantity"] > 0
            ]


        for tire in records:

            self.inventory_table.insert(
                "",
                "end",
                iid=str(tire["id"]),
                values=(
                    tire["id"],
                    tire["condition"],
                    tire["brand"] or "N/A",
                    tire["size"],
                    tire["barcode"] or "N/A",
                    tire["quantity"]
                )
            )


        self.status.configure(
            text=(
                f"Store: {self.store_name}    |    "
                f"Records shown: {len(records)}"
            )
        )


    # =====================================================
    # GET SELECTED TIRE
    # =====================================================

    def selected_tire(self):

        selection = self.inventory_table.selection()

        if not selection:

            messagebox.showwarning(
                "No Tire Selected",
                "Select a tire from the inventory table first.",
                parent=self.root
            )

            return None


        tire_id = int(
            selection[0]
        )


        return self.system.find_tire(
            tire_id
        )


    # =====================================================
    # ADD NEW TIRE
    # =====================================================

    def add_new_tire(self):

        barcode = simpledialog.askstring(
            "Add New Tire",
            (
                "Scan or enter barcode.\n\n"
                "Leave blank if this tire does not "
                "have a barcode."
            ),
            parent=self.root
        )


        if barcode is None:
            return


        barcode = barcode.strip()


        # -------------------------------------------------
        # EXISTING BARCODE
        # -------------------------------------------------

        if barcode:

            existing = self.system.find_by_barcode(
                barcode
            )

            if existing:

                quantity = simpledialog.askinteger(
                    "Existing Tire",
                    (
                        "This barcode already exists.\n\n"
                        f"Brand: {existing['brand']}\n"
                        f"Size: {existing['size']}\n"
                        f"Current quantity: "
                        f"{existing['quantity']}\n\n"
                        "Quantity being added:"
                    ),
                    minvalue=1,
                    parent=self.root
                )


                if quantity is None:
                    return


                result = self.system.add_new_tire(
                    barcode,
                    existing["brand"],
                    existing["size"],
                    quantity
                )


                if result:

                    updated = self.system.find_by_barcode(
                        barcode
                    )

                    messagebox.showinfo(
                        "Inventory Updated",
                        (
                            "Inventory updated successfully.\n\n"
                            f"New quantity: "
                            f"{updated['quantity']}"
                        ),
                        parent=self.root
                    )

                    self.refresh_inventory()


                return


        # -------------------------------------------------
        # NEW PRODUCT
        # -------------------------------------------------

        brand = simpledialog.askstring(
            "Add New Tire",
            "Brand:",
            parent=self.root
        )


        if brand is None:
            return


        brand = brand.strip()


        if not brand:

            messagebox.showwarning(
                "Missing Brand",
                "Brand cannot be empty.",
                parent=self.root
            )

            return


        size = simpledialog.askstring(
            "Add New Tire",
            (
                "Tire size:\n\n"
                "Examples:\n"
                "225/45R17\n"
                "P215/60R16\n"
                "LT245/75R16\n"
                "ST205/75R15"
            ),
            parent=self.root
        )


        if size is None:
            return


        quantity = simpledialog.askinteger(
            "Add New Tire",
            "Quantity:",
            minvalue=1,
            parent=self.root
        )


        if quantity is None:
            return


        result = self.system.add_new_tire(
            barcode,
            brand,
            size,
            quantity
        )


        if result:

            messagebox.showinfo(
                "Inventory Updated",
                "New tire inventory was updated successfully.",
                parent=self.root
            )

            self.refresh_inventory()


        else:

            messagebox.showerror(
                "Unable to Add Tire",
                (
                    "The tire could not be added.\n\n"
                    "Check the brand, tire size, "
                    "and quantity."
                ),
                parent=self.root
            )


    # =====================================================
    # ADD USED TIRE
    # =====================================================

    def add_used_tire(self):

        size = simpledialog.askstring(
            "Add Used Tire",
            (
                "Tire size:\n\n"
                "Examples:\n"
                "225/45R17\n"
                "P215/60R16\n"
                "LT245/75R16\n"
                "ST205/75R15"
            ),
            parent=self.root
        )


        if size is None:
            return


        quantity = simpledialog.askinteger(
            "Add Used Tire",
            "Quantity:",
            minvalue=1,
            parent=self.root
        )


        if quantity is None:
            return


        result = self.system.add_used_tire(
            size,
            quantity
        )


        if result:

            messagebox.showinfo(
                "Inventory Updated",
                "Used tire inventory was updated successfully.",
                parent=self.root
            )

            self.refresh_inventory()


        else:

            messagebox.showerror(
                "Unable to Add Tire",
                "Check the tire size and quantity.",
                parent=self.root
            )


    # =====================================================
    # SELL SELECTED TIRE
    # =====================================================

    def sell_selected(self):

        tire = self.selected_tire()


        if tire is None:
            return


        if tire["quantity"] <= 0:

            messagebox.showwarning(
                "Out of Stock",
                "This tire is currently out of stock.",
                parent=self.root
            )

            return


        quantity = simpledialog.askinteger(
            "Sell Tire",
            (
                f"{tire['condition']} Tire\n\n"
                f"Brand: {tire['brand'] or 'N/A'}\n"
                f"Size: {tire['size']}\n"
                f"Barcode: {tire['barcode'] or 'N/A'}\n"
                f"Available: {tire['quantity']}\n\n"
                "Quantity sold:"
            ),
            minvalue=1,
            maxvalue=tire["quantity"],
            parent=self.root
        )


        if quantity is None:
            return


        confirm = messagebox.askyesno(
            "Confirm Sale",
            (
                f"Sell {quantity} tire(s)?\n\n"
                f"Brand: {tire['brand'] or 'N/A'}\n"
                f"Size: {tire['size']}"
            ),
            parent=self.root
        )


        if not confirm:
            return


        result = self.system.sell_tire(
            tire["id"],
            quantity
        )


        if result:

            updated = self.system.find_tire(
                tire["id"]
            )

            messagebox.showinfo(
                "Sale Recorded",
                (
                    "Sale recorded successfully.\n\n"
                    f"Remaining quantity: "
                    f"{updated['quantity']}"
                ),
                parent=self.root
            )

            self.refresh_inventory()


        else:

            messagebox.showerror(
                "Sale Failed",
                "The sale could not be completed.",
                parent=self.root
            )


    # =====================================================
    # SEARCH BY SIZE
    # =====================================================

    def search_by_size(self):

        size = self.size_search.get().strip()


        if not size:

            messagebox.showwarning(
                "Missing Size",
                "Enter a tire size.",
                parent=self.root
            )

            return


        results = self.system.search_by_size(
            size
        )


        # Respect the zero-stock checkbox when determining
        # whether there is anything visible.
        if self.show_all.get():
            visible_results = results

        else:
            visible_results = [
                tire
                for tire in results
                if tire["quantity"] > 0
            ]


        if not visible_results:

            if results and not self.show_all.get():

                messagebox.showinfo(
                    "Out of Stock",
                    (
                        "Matching tire records exist, "
                        "but they are currently out of stock.\n\n"
                        "Enable 'Show zero-stock records' "
                        "to view them."
                    ),
                    parent=self.root
                )

            else:

                messagebox.showinfo(
                    "No Results",
                    "No tires were found in that size.",
                    parent=self.root
                )

            return


        self.refresh_inventory(
            results
        )


    # =====================================================
    # FIND BY BARCODE
    # =====================================================

    def find_by_barcode(self):

        barcode = self.barcode_search.get().strip()


        if not barcode:

            messagebox.showwarning(
                "Missing Barcode",
                "Scan or enter a barcode.",
                parent=self.root
            )

            return


        tire = self.system.find_by_barcode(
            barcode
        )


        if tire is None:

            messagebox.showinfo(
                "Not Found",
                "No tire was found with that barcode.",
                parent=self.root
            )

            return


        # Barcode lookup should still find a zero-stock
        # product.
        self.show_all.set(True)

        self.refresh_inventory(
            [tire]
        )


        item_id = str(
            tire["id"]
        )


        self.inventory_table.selection_set(
            item_id
        )

        self.inventory_table.focus(
            item_id
        )

        self.inventory_table.see(
            item_id
        )


    # =====================================================
    # CLEAR SEARCH
    # =====================================================

    def clear_search(self):

        self.size_search.delete(
            0,
            tk.END
        )

        self.barcode_search.delete(
            0,
            tk.END
        )

        self.show_all.set(False)

        self.refresh_inventory()


    # =====================================================
    # EDIT SELECTED TIRE
    # =====================================================

    def edit_selected(self):

        tire = self.selected_tire()


        if tire is None:
            return


        window = tk.Toplevel(
            self.root
        )

        window.title(
            f"Edit Tire {tire['id']}"
        )

        window.geometry(
            "430x350"
        )

        window.resizable(
            False,
            False
        )

        window.transient(
            self.root
        )

        window.grab_set()


        ttk.Label(
            window,
            text=f"Edit Tire ID {tire['id']}",
            font=("Arial", 16, "bold")
        ).pack(
            pady=15
        )


        form = ttk.Frame(
            window
        )

        form.pack(
            fill="x",
            padx=25
        )


        # -------------------------------------------------
        # CONDITION
        # -------------------------------------------------

        ttk.Label(
            form,
            text="Condition:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=7
        )


        ttk.Label(
            form,
            text=tire["condition"]
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=5,
            pady=7
        )


        # -------------------------------------------------
        # SIZE
        # -------------------------------------------------

        ttk.Label(
            form,
            text="Size:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=7
        )


        size_var = tk.StringVar(
            value=tire["size"]
        )


        ttk.Entry(
            form,
            textvariable=size_var
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5,
            pady=7
        )


        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        ttk.Label(
            form,
            text="Brand:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=7
        )


        brand_var = tk.StringVar(
            value=tire["brand"] or ""
        )


        brand_entry = ttk.Entry(
            form,
            textvariable=brand_var
        )


        brand_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=5,
            pady=7
        )


        # -------------------------------------------------
        # BARCODE
        # -------------------------------------------------

        ttk.Label(
            form,
            text="Barcode:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=5,
            pady=7
        )


        barcode_var = tk.StringVar(
            value=tire["barcode"] or ""
        )


        barcode_entry = ttk.Entry(
            form,
            textvariable=barcode_var
        )


        barcode_entry.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=5,
            pady=7
        )


        # -------------------------------------------------
        # QUANTITY - READ ONLY
        # -------------------------------------------------

        ttk.Label(
            form,
            text="Quantity:"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            padx=5,
            pady=7
        )


        ttk.Label(
            form,
            text=str(tire["quantity"])
        ).grid(
            row=4,
            column=1,
            sticky="w",
            padx=5,
            pady=7
        )


        form.columnconfigure(
            1,
            weight=1
        )


        # Used tires do not use brand or barcode.
        if tire["condition"] == "Used":

            brand_entry.configure(
                state="disabled"
            )

            barcode_entry.configure(
                state="disabled"
            )


        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        def save():

            result = self.system.update_tire_info(
                tire["id"],
                brand_var.get(),
                size_var.get(),
                barcode_var.get()
            )


            if result:

                messagebox.showinfo(
                    "Updated",
                    "Tire information was updated.",
                    parent=window
                )

                window.destroy()

                self.refresh_inventory()


            else:

                messagebox.showerror(
                    "Unable to Update",
                    (
                        "The tire could not be updated.\n\n"
                        "Check the tire size, brand, "
                        "and barcode.\n\n"
                        "The barcode may already belong "
                        "to another tire."
                    ),
                    parent=window
                )


        ttk.Button(
            window,
            text="Save Changes",
            command=save
        ).pack(
            pady=20
        )


    # =====================================================
    # SALES DISPLAY
    # =====================================================

    def display_sales(
        self,
        title,
        sales
    ):

        window = tk.Toplevel(
            self.root
        )


        window.title(
            f"{title} - {self.store_name}"
        )

        window.geometry(
            "1000x450"
        )


        ttk.Label(
            window,
            text=title,
            font=("Arial", 18, "bold")
        ).pack(
            pady=(15, 2)
        )


        ttk.Label(
            window,
            text=self.store_name,
            font=("Arial", 11)
        ).pack(
            pady=(0, 10)
        )


        table_frame = ttk.Frame(
            window
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )


        columns = (
            "sale_id",
            "tire_id",
            "condition",
            "brand",
            "size",
            "quantity",
            "date"
        )


        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )


        headings = {
            "sale_id": "Sale ID",
            "tire_id": "Tire ID",
            "condition": "Condition",
            "brand": "Brand",
            "size": "Size",
            "quantity": "Qty Sold",
            "date": "Date Sold"
        }


        for column in columns:

            table.heading(
                column,
                text=headings[column]
            )


        table.column(
            "sale_id",
            width=75,
            anchor="center"
        )

        table.column(
            "tire_id",
            width=75,
            anchor="center"
        )

        table.column(
            "condition",
            width=100,
            anchor="center"
        )

        table.column(
            "brand",
            width=170
        )

        table.column(
            "size",
            width=130,
            anchor="center"
        )

        table.column(
            "quantity",
            width=100,
            anchor="center"
        )

        table.column(
            "date",
            width=190,
            anchor="center"
        )


        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=table.yview
        )


        table.configure(
            yscrollcommand=scrollbar.set
        )


        for sale in sales:

            table.insert(
                "",
                "end",
                values=(
                    sale["id"],
                    sale["tire_id"],
                    sale["condition"],
                    sale["brand"] or "N/A",
                    sale["size"],
                    sale["quantity"],
                    sale["date_sold"]
                )
            )


        table.pack(
            side="left",
            fill="both",
            expand=True
        )


        scrollbar.pack(
            side="right",
            fill="y"
        )


        if not sales:

            ttk.Label(
                window,
                text="No sales found."
            ).pack(
                pady=10
            )


    # =====================================================
    # TODAY'S SALES
    # =====================================================

    def show_todays_sales(self):

        sales = self.system.get_todays_sales()

        self.display_sales(
            "Today's Sales",
            sales
        )


    # =====================================================
    # SALES BY DATE
    # =====================================================

    def show_sales_by_date(self):

        value = simpledialog.askstring(
            "Sales By Date",
            "Enter date (YYYY-MM-DD):",
            parent=self.root
        )


        if value is None:
            return


        try:

            target_date = datetime.strptime(
                value.strip(),
                "%Y-%m-%d"
            ).date()


        except ValueError:

            messagebox.showerror(
                "Invalid Date",
                "Use the format YYYY-MM-DD.",
                parent=self.root
            )

            return


        sales = self.system.get_sales_by_date(
            target_date
        )


        self.display_sales(
            f"Sales for {target_date}",
            sales
        )


    # =====================================================
    # BACKUP INVENTORY
    # =====================================================

    def backup_inventory(self):

        backup_folder = filedialog.askdirectory(
            title="Choose Backup Location",
            parent=self.root
        )


        if not backup_folder:
            return


        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )


        store_filename = safe_filename(
            self.store_name
        )


        backup_filename = (
            f"{store_filename}_"
            f"inventory_backup_"
            f"{timestamp}.db"
        )


        backup_path = (
            Path(backup_folder)
            / backup_filename
        )


        result = self.system.backup_database(
            str(backup_path)
        )


        if result:

            messagebox.showinfo(
                "Backup Complete",
                (
                    "Inventory backup created successfully.\n\n"
                    f"Store: {self.store_name}\n\n"
                    f"{backup_path}"
                ),
                parent=self.root
            )


        else:

            messagebox.showerror(
                "Backup Failed",
                (
                    "The inventory backup could "
                    "not be created."
                ),
                parent=self.root
            )


    # =====================================================
    # CHANGE STORE NAME
    # =====================================================

    def change_store_name(self):

        new_name = simpledialog.askstring(
            "Change Store Name",
            "Store/location name:",
            initialvalue=self.store_name,
            parent=self.root
        )


        if new_name is None:
            return


        new_name = new_name.strip()


        if not new_name:

            messagebox.showwarning(
                "Invalid Store Name",
                "Store name cannot be empty.",
                parent=self.root
            )

            return


        self.store_name = new_name


        save_store_name(
            self.store_name
        )


        self.store_label.configure(
            text=self.store_name
        )


        self.root.title(
            f"Tire Inventory - {self.store_name}"
        )


        self.refresh_inventory()


        messagebox.showinfo(
            "Store Updated",
            (
                "Store name changed to:\n\n"
                f"{self.store_name}"
            ),
            parent=self.root
        )


    # =====================================================
    # CLOSE PROGRAM
    # =====================================================

    def close_program(self):

        self.system.close()

        self.root.destroy()


# =========================================================
# START PROGRAM
# =========================================================

def main():

    root = tk.Tk()

    app = TireInventoryApp(
        root
    )


    if app.cancelled:
        return


    root.mainloop()


if __name__ == "__main__":
    main()