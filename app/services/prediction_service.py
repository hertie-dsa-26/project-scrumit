"""Prediction service for transaction-level money laundering inference.

The service loads:
1) A trained model artifact.
2) The PyCaret preprocessing artifact used during training.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class MoneyLaunderingPredictor:
    """
    Makes predictions on transaction data using the trained QDA model
    and a compatible preprocessing pipeline.
    """
    
    def __init__(self):
        """Initialize by loading the model and preprocessing artifacts."""
        self.project_root = Path(__file__).parent.parent.parent
        
        # Load the model (portable, works in .venv)
        model_path = self.project_root / "analysis" / "models" / "custom_qda_model_for_flask.pkl"
        self.model = joblib.load(model_path)
        
        self.preprocessor = None
        self.preprocessor_path = self.project_root / "analysis" / "features" / "pycaret_preprocessing_pipeline.pkl"
        self.preprocessor_source = "pycaret"
        self.preprocessor_available = False

        try:
            self.preprocessor = joblib.load(self.preprocessor_path)
            self.preprocessor_available = True
        except (FileNotFoundError, ModuleNotFoundError):
            self.preprocessor_available = False
    
    def preprocess_transaction(self, raw_data: dict) -> np.ndarray:
        """
        Preprocess raw transaction data to match training format.
        
        Args:
            raw_data: Dictionary with keys matching training features
                Example: {
                    'from_bank': 'BankA',
                    'account': 'ACC123',
                    'to_bank': 'BankB',
                    'account.1': 'ACC456',
                    'amount_received': 5000.0,
                    'receiving_currency': 'USD',
                    'amount_paid': 5000.0,
                    'payment_currency': 'USD',
                    'currency_mismatch': 'No',
                    'payment_format': 'Wire',
                    's_country': 'US',
                    'r_country': 'MX',
                    's_bank_type': 'Commercial',
                    'r_bank_type': 'Commercial'
                }
        
        Returns:
            Preprocessed features array (56 dimensions)
            
        Raises:
            RuntimeError: If preprocessor not available
        """
        if not self.preprocessor_available:
            raise RuntimeError(
                "Preprocessing pipeline not available in this environment.\n"
                "Expected artifact:\n"
                "- analysis/features/pycaret_preprocessing_pipeline.pkl"
            )
        
        # Convert dict to DataFrame with correct column names
        expected_features = [
            'from_bank', 'account', 'to_bank', 'account.1',
            'amount_received', 'receiving_currency', 'amount_paid', 'payment_currency',
            'currency_mismatch', 'payment_format', 's_country', 'r_country',
            's_bank_type', 'r_bank_type'
        ]
        
        # Validate input has all required features
        missing_features = [f for f in expected_features if f not in raw_data]
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")
        
        # Create DataFrame with expected features only
        df_raw = pd.DataFrame([{f: raw_data[f] for f in expected_features}])
        
        # Apply preprocessing
        df_preprocessed = self.preprocessor.transform(df_raw)
        
        # Convert to numpy array
        if hasattr(df_preprocessed, 'values'):
            return df_preprocessed.values[0]  # Extract first row
        else:
            return df_preprocessed[0]
    
    def predict(self, raw_data: dict) -> dict:
        """
        Make prediction on raw transaction data.
        
        Args:
            raw_data: Dictionary with transaction features
        
        Returns:
            Dictionary with prediction results:
            {
                'is_laundering': 0 or 1 (prediction),
                'probability': float (probability of money laundering),
                'confidence': float (probability of predicted class)
            }
        """
        # Preprocess
        features = self.preprocess_transaction(raw_data)
        
        # Reshape to 2D array (required by model)
        features = features.reshape(1, -1)
        
        # Get prediction
        prediction = self.model.predict(features)[0]
        
        # Get probability of positive class (money laundering = 1)
        proba_matrix = self.model.predict_proba(features)
        # Find index of class 1 in model's classes
        class_one_idx = list(self.model.classes).index(1)
        probability = proba_matrix[0, class_one_idx]
        
        return {
            'is_laundering': int(prediction),
            'probability': float(probability),
            'confidence': float(max(proba_matrix[0])),
            'model_classes': list(self.model.classes),
            'preprocessor_source': self.preprocessor_source
        }


# Example usage (for testing)
if __name__ == "__main__":
    # Smoke test for local execution.
    
    predictor = MoneyLaunderingPredictor()
    
    # Example transaction
    sample_transaction = {
        'from_bank': 'Bank of America',
        'account': '12345678',
        'to_bank': 'HSBC',
        'account.1': '87654321',
        'amount_received': 50000.0,
        'receiving_currency': 'USD',
        'amount_paid': 50000.0,
        'payment_currency': 'USD',
        'currency_mismatch': 'No',
        'payment_format': 'Wire Transfer',
        's_country': 'US',
        'r_country': 'CN',
        's_bank_type': 'Commercial',
        'r_bank_type': 'Commercial'
    }
    
    if predictor.preprocessor_available:
        print(f"Using preprocessor: {predictor.preprocessor_source} ({predictor.preprocessor_path})")
        result = predictor.predict(sample_transaction)
        print("Prediction Result:")
        print(f"  Is Laundering: {result['is_laundering']}")
        print(f"  Probability: {result['probability']:.4f}")
        print(f"  Confidence: {result['confidence']:.4f}")
    else:
        print("Cannot test: preprocessing artifact is unavailable in this environment")
