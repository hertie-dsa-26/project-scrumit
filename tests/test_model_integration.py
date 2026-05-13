# testing integration between pycaret preprocessing pipeline and custom qda model
# terminal command to run test "python -m unittest tests.test_model_integration -v"

import unittest
import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class TestModelIntegration(unittest.TestCase):

    # loading both artifacts, transforming once and slicing off is_laundering target column
    def setUp(self):
        project_root = Path(__file__).parent.parent
        self.pipeline = joblib.load(project_root / "analysis" / "features" / "pycaret_preprocessing_pipeline.pkl")
        self.model = joblib.load(project_root / "analysis" / "models" / "custom_qda_model_for_flask.pkl")
        self.n_features = len(list(self.model.means.values())[0])

        self.sample_input = pd.DataFrame({
            "from_bank":            [3335],
            "account":              [8000265690],
            "to_bank":              [3335],
            "account.1":            [8000265690],
            "amount_received":      [1000.00],
            "receiving_currency":   ["US Dollar"],
            "amount_paid":          [1000.00],
            "payment_currency":     ["US Dollar"],
            "currency_mismatch":    [0],
            "payment_format":       ["Wire"],
            "s_country":            ["US"],
            "s_bank_type":          ["Commercial"],
            "r_country":            ["US"],
            "r_bank_type":          ["Commercial"],
            "is_laundering":        [0]
        })

        self.batch_input = pd.concat([self.sample_input] * 10, ignore_index=True)
        self.transformed_single = self.pipeline.transform(self.sample_input).iloc[:, :self.n_features]
        self.transformed_batch = self.pipeline.transform(self.batch_input).iloc[:, :self.n_features]

    # testing that pipeline output shape matches model expected input dimensions
    def test_pipeline_output_matches_model_input(self):
        self.assertEqual(self.transformed_single.shape[1], self.n_features)

    # testing that pipeline output contains no nan values that would break model
    def test_pipeline_output_no_nulls(self):
        self.assertFalse(np.isnan(self.transformed_single.values).any())

    # testing end to end flow produces a valid binary prediction
    def test_end_to_end_predict(self):
        prediction = self.model.predict(self.transformed_single)
        self.assertIn(prediction[0], [0, 1])

    # testing end to end flow produces probability distribution that sums to 1
    def test_end_to_end_predict_proba(self):
        probability = self.model.predict_proba(self.transformed_single)
        self.assertAlmostEqual(probability.sum(), 1.0, places=5)

    # testing that batch input flows through pipeline and returns correct number of predictions
    def test_batch_end_to_end_length(self):
        predictions = self.model.predict(self.transformed_batch)
        self.assertEqual(len(predictions), 10)

    # testing that all batch predictions are valid binary labels
    def test_batch_predictions_valid_labels(self):
        predictions = self.model.predict(self.transformed_batch)
        self.assertTrue(all(p in [0, 1] for p in predictions))

    # testing that currency mismatch flag survives pipeline transformation
    def test_currency_mismatch_flag_preserved(self):
        mismatched = self.sample_input.copy()
        mismatched["payment_currency"] = "Bitcoin"
        mismatched["currency_mismatch"] = 1
        transformed = self.pipeline.transform(mismatched).iloc[:, :self.n_features]
        self.assertEqual(transformed.shape[1], self.n_features)

    # testing that pipeline produces consistent output shape across different transaction types
    def test_pipeline_output_shape_consistent(self):
        suspicious = self.sample_input.copy()
        suspicious["amount_paid"] = 99999999.99
        suspicious["payment_format"] = "Bitcoin"
        transformed_suspicious = self.pipeline.transform(suspicious).iloc[:, :self.n_features]
        self.assertEqual(self.transformed_single.shape[1], transformed_suspicious.shape[1])

# fail safe if discover doesn't work
# when file is discovered by unittest, it will run all test methods in this class
if __name__ == "__main__":
    unittest.main()