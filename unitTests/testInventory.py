import unittest
from datetime import datetime

from Classes.inventorySystem import InventorySystem


class TestInventorySystem(unittest.TestCase):

    def setUp(self):
        # Every test gets its own empty temporary database
        self.system = InventorySystem(":memory:")

    def tearDown(self):
        # Close the temporary database after each test
        self.system.close()


    def test_add_new_tire(self):
        self.system.add_new_tire(
            "111",
            "Pirelli",
            "245/40R18",
            10
        )

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["condition"], "New")
        self.assertEqual(inventory[0]["brand"], "Pirelli")
        self.assertEqual(inventory[0]["size"], "245/40R18")
        self.assertEqual(inventory[0]["quantity"], 10)


    def test_add_existing_new_tire_updates_quantity(self):
        self.system.add_new_tire(
            "111",
            "Pirelli",
            "245/40R18",
            10
        )

        self.system.add_new_tire(
            "111",
            "Pirelli",
            "245/40R18",
            5
        )

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["quantity"], 15)


    def test_add_used_tire(self):
        self.system.add_used_tire(
            "205/55R16",
            4
        )

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["condition"], "Used")
        self.assertEqual(inventory[0]["size"], "205/55R16")
        self.assertEqual(inventory[0]["quantity"], 4)


    def test_find_tire_success_and_fail(self):
        self.system.add_used_tire(
            "205/55R16",
            4
        )

        found_tire = self.system.find_tire(1)
        missing_tire = self.system.find_tire(99)

        self.assertIsNotNone(found_tire)
        self.assertEqual(found_tire["id"], 1)
        self.assertIsNone(missing_tire)


    def test_sell_tire_success(self):
        self.system.add_new_tire(
            "222",
            "Bridgestone",
            "215/60R16",
            8
        )

        self.system.sell_tire(1, 3)

        tire = self.system.find_tire(1)

        self.assertEqual(tire["quantity"], 5)

        sales = self.system.get_todays_sales()

        self.assertEqual(len(sales), 1)
        self.assertEqual(sales[0]["quantity"], 3)


    def test_sell_tire_insufficient_inventory(self):
        self.system.add_used_tire(
            "225/45R17",
            2
        )

        self.system.sell_tire(1, 5)

        tire = self.system.find_tire(1)

        self.assertEqual(tire["quantity"], 2)

        sales = self.system.get_todays_sales()

        self.assertEqual(len(sales), 0)


    def test_get_todays_sales(self):
        self.system.add_used_tire(
            "225/45R17",
            10
        )

        self.system.sell_tire(1, 2)
        self.system.sell_tire(1, 1)

        todays_sales = self.system.get_todays_sales()

        self.assertEqual(len(todays_sales), 2)
        self.assertEqual(todays_sales[0]["quantity"], 2)
        self.assertEqual(todays_sales[1]["quantity"], 1)


    def test_get_sales_by_date(self):
        self.system.add_used_tire(
            "225/45R17",
            10
        )

        self.system.sell_tire(1, 2)

        today = datetime.now().date()

        sales = self.system.get_sales_by_date(today)

        self.assertEqual(len(sales), 1)
        self.assertEqual(sales[0]["quantity"], 2)


    def test_can_add_new_tire_without_barcode(self):
        result = self.system.add_new_tire(
            "",
            "Michelin",
            "225/45R17",
        4
        )

        self.assertTrue(result)

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["brand"], "Michelin")
        self.assertEqual(inventory[0]["size"], "225/45R17")
        self.assertIsNone(inventory[0]["barcode"])
        self.assertEqual(inventory[0]["quantity"], 4)


    def test_cannot_add_negative_used_quantity(self):
        self.system.add_used_tire(
            "225/45R17",
            -5
        )

        self.assertEqual(
            len(self.system.get_inventory()),
            0
        )


    def test_cannot_add_zero_new_quantity(self):
        self.system.add_new_tire(
            "111",
            "Pirelli",
            "245/40R18",
            0
        )

        self.assertEqual(
            len(self.system.get_inventory()),
            0
        )
    def test_search_by_size(self):
        self.system.add_new_tire(
            "111",
            "Michelin",
            "225/45R17",
            4
        )

        self.system.add_used_tire(
            "225/45R17",
            3
        )

        self.system.add_new_tire(
            "222",
            "Goodyear",
            "205/55R16",
            5
        )

        results = self.system.search_by_size("225/45R17")

        self.assertEqual(len(results), 2)

        for tire in results:
            self.assertEqual(
                tire["size"],
                "225/45R17"
            )

    def test_find_tire_by_barcode(self):
        self.system.add_new_tire(
            "123456",
            "Michelin",
            "225/45R17",
            10
        )

        tire = self.system.find_by_barcode("123456")

        self.assertIsNotNone(tire)
        self.assertEqual(tire["barcode"], "123456")
        self.assertEqual(tire["brand"], "Michelin")
        self.assertEqual(tire["size"], "225/45R17")
        self.assertEqual(tire["quantity"], 10)

    def test_find_nonexistent_barcode(self):
        tire = self.system.find_by_barcode("999999")

        self.assertIsNone(tire)

    def test_can_add_new_tire_without_barcode(self):
        result = self.system.add_new_tire(
            "",
            "Michelin",
            "225/45R17",
            4
        )

        self.assertTrue(result)

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["brand"], "Michelin")
        self.assertEqual(inventory[0]["size"], "225/45R17")
        self.assertIsNone(inventory[0]["barcode"])
        self.assertEqual(inventory[0]["quantity"], 4)

    def test_cannot_add_new_tire_without_brand(self):
        result = self.system.add_new_tire(
            "123456",
            "",
            "225/45R17",
            4
        )

        self.assertFalse(result)
        self.assertEqual(len(self.system.get_inventory()), 0)


    def test_cannot_add_used_tire_without_size(self):
        result = self.system.add_used_tire("", 4)

        self.assertFalse(result)
        self.assertEqual(len(self.system.get_inventory()), 0)

    def test_sell_new_tire_by_barcode(self):
        self.system.add_new_tire(
            "ABC123",
            "Michelin",
            "225/45R17",
            10
        )

        result = self.system.sell_new_tire(
            "ABC123",
            3
        )

        tire = self.system.find_by_barcode(
            "ABC123"
        )

        self.assertTrue(result)
        self.assertEqual(tire["quantity"], 7)

        sales = self.system.get_todays_sales()

        self.assertEqual(len(sales), 1)
        self.assertEqual(sales[0]["quantity"], 3)

    def test_sell_used_tire_by_size(self):
        self.system.add_used_tire(
            "225/45R17",
            6
        )

        result = self.system.sell_used_tire(
            "225/45R17",
            2
        )

        results = self.system.search_by_size(
            "225/45R17"
        )

        used_tire = None

        for tire in results:
            if tire["condition"] == "Used":
                used_tire = tire
                break

        self.assertTrue(result)
        self.assertIsNotNone(used_tire)
        self.assertEqual(used_tire["quantity"], 4)


    def test_tire_size_normalizes_lowercase_r(self):
        self.system.add_used_tire(
            "225/45r17",
            4
        )

        inventory = self.system.get_inventory()

        self.assertEqual(
            inventory[0]["size"],
            "225/45R17"
        )


    def test_invalid_tire_size_is_rejected(self):
        result = self.system.add_used_tire(
            "banana",
            4
        )

        self.assertFalse(result)
        self.assertEqual(
            len(self.system.get_inventory()),
            0
        )


    def test_same_normalized_used_size_combines(self):
        self.system.add_used_tire(
            "225/45R17",
            4
        )

        self.system.add_used_tire(
            "225/45r17",
            3
        )

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(
            inventory[0]["quantity"],
            7
        )
    def test_blank_barcode_cannot_be_found(self):
        tire = self.system.find_by_barcode("")
        self.assertIsNone(tire)

    def test_blank_barcode_cannot_be_sold(self):
        result = self.system.sell_new_tire("", 2)
        self.assertFalse(result)

    def test_barcode_less_new_tires_combine_by_brand_and_size(self):
        self.system.add_new_tire(
            "",
            "Michelin",
            "225/45R17",
            4
        )

        self.system.add_new_tire(
            "",
            "Michelin",
            "225/45R17",
            3
        )

        inventory = self.system.get_inventory()

        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["quantity"], 7)
        
    def test_update_new_tire_information(self):
        self.system.add_new_tire(
            "",
            "Michellin",
            "225/45R17",
            4
        )

        result = self.system.update_tire_info(
            1,
            "Michelin",
            "225/45R17",
            ""
        )

        tire = self.system.find_tire(1)

        self.assertTrue(result)
        self.assertEqual(tire["brand"], "Michelin")
        self.assertEqual(tire["size"], "225/45R17")
        self.assertIsNone(tire["barcode"])


    def test_cannot_reuse_existing_barcode(self):
        self.system.add_new_tire(
            "111",
            "Michelin",
            "225/45R17",
            4
        )

        self.system.add_new_tire(
            "222",
            "Goodyear",
            "205/55R16",
            4
        )

        result = self.system.update_tire_info(
            2,
            "Goodyear",
            "205/55R16",
            "111"
        )

        self.assertFalse(result)
    def test_accepts_p_metric_tire_size(self):
        result = self.system.add_new_tire(
        "",
            "Michelin",
            "P215/60R16",
            4
        )

        self.assertTrue(result)

        tire = self.system.get_inventory()[0]

        self.assertEqual(
            tire["size"],
            "P215/60R16"
        )


    def test_accepts_lt_tire_size(self):
        result = self.system.add_new_tire(
            "",
            "BFGoodrich",
            "LT245/75R16",
            4
        )

        self.assertTrue(result)


    def test_tire_prefix_normalizes_case(self):
        self.system.add_new_tire(
            "",
            "Michelin",
            "p215/60r16",
            4
        )

        tire = self.system.get_inventory()[0]

        self.assertEqual(
            tire["size"],
            "P215/60R16"
        )

if __name__ == "__main__":
    unittest.main()