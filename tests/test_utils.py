# testing map utility functions from src/utils.py
# terminal command to run test "python -m unittest tests.test_utils -v"

import unittest
import json
import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import compute_country_rates, compute_corridors, precompute_map, NAME_TO_ISO


class TestUtils(unittest.TestCase):

    # building minimal mock dataframe and temp output directory for all utils tests
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()

        self.df = pd.DataFrame({
            "s_country":    ["USA", "USA", "UK",  "UK",  "USA"],
            "r_country":    ["UK",  "USA", "USA", "UK",  "UK"],
            "s_latitude":   [38.89, 38.89, 51.50, 51.50, 38.89],
            "s_longitude":  [-77.03, -77.03, -0.12, -0.12, -77.03],
            "r_latitude":   [51.50, 38.89, 38.89, 51.50, 51.50],
            "r_longitude":  [-0.12, -77.03, -77.03, -0.12, -0.12],
            "is_laundering": [1, 0, 0, 1, 1],
        })

    # ---- NAME_TO_ISO tests ----

    # testing that name to iso mapping contains expected countries
    def test_name_to_iso_contains_usa(self):
        self.assertIn("USA", NAME_TO_ISO)
        self.assertEqual(NAME_TO_ISO["USA"], 840)

    # testing that name to iso mapping contains uk with correct code
    def test_name_to_iso_contains_uk(self):
        self.assertIn("UK", NAME_TO_ISO)
        self.assertEqual(NAME_TO_ISO["UK"], 826)

    # testing that all iso codes are integers
    def test_name_to_iso_values_are_integers(self):
        self.assertTrue(all(isinstance(v, int) for v in NAME_TO_ISO.values()))

    # ---- compute_country_rates tests ----

    # testing that country rates json file is created
    def test_compute_country_rates_creates_file(self):
        compute_country_rates(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "country_rates.json")))

    # testing that country rates json is valid and parseable
    def test_compute_country_rates_valid_json(self):
        compute_country_rates(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "country_rates.json")) as f:
            result = json.load(f)
        self.assertIsInstance(result, dict)

    # testing that country rates uses iso codes as keys not country names
    def test_compute_country_rates_uses_iso_keys(self):
        compute_country_rates(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "country_rates.json")) as f:
            result = json.load(f)
        for key in result.keys():
            self.assertIsInstance(int(key), int)

    # testing that all rates are between 0 and 100
    def test_compute_country_rates_valid_range(self):
        compute_country_rates(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "country_rates.json")) as f:
            result = json.load(f)
        for rate in result.values():
            self.assertGreaterEqual(rate, 0)
            self.assertLessEqual(rate, 100)

    # ---- compute_corridors tests ----

    # testing that corridors json file is created
    def test_compute_corridors_creates_file(self):
        compute_corridors(self.df, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "corridors.json")))

    # testing that corridors json is valid and returns a list
    def test_compute_corridors_valid_json(self):
        compute_corridors(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "corridors.json")) as f:
            result = json.load(f)
        self.assertIsInstance(result, list)

    # testing that corridors exclude same country transactions
    def test_compute_corridors_excludes_domestic(self):
        compute_corridors(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "corridors.json")) as f:
            result = json.load(f)
        for corridor in result:
            self.assertNotEqual(corridor["s_country"], corridor["r_country"])

    # testing that each corridor contains expected keys
    def test_compute_corridors_expected_keys(self):
        compute_corridors(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "corridors.json")) as f:
            result = json.load(f)
        expected_keys = {"from", "to", "rate", "count", "s_country", "r_country", "s_iso", "r_iso"}
        for corridor in result:
            self.assertTrue(expected_keys.issubset(corridor.keys()))

    # testing that corridor rates are between 0 and 100
    def test_compute_corridors_valid_rate_range(self):
        compute_corridors(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "corridors.json")) as f:
            result = json.load(f)
        for corridor in result:
            self.assertGreaterEqual(corridor["rate"], 0)
            self.assertLessEqual(corridor["rate"], 100)

    # testing that corridor count is a positive integer
    def test_compute_corridors_count_is_positive(self):
        compute_corridors(self.df, self.output_dir)
        with open(os.path.join(self.output_dir, "corridors.json")) as f:
            result = json.load(f)
        for corridor in result:
            self.assertGreater(corridor["count"], 0)

    # ---- precompute_map tests ----

    # testing that precompute map creates output directory if it does not exist
    def test_precompute_map_creates_output_dir(self):
        new_dir = os.path.join(self.output_dir, "new_map_dir")
        precompute_map(self.df, output_dir=new_dir)
        self.assertTrue(os.path.exists(new_dir))

    # testing that precompute map creates both expected json files
    def test_precompute_map_creates_both_files(self):
        precompute_map(self.df, output_dir=self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "country_rates.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "corridors.json")))

# fail safe if discover doesn't work
# when file is discovered by unittest, it will run all test methods in this class
if __name__ == "__main__":
    unittest.main()
