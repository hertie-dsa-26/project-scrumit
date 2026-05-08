# tests for feature_importance.py and feature_importance.pkl
# terminal command to run test "python -m unittest tests.test_model_feature_importance -v"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "analysis"/ "models"))

from feature_importance import compute_feature_importance, _resolve_feature_names
from app.services.custom_qda import CustomQDA
import unittest
import joblib
import numpy as np
import pandas as pd



class TestFeatureImportance(unittest.TestCase): 

    # navigating to the model artifact and loading for testing
    def setUp(self):
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(Path(__file__).parent.parent))
        self.compute_feature_importance = compute_feature_importance
        self._resolve_feature_names = _resolve_feature_names
        self.importance_df = joblib.load(project_root / "analysis" / "models" / "feature_importance_results.pkl")
        self.model = joblib.load(project_root / "analysis" / "models" / "custom_qda_model_for_flask.pkl")
        self.n_features = self.model.means[0].shape[0]
    
    # ---- test for feature importance dataaframe ----

    # confirm that the pkl loads as a dataframe
    def test_dataframe(self): 
        self.assertIsInstance(self.importance_df, pd.DataFrame)

    # confirm expected columns exist in the dataframe
    def test_expected_columns(self): 
        expected_columns = {"feature", "importance_mean", "importance_std"}
        self.assertTrue(expected_columns.issubset(self.importance_df.columns))

    # confirm that importance_mean is sorted in descending order (ie most important features higher up)
    def test_descending_sort(self): 
        means = self.importance_df["importance_mean"].values
        self.assertTrue(np.array_equal(means, sorted(means, reverse=True)))

    # ensure dataframe is not empty
    def test_not_empty(self):
        self.assertGreater(len(self.importance_df), 0)

    # ---- tests for resolve_feature_names ---- 

    # confirm function returns list of feature names
    def test_resolve_returns_list(self): 
        feature_names = self._resolve_feature_names(np.zeros((5, self.n_features)), preprocessing_pipeline = None)
        self.assertIsInstance(feature_names, list)
    
    def test_resolve_length(self): 
        X_dummy = np.zeros((5, self.n_features))
        feature_names = self._resolve_feature_names(X_dummy, preprocessing_pipeline=None)
        self.assertEqual(len(feature_names), self.n_features)

    # ---- compute_feature_importance tests ----

    # confirm that compute_feature_importance returns a dataframe
    def test_compute_return_dataframe(self):
        X_dummy = np.zeros((10, self.n_features))
        y_dummy = np.zeros(10)
        results = self.compute_feature_importance(X_dummy, y_dummy, self.model,
                                              preprocessing_pipeline=None,
                                              n_repeats=1, n_jobs=1)
        self.assertIsInstance(results, pd.DataFrame)

    # confirm that compute_feature_importance returns expected columns
    def test_compute_expected_columns(self): 
        X_dummy = np.zeros((10, self.n_features))
        y_dummy = np.zeros(10)
        results = self.compute_feature_importance(X_dummy, y_dummy, self.model,
                                              preprocessing_pipeline=None,
                                              n_repeats=1, n_jobs=1)
        self.assertIn("feature", results.columns)
        self.assertIn("importance_mean", results.columns)
        self.assertIn("importance_std", results.columns)

# fail safe if discover doesn't work 
# when file is discovered by unittest, it will run all test methods in this class
if __name__ == "__main__":
    unittest.main()