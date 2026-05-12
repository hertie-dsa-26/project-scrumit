# testing flask routes across api, dashboard, map and ml blueprints
# terminal command to run test "python -m unittest tests.test_routes -v"

import unittest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from unittest.mock import patch, MagicMock



class TestRoutes(unittest.TestCase):

    # creating test client from app factory for all route tests
    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    # ---- api health and info routes ----

    # testing that health endpoint returns 200
    def test_health_returns_200(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    # testing that health endpoint returns expected json keys
    def test_health_returns_expected_keys(self):
        response = self.client.get("/api/health")
        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertIn("service", data)
        self.assertIn("preprocessor_available", data)

    # testing that required features endpoint returns 200
    def test_required_features_returns_200(self):
        response = self.client.get("/api/required-features")
        self.assertEqual(response.status_code, 200)

    # testing that required features response contains categorical and numerical keys
    def test_required_features_expected_keys(self):
        response = self.client.get("/api/required-features")
        data = json.loads(response.data)
        self.assertIn("categorical", data)
        self.assertIn("numerical", data)

    # testing that default values endpoint returns 200
    def test_default_values_returns_200(self):
        response = self.client.get("/api/default-values")
        self.assertEqual(response.status_code, 200)

    # testing that default values response contains defaults and feature info keys
    def test_default_values_expected_keys(self):
        response = self.client.get("/api/default-values")
        data = json.loads(response.data)
        self.assertIn("defaults", data)
        self.assertIn("feature_info", data)

    # testing that model info endpoint returns 200
    def test_model_info_returns_200(self):
        response = self.client.get("/api/model-info")
        self.assertEqual(response.status_code, 200)

    # testing that model info response contains expected keys
    def test_model_info_expected_keys(self):
        response = self.client.get("/api/model-info")
        data = json.loads(response.data)
        self.assertIn("model_type", data)
        self.assertIn("status", data)
        self.assertIn("input_features", data)

    # testing that feature importance endpoint returns 200
    def test_feature_importance_returns_200(self):
        response = self.client.get("/api/feature-importance")
        self.assertEqual(response.status_code, 200)

    # testing that feature importance response contains success and features keys
    def test_feature_importance_expected_keys(self):
        response = self.client.get("/api/feature-importance")
        data = json.loads(response.data)
        self.assertIn("success", data)
        self.assertIn("features", data)

    # ---- api predict route ----

    # testing that predict endpoint returns non-200 when no json is provided
    def test_predict_no_json_returns_error(self):
        response = self.client.post("/api/predict")
        self.assertNotEqual(response.status_code, 200)

    # testing that predict endpoint returns json with success key on any input
    def test_predict_returns_json(self):
        response = self.client.post(
            "/api/predict",
            json={
                "amount_paid": 1000.0,
                "amount_received": 1000.0,
                "payment_currency": "US Dollar",
                "receiving_currency": "US Dollar",
                "payment_format": "Wire",
                "s_bank_type": "Commercial",
                "r_bank_type": "Commercial",
                "s_country": "USA",
                "r_country": "USA",
                "currency_mismatch": "0",
            }
        )
        data = json.loads(response.data)
        self.assertIn("success", data)

    # testing that predict endpoint does not return 500 on valid input
    def test_predict_does_not_crash(self):
        response = self.client.post("/api/predict", json={})
        self.assertNotEqual(response.status_code, 500)

    # ---- dashboard routes ----

    # testing that index route returns 200
    def test_index_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # testing that ml dashboard route returns 200
    def test_ml_returns_200(self):
        response = self.client.get("/ml")
        self.assertEqual(response.status_code, 200)

    # testing that map route returns 200
    def test_map_returns_200(self):
        response = self.client.get("/map")
        self.assertEqual(response.status_code, 200)

    # ---- map api routes ----

    # testing that country rates endpoint returns non-500 status
    def test_country_rates_does_not_crash(self):
        response = self.client.get("/api/country-rates")
        self.assertNotEqual(response.status_code, 500)

    # testing that corridors endpoint returns non-500 status
    def test_corridors_does_not_crash(self):
        response = self.client.get("/api/corridors")
        self.assertNotEqual(response.status_code, 500)

    def test_predict_mocked_predictor(self):
        mock_predictor = MagicMock()
        mock_predictor.preprocessor_available = True
        mock_predictor.predict.return_value = {
            "is_laundering": 0,
            "probability": 0.12,
            "confidence": "low",
            "imputed_fields": []
        }
        with patch("app.routes.api.get_predictor", return_value=mock_predictor):
            response = self.client.post("/api/predict", json={"amount_paid": 1000.0})
            data = json.loads(response.data)
            self.assertTrue(data["success"])

    # fail safe if discover doesn't work
    # when file is discovered by unittest, it will run all test methods in this class
    if __name__ == "__main__":
        unittest.main()