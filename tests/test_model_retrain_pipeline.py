# testing retrain pipeline for custom qda model
# terminal command to run test "python -m unittest tests.test_model_retrain_pipeline -v"

import unittest
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from imblearn.over_sampling import SMOTE
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.custom_qda import CustomQDA


class TestModelRetrainPipeline(unittest.TestCase):

    # building synthetic preprocessed data to simulate retrain pipeline without loading full csv
    def setUp(self):
        project_root = Path(__file__).parent.parent
        self.model_path = project_root / "analysis" / "models" / "custom_qda_model_for_flask.pkl"
        self.n_features = 56
        np.random.seed(42)

        # synthetic training data with class imbalance mirroring real aml dataset
        n_majority = 200
        n_minority = 20
        X_majority = np.random.randn(n_majority, self.n_features)
        X_minority = np.random.randn(n_minority, self.n_features) + 2
        y_majority = np.zeros(n_majority)
        y_minority = np.ones(n_minority)

        self.X_train = np.vstack([X_majority, X_minority])
        self.y_train = np.concatenate([y_majority, y_minority])

    # testing that custom qda instantiates with reg_param without error
    def test_model_instantiation(self):
        model = CustomQDA(reg_param=0.14)
        self.assertIsNotNone(model)

    # testing that custom qda fits on preprocessed data without raising
    def test_model_fits_without_error(self):
        model = CustomQDA(reg_param=0.14)
        try:
            model.fit(self.X_train, self.y_train)
        except Exception as e:
            self.fail(f"model.fit raised an exception: {e}")

    # testing that fitted model has expected attributes after training
    def test_fitted_model_has_attributes(self):
        model = CustomQDA(reg_param=0.14)
        model.fit(self.X_train, self.y_train)
        self.assertTrue(hasattr(model, "means"))
        self.assertTrue(hasattr(model, "priors"))
        self.assertTrue(hasattr(model, "classes"))

    # testing that fitted model produces valid binary predictions
    def test_fitted_model_predict(self):
        model = CustomQDA(reg_param=0.14)
        model.fit(self.X_train, self.y_train)
        predictions = model.predict(self.X_train[:5])
        self.assertTrue(all(p in [0, 1] for p in predictions))

    # testing that fitted model probability output sums to 1
    def test_fitted_model_predict_proba(self):
        model = CustomQDA(reg_param=0.14)
        model.fit(self.X_train, self.y_train)
        probability = model.predict_proba(self.X_train[:1])
        self.assertAlmostEqual(probability.sum(), 1.0, places=5)

    # testing that smote increases minority class samples before fitting
    def test_smote_increases_minority_class(self):
        smote = SMOTE(k_neighbors=3, random_state=42, sampling_strategy=0.2)
        X_resampled, y_resampled = smote.fit_resample(self.X_train, self.y_train)
        self.assertGreater(len(y_resampled), len(self.y_train))

    # testing that model serializes and deserializes without losing predict ability
    def test_model_save_and_reload(self):
        import tempfile, os
        model = CustomQDA(reg_param=0.14)
        model.fit(self.X_train, self.y_train)
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            tmp_path = f.name
        try:
            joblib.dump(model, tmp_path)
            reloaded = joblib.load(tmp_path)
            predictions = reloaded.predict(self.X_train[:5])
            self.assertTrue(all(p in [0, 1] for p in predictions))
        finally:
            os.remove(tmp_path)

    # testing that fitting on empty data raises cleanly rather than silently failing
    def test_fit_empty_data_raises(self):
        model = CustomQDA(reg_param=0.14)
        with self.assertRaises(Exception):
            model.fit(np.array([]).reshape(0, self.n_features), np.array([]))

    # fail safe if discover doesn't work
    # when file is discovered by unittest, it will run all test methods in this class
    if __name__ == "__main__":
        unittest.main()