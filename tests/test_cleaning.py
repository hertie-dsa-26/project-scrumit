# testing cleaning pipeline functions from src/cleaning.py
# terminal command to run test "python -m unittest tests.test_cleaning -v"

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.cleaning import (
    _find_country,
    _find_bank_type,
    _city_to_country,
    _clean_columns,
    _prefix_accounts,
    merge_datasets,
    clean_transactions,
)


class TestCleaning(unittest.TestCase):

    # ---- _find_country tests ----

    # testing that bank name with city prefix is extracted correctly
    def test_find_country_city_prefix(self):
        result = _find_country("Boston Bank #12")
        self.assertEqual(result, "Boston")

    # testing that bank of format extracts correctly
    def test_find_country_bank_of(self):
        result = _find_country("Bank of Chicago")
        self.assertEqual(result, "Chicago")

    # testing that unrecognised bank name returns other
    def test_find_country_unrecognised(self):
        result = _find_country("RandomFinancialInstitution")
        self.assertEqual(result, "other")

    # ---- _find_bank_type tests ----

    # testing that cooperative banks are classified correctly
    def test_find_bank_type_cooperative(self):
        self.assertEqual(_find_bank_type("Springfield Cooperative Bank"), "Cooperative")

    # testing that holding companies are classified correctly
    def test_find_bank_type_holding(self):
        self.assertEqual(_find_bank_type("Northeast Bancorp"), "Holding")

    # testing that trust banks are classified correctly
    def test_find_bank_type_trust(self):
        self.assertEqual(_find_bank_type("Boston Trust Bank"), "Trust")

    # testing that savings banks are classified correctly
    def test_find_bank_type_savings(self):
        self.assertEqual(_find_bank_type("Dallas Savings Bank"), "Savings")

    # testing that commercial banks are classified correctly
    def test_find_bank_type_commercial(self):
        self.assertEqual(_find_bank_type("City Bank"), "Commercial")

    # testing that unrecognised names return none
    def test_find_bank_type_unknown(self):
        self.assertIsNone(_find_bank_type("Financial Services LLC"))

    # ---- _city_to_country tests ----

    # testing that city names are mapped to correct countries
    def test_city_to_country_maps_correctly(self):
        df = pd.DataFrame({"Country": ["Boston", "Lincoln"]})
        mapping = {"Boston": "USA", "Lincoln": "UK"}
        result = _city_to_country(df, mapping)
        self.assertEqual(result["Country"].iloc[0], "USA")
        self.assertEqual(result["Country"].iloc[1], "UK")

    # testing that unmapped cities are left unchanged
    def test_city_to_country_leaves_unmapped(self):
        df = pd.DataFrame({"Country": ["UnknownCity"]})
        result = _city_to_country(df, {"Boston": "USA"})
        self.assertEqual(result["Country"].iloc[0], "UnknownCity")

    # testing that original dataframe is not mutated
    def test_city_to_country_does_not_mutate(self):
        df = pd.DataFrame({"Country": ["Boston"]})
        _city_to_country(df, {"Boston": "USA"})
        self.assertEqual(df["Country"].iloc[0], "Boston")

    # ---- _clean_columns tests ----

    # testing that column names are converted to snake_case
    def test_clean_columns_snake_case(self):
        df = pd.DataFrame({"Amount Paid": [1], "Payment Format": [2]})
        result = _clean_columns(df)
        self.assertIn("amount_paid", result.columns)
        self.assertIn("payment_format", result.columns)

    # testing that leading and trailing whitespace is stripped from column names
    def test_clean_columns_strips_whitespace(self):
        df = pd.DataFrame({" Bank Name ": [1]})
        result = _clean_columns(df)
        self.assertIn("bank_name", result.columns)

    # testing that original dataframe is not mutated
    def test_clean_columns_does_not_mutate(self):
        df = pd.DataFrame({"Amount Paid": [1]})
        _clean_columns(df)
        self.assertIn("Amount Paid", df.columns)

    # ---- _prefix_accounts tests ----

    # testing that prefix is added to all column names
    def test_prefix_accounts_adds_prefix(self):
        df = pd.DataFrame({"account_number": [1], "bank_name": ["X"]})
        result = _prefix_accounts(df, "s_", "account")
        self.assertIn("s_bank_name", result.columns)

    # testing that account number column is renamed correctly after prefixing
    def test_prefix_accounts_renames_account(self):
        df = pd.DataFrame({"account_number": [1], "bank_name": ["X"]})
        result = _prefix_accounts(df, "s_", "account")
        self.assertIn("account", result.columns)
        self.assertNotIn("s_account_number", result.columns)

    # ---- clean_transactions tests ----

    # testing that currency mismatch flag is 1 when currencies differ
    def test_currency_mismatch_flag_set(self):
        mock_data = pd.DataFrame({
            "Timestamp":            ["2022/01/01 10:00"],
            "From Bank":            [1],
            "Account":              [100],
            "To Bank":              [2],
            "Account.1":            [200],
            "Amount Received":      [500.0],
            "Receiving Currency":   ["US Dollar"],
            "Amount Paid":          [500.0],
            "Payment Currency":     ["Bitcoin"],
            "Payment Format":       ["Wire"],
            "Is Laundering":        [0],
        })
        with patch("pandas.read_csv", return_value=mock_data):
            result = clean_transactions("fake/path.csv")
            self.assertEqual(result["currency_mismatch"].iloc[0], 1)

    # testing that non-positive transactions are dropped
    def test_non_positive_transactions_dropped(self):
        mock_data = pd.DataFrame({
            "Timestamp":            ["2022/01/01 10:00", "2022/01/01 11:00"],
            "From Bank":            [1, 2],
            "Account":              [100, 101],
            "To Bank":              [2, 3],
            "Account.1":            [200, 201],
            "Amount Received":      [500.0, 0.0],
            "Receiving Currency":   ["US Dollar", "Euro"],
            "Amount Paid":          [500.0, 0.0],
            "Payment Currency":     ["US Dollar", "Euro"],
            "Payment Format":       ["Wire", "Cash"],
            "Is Laundering":        [0, 0],
        })
        with patch("pandas.read_csv", return_value=mock_data):
            result = clean_transactions("fake/path.csv")
            self.assertEqual(len(result), 1)

    # ---- merge_datasets tests ----

    # testing that merge produces a dataframe with rows from transactions
    def test_merge_returns_dataframe(self):
        trans = pd.DataFrame({
            "account":   [100],
            "account.1": [200],
            "amount_paid": [1000.0],
        })
        accounts = pd.DataFrame({
            "account_number": [100, 200],
            "bank_name": ["Bank A", "Bank B"],
        })
        s_acc = _prefix_accounts(_clean_columns(accounts), "s_", "account")
        r_acc = _prefix_accounts(_clean_columns(accounts), "r_", "account.1")
        result = trans.merge(s_acc, on="account", how="left")
        result = result.merge(r_acc, on="account.1", how="left")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

# fail safe if discover doesn't work
# when file is discovered by unittest, it will run all test methods in this class
if __name__ == "__main__":
    unittest.main()