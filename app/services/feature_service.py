"""Service to load and serve feature importance results to Flask."""

import joblib
from pathlib import Path


class FeatureImportanceService:
    """Load and serve cached feature importance results."""
    
    def __init__(self):
        """Initialize by loading cached feature importance."""
        self.project_root = Path(__file__).parent.parent.parent
        self.importance_path = self.project_root / "analysis" / "models" / "feature_importance_results.pkl"
        self.importance_df = None
        self.load_importance()
    
    def load_importance(self):
        """Load cached feature importance DataFrame."""
        try:
            self.importance_df = joblib.load(self.importance_path)
        except FileNotFoundError:
            raise RuntimeError(
                f"Feature importance cache not found: {self.importance_path}\n"
                "To generate it, run:\n"
                "  python analysis/models/feature_importance.py\n"
                "from the project root directory."
            )
        except Exception as e:
            raise RuntimeError(f"Error loading feature importance: {str(e)}")
    
    def get_top_features(self, n=10):
        """
        Get top N features by importance.
        
        Args:
            n: Number of top features to return (default: 10)
        
        Returns:
            Dict with 'features', 'importance_mean', 'importance_std' lists
        """
        if self.importance_df is None:
            return {'error': 'Feature importance not loaded'}
        
        top = self.importance_df.head(n)
        return {
            'features': top['feature'].tolist(),
            'importance_mean': top['importance_mean'].tolist(),
            'importance_std': top['importance_std'].tolist(),
            'n_features': len(top)
        }
    
    def get_all_features(self):
        """
        Get all features with their importance scores.
        
        Returns:
            Dict with 'features', 'importance_mean', 'importance_std' lists
        """
        if self.importance_df is None:
            return {'error': 'Feature importance not loaded'}
        
        return {
            'features': self.importance_df['feature'].tolist(),
            'importance_mean': self.importance_df['importance_mean'].tolist(),
            'importance_std': self.importance_df['importance_std'].tolist(),
            'n_features': len(self.importance_df)
        }
    
    def get_feature_by_name(self, feature_name):
        """
        Get importance score for a specific feature.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            Dict with feature name, importance, and std, or error message
        """
        if self.importance_df is None:
            return {'error': 'Feature importance not loaded'}
        
        row = self.importance_df[self.importance_df['feature'] == feature_name]
        if row.empty:
            return {'error': f'Feature "{feature_name}" not found'}
        
        return {
            'feature': feature_name,
            'importance_mean': float(row['importance_mean'].iloc[0]),
            'importance_std': float(row['importance_std'].iloc[0]),
            'rank': int(self.importance_df.index[self.importance_df['feature'] == feature_name][0]) + 1
        }


# Example usage for Flask route
if __name__ == "__main__":
    service = FeatureImportanceService()
    
    print("Top 10 features:")
    print(service.get_top_features(10))
    
    print("\nAll features:")
    all_data = service.get_all_features()
    print(f"Total features: {all_data['n_features']}")
