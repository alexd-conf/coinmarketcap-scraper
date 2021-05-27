import unittest
from unittest.mock import MagicMock
from scraper.scraper import get_table_with_data, row_not_loaded, \
                            reload_table_rows, get_coin_name, get_coin_symbol, \
                            get_coin_price, get_coin_change24h, get_coin_change7d, \
                            get_coin_market_cap, get_coin_volume24h, get_coin_circulating_supply


class TestStringMethods(unittest.TestCase):

    def test_get_table_with_data_raises_error(self):
        self.assertRaises(AttributeError, get_table_with_data, "")

    def test_row_not_loaded_true(self):
        def has_attr(arg):
            return True
        row_mock = MagicMock()
        row_mock.has_attr = has_attr
        self.assertTrue(row_not_loaded(row_mock))

    def test_row_not_loaded_false(self):
        def has_attr(arg):
            return False
        row_mock = MagicMock()
        row_mock.has_attr = has_attr
        self.assertFalse(row_not_loaded(row_mock))

    def test_reload_table_rows_raises_error(self):
        driver_mock = MagicMock(page_source="")
        self.assertRaises(AttributeError, reload_table_rows, driver_mock)

    def test_get_coin_name_result_none(self):
        self.assertIsNone(get_coin_name([]))

    def test_get_coin_symbol_result_none(self):
        self.assertIsNone(get_coin_symbol([]))

    def test_get_coin_price_result_none(self):
        self.assertIsNone(get_coin_price([]))

    def test_get_coin_change24h_result_none(self):
        self.assertIsNone(get_coin_change24h([]))

    def test_get_coin_change7d_result_none(self):
        self.assertIsNone(get_coin_change7d([]))

    def test_get_coin_market_cap_result_none(self):
        self.assertIsNone(get_coin_market_cap([]))

    def test_get_coin_volume24h_result_none(self):
        self.assertIsNone(get_coin_volume24h([]))

    def test_get_coin_circulating_supply_result_none(self):
        self.assertIsNone(get_coin_circulating_supply([]))
    

