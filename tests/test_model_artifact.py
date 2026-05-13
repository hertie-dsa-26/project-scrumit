# testing custom_qda_model_for_flask.pkl
# terminal command to run test "python -m unittest tests.test_model_artifact -v"

import unittest
import joblib
import numpy as np
from pathlib import Path

class TestModelArtifact(unittest.TestCase): 

    # navigating to the model artifact and loading for testing
    def setUp(self):
        project_root = Path(__file__).parent.parent
        self.model = joblib.load(project_root / "analysis" / "models" / "custom_qda_model_for_flask.pkl")
        self.n_features = len(list(self.model.means.values())[0])

    # testing that model has predict method for data classification
    def test_model_has_predict(self):
        self.assertTrue(hasattr(self.model, "predict"))

    # testing model has predict_proba method for probability
    def test_model_has_predict_proba(self):
        self.assertTrue(hasattr(self.model, "predict_proba"))

    # testing that model output label is either 0 or 1
    def test_model_predict_output(self): 
        dummy_input = np.zeros((1, self.n_features))
        prediction = self.model.predict(dummy_input)
        self.assertIn(prediction[0], [0, 1])

    # testing that model output is expected probability distribution (sums to 1)
    def test_model_predict_probability_sums_to_one(self): 
        dummy_input = np.zeros((1, self.n_features))
        probability = self.model.predict_proba(dummy_input)
        self.assertAlmostEqual(probability.sum(), 1.0, places=5)

    # testing that model handles batch input and returns correct number of predictions
    def test_batch_prediction_length(self):
        batch_input = np.zeros((10, self.n_features))
        predictions = self.model.predict(batch_input)
        self.assertEqual(len(predictions), 10)

    # testing that all predictions in a batch are valid binary labels
    def test_batch_predictions_are_valid_labels(self):
        batch_input = np.random.rand(20, self.n_features)
        predictions = self.model.predict(batch_input)
        self.assertTrue(all(p in [0, 1] for p in predictions))

    # testing that mismatched feature count raises an error rather than silently failing
    def test_wrong_feature_count_raises(self):
        bad_input = np.zeros((1, self.n_features + 5))
        with self.assertRaises(Exception):
            self.model.predict(bad_input)

    # testing that class priors sum to 1 as expected for a probability distribution
    def test_class_priors_sum_to_one(self):
        self.assertAlmostEqual(sum(self.model.priors), 1.0, places=5)

    # testing that model was trained on exactly two classes (fraudulent and non-fraudulent)
    def test_two_classes_only(self):
        self.assertEqual(len(self.model.classes), 2)

    # testing that means are stored for each class and match expected feature dimensions
    def test_class_means_shape(self):
        for class_mean in self.model.means.values():
            self.assertEqual(len(class_mean), self.n_features)

# fail safe if discover doesn't work 
# when file is discovered by unittest, it will run all test methods in this class
if __name__ == "__main__": 
    unittest.main()