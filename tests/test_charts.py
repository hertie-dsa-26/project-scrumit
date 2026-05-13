# testing chart generation functions from src/charts.py
# terminal command to run test "python -m unittest tests.test_charts -v"

import unittest
import json
import os
import sys
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from charts import (
    save_hourly_laundering_rate,
    save_daily_volume,
    save_daily_laundering_rate,
    save_laundering_by_payment_format,
    save_laundering_by_amount_bucket,
    save_laundering_rate_by_currency,
    save_currency_volume,
    save_currency_laundering_rate,
    save_top_country_corridors,
    save_domestic_vs_crossborder,
    save_top_sender_countries,
    save_top_receiver_countries,
)


class TestCharts(unittest.TestCase):

    # building minimal mock dataframes and temp output directory for all chart tests
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()

        # mock transaction dataframe matching expected input after build_transactions_df
        self.df = pd.DataFrame({
            "hour":             [9, 14, 9, 22, 14],
            "day_of_week":      ["Monday", "Tuesday", "Wednesday", "Monday", "Friday"],
            "is_laundering":    [0, 1, 0, 1, 0],
            "s_country":        ["USA", "USA", "UK", "UK", "USA"],
            "r_country":        ["UK", "USA", "USA", "UK", "UK"],
            "amount_paid":      [500.0, 15000.0, 75000.0, 200.0, 120000.0],
            "payment_format":   ["Wire", "Cash", "Cheque", "Wire", "Bitcoin"],
            "payment_currency": ["US Dollar", "Euro", "Bitcoin", "US Dollar", "Euro"],
            "country_mismatch": [1, 0, 1, 0, 1],
        })

        # mock money dataframe matching expected output of build_money_df
        self.df_money = pd.DataFrame({
            "payment_currency": ["US Dollar", "Euro", "Bitcoin"],
            "n_transactions":   [100, 80, 20],
            "total_volume":     [500000.0, 400000.0, 100000.0],
            "avg_transaction":  [5000.0, 5000.0, 5000.0],
            "laundering_rate":  [0.05, 0.08, 0.20],
            "n_countries":      [3, 2, 1],
            "n_cross_border":   [40, 30, 10],
        })

    # ---- helper ----

    def _load_json(self, filename):
        """load and parse a saved chart json file"""
        path = os.path.join(self.output_dir, filename)
        with open(path) as f:
            return json.load(f)

    # ---- temporal view tests ----

    # testing that hourly chart json file is created
    def test_save_hourly_laundering_rate_creates_file(self):
        save_hourly_laundering_rate(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "hourly_chart.json")))

    # testing that hourly chart json is valid and contains plotly data key
    def test_save_hourly_laundering_rate_valid_json(self):
        save_hourly_laundering_rate(self.df, self.output_dir)
        chart = self._load_json("hourly_chart.json")
        self.assertIn("data", chart)

    # testing that daily volume json file is created
    def test_save_daily_volume_creates_file(self):
        save_daily_volume(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "volume_chart.json")))

    # testing that daily volume json is valid and contains plotly data key
    def test_save_daily_volume_valid_json(self):
        save_daily_volume(self.df, self.output_dir)
        chart = self._load_json("volume_chart.json")
        self.assertIn("data", chart)

    # testing that daily laundering rate json file is created
    def test_save_daily_laundering_rate_creates_file(self):
        save_daily_laundering_rate(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "daily_rate_chart.json")))

    # testing that daily laundering rate json is valid and contains plotly data key
    def test_save_daily_laundering_rate_valid_json(self):
        save_daily_laundering_rate(self.df, self.output_dir)
        chart = self._load_json("daily_rate_chart.json")
        self.assertIn("data", chart)

    # ---- currency view tests ----

    # testing that payment format chart json file is created
    def test_save_laundering_by_payment_format_creates_file(self):
        save_laundering_by_payment_format(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "payment_format_chart.json")))

    # testing that payment format json is valid and contains plotly data key
    def test_save_laundering_by_payment_format_valid_json(self):
        save_laundering_by_payment_format(self.df, self.output_dir)
        chart = self._load_json("payment_format_chart.json")
        self.assertIn("data", chart)

    # testing that amount bucket chart json file is created
    def test_save_laundering_by_amount_bucket_creates_file(self):
        save_laundering_by_amount_bucket(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "amount_bucket_chart.json")))

    # testing that amount bucket json is valid and contains plotly data key
    def test_save_laundering_by_amount_bucket_valid_json(self):
        save_laundering_by_amount_bucket(self.df, self.output_dir)
        chart = self._load_json("amount_bucket_chart.json")
        self.assertIn("data", chart)

    # testing that laundering rate by currency json file is created
    def test_save_laundering_rate_by_currency_creates_file(self):
        save_laundering_rate_by_currency(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "laundering_rate_by_currency_chart.json")))

    # testing that laundering rate by currency json is valid and contains plotly data key
    def test_save_laundering_rate_by_currency_valid_json(self):
        save_laundering_rate_by_currency(self.df, self.output_dir)
        chart = self._load_json("laundering_rate_by_currency_chart.json")
        self.assertIn("data", chart)

    # testing that currency volume json file is created
    def test_save_currency_volume_creates_file(self):
        save_currency_volume(self.df_money, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "currency_volume_chart.json")))

    # testing that currency volume json is valid and contains plotly data key
    def test_save_currency_volume_valid_json(self):
        save_currency_volume(self.df_money, self.output_dir)
        chart = self._load_json("currency_volume_chart.json")
        self.assertIn("data", chart)

    # testing that currency laundering rate json file is created
    def test_save_currency_laundering_rate_creates_file(self):
        save_currency_laundering_rate(self.df_money, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "currency_laundering_rate_chart.json")))

    # testing that currency laundering rate json is valid and contains plotly data key
    def test_save_currency_laundering_rate_valid_json(self):
        save_currency_laundering_rate(self.df_money, self.output_dir)
        chart = self._load_json("currency_laundering_rate_chart.json")
        self.assertIn("data", chart)

    # ---- geographical view tests ----

    # testing that top country corridors json file is created
    def test_save_top_country_corridors_creates_file(self):
        save_top_country_corridors(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "top_corridors_chart.json")))

    # testing that top country corridors json is valid and contains plotly data key
    def test_save_top_country_corridors_valid_json(self):
        save_top_country_corridors(self.df, self.output_dir)
        chart = self._load_json("top_corridors_chart.json")
        self.assertIn("data", chart)

    # testing that domestic vs crossborder json file is created
    def test_save_domestic_vs_crossborder_creates_file(self):
        save_domestic_vs_crossborder(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "domestic_vs_crossborder_chart.json")))

    # testing that domestic vs crossborder json is valid and contains plotly data key
    def test_save_domestic_vs_crossborder_valid_json(self):
        save_domestic_vs_crossborder(self.df, self.output_dir)
        chart = self._load_json("domestic_vs_crossborder_chart.json")
        self.assertIn("data", chart)

    # testing that top sender countries json file is created
    def test_save_top_sender_countries_creates_file(self):
        save_top_sender_countries(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "top_sender_countries_chart.json")))

    # testing that top sender countries json is valid and contains plotly data key
    def test_save_top_sender_countries_valid_json(self):
        save_top_sender_countries(self.df, self.output_dir)
        chart = self._load_json("top_sender_countries_chart.json")
        self.assertIn("data", chart)

    # testing that top receiver countries json file is created
    def test_save_top_receiver_countries_creates_file(self):
        save_top_receiver_countries(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "top_receiver_countries_chart.json")))

    # testing that top receiver countries json is valid and contains plotly data key
    def test_save_top_receiver_countries_valid_json(self):
        save_top_receiver_countries(self.df, self.output_dir)
        chart = self._load_json("top_receiver_countries_chart.json")
        self.assertIn("data", chart)

    # ---- edge case tests ----

    # testing that single row dataframe does not crash any chart function
    def test_single_row_does_not_crash(self):
        single = self.df.head(1)
        try:
            save_hourly_laundering_rate(single, self.output_dir)
            save_daily_volume(single, self.output_dir)
            save_top_sender_countries(single, self.output_dir)
        except Exception as e:
            self.fail(f"single row input raised an exception: {e}")

    # testing that all laundering values of zero do not crash chart functions
    def test_all_non_laundering_does_not_crash(self):
        clean_df = self.df.copy()
        clean_df["is_laundering"] = 0
        try:
            save_daily_laundering_rate(clean_df, self.output_dir)
            save_laundering_by_payment_format(clean_df, self.output_dir)
        except Exception as e:
            self.fail(f"all-zero laundering input raised an exception: {e}")

# fail safe if discover doesn't work
# when file is discovered by unittest, it will run all test methods in this class
if __name__ == "__main__":
    unittest.main() 