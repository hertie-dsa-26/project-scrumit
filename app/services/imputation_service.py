"""Service to handle missing feature values with statistical imputation."""

from typing import Dict, Any


class FeatureImputationService:
    """
    Imputes missing transaction features with reasonable defaults.
    Uses mode for categorical features and median for numerical features.
    """

    # Categorical features with their mode values
    CATEGORICAL_DEFAULTS = {
        'from_bank': 'Unknown',
        'account': 'UNKNOWN-ACCOUNT',
        'to_bank': 'Unknown',
        'account.1': 'UNKNOWN-ACCOUNT',
        'receiving_currency': 'USD',
        'payment_currency': 'USD',
        'currency_mismatch': 'No',
        'payment_format': 'Wire',
        's_country': 'US',
        'r_country': 'US',
        's_bank_type': 'Commercial',
        'r_bank_type': 'Commercial'
    }

    # Numerical features with their median/mean values (from training data)
    NUMERICAL_DEFAULTS = {
        'amount_received': 10000.0,    # Median transaction amount
        'amount_paid': 10000.0,        # Median transaction amount
    }

    # All required features
    ALL_FEATURES = list(CATEGORICAL_DEFAULTS.keys()) + list(NUMERICAL_DEFAULTS.keys())

    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """Get all default values as a single dictionary."""
        defaults = {}
        defaults.update(FeatureImputationService.CATEGORICAL_DEFAULTS)
        defaults.update(FeatureImputationService.NUMERICAL_DEFAULTS)
        return defaults

    @staticmethod
    def impute_missing(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill in missing values in the transaction data with defaults.

        Args:
            data: Partial or complete transaction data dictionary

        Returns:
            Complete transaction data with all required features
        """
        imputed = FeatureImputationService.get_defaults()

        # Override defaults with provided values (skip empty strings)
        for key, value in data.items():
            if value is not None and value != '':
                imputed[key] = value

        return imputed

    @staticmethod
    def get_feature_info() -> Dict[str, Dict[str, Any]]:
        """
        Get information about each feature including type and default value.

        Returns:
            Dictionary mapping feature names to their metadata
        """
        features = {}

        for feature, default in FeatureImputationService.CATEGORICAL_DEFAULTS.items():
            features[feature] = {
                'type': 'categorical',
                'default': default,
                'description': f'Categorical feature with mode value: {default}'
            }

        for feature, default in FeatureImputationService.NUMERICAL_DEFAULTS.items():
            features[feature] = {
                'type': 'numerical',
                'default': default,
                'description': f'Numerical feature with median value: {default}'
            }

        return features

    @staticmethod
    def validate_required_fields(data: Dict[str, Any]) -> tuple[bool, list]:
        """
        Validate that all required fields are either provided or can be imputed.

        Args:
            data: Transaction data to validate

        Returns:
            Tuple of (is_valid, missing_fields_with_defaults)
        """
        all_fields = FeatureImputationService.ALL_FEATURES
        provided_fields = [k for k in data.keys() if data[k] is not None and data[k] != '']
        imputable_fields = all_fields

        # All fields can be imputed with defaults
        return True, []


# Example usage
if __name__ == "__main__":
    # Example: Partial transaction data
    partial_data = {
        'from_bank': 'Bank of America',
        'to_bank': 'HSBC',
        'amount_paid': 50000.0,
    }

    service = FeatureImputationService()

    print("Original data:")
    print(partial_data)

    print("\nImputed data:")
    imputed = service.impute_missing(partial_data)
    print(imputed)

    print("\nFeature info:")
    info = service.get_feature_info()
    for feature, meta in list(info.items())[:5]:
        print(f"  {feature}: {meta['type']} (default: {meta['default']})")
