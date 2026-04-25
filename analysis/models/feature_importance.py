"""Compute and cache permutation feature importance for the QDA model."""

import joblib
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import recall_score
from pathlib import Path


def _resolve_feature_names(X_transformed, preprocessing_pipeline, X_raw=None):
    """Return meaningful transformed feature names whenever possible."""
    if hasattr(X_transformed, "columns"):
        return list(X_transformed.columns)

    if X_raw is not None:
        try:
            transformed_preview = preprocessing_pipeline.transform(X_raw.iloc[:1])
            if hasattr(transformed_preview, "columns"):
                return list(transformed_preview.columns)
        except Exception:
            pass

    try:
        pipeline_without_last = preprocessing_pipeline[:-1]
        if hasattr(pipeline_without_last, "get_feature_names_out"):
            return list(pipeline_without_last.get_feature_names_out())
    except Exception:
        pass

    return [f"transformed_feature_{i}" for i in range(X_transformed.shape[1])]


def compute_feature_importance(X_test, y_test, model, preprocessing_pipeline,
                              n_repeats=3, n_jobs=2, random_state=42, X_test_raw=None):
    """
    Compute permutation importance based on recall metric and save results.
    
    Args:
        X_test: Preprocessed test features (numpy array)
        y_test: Test labels
        model: Trained QDA model
        preprocessing_pipeline: The preprocessing pipeline used for feature names
        n_repeats: Number of times to permute a feature (default: 3 to save resources)
        n_jobs: Number of parallel jobs (default: 2 to avoid system resource errors)
        random_state: For reproducibility
        X_test_raw: Raw (untransformed) test features used only for name resolution
    
    Returns:
        DataFrame with features sorted by importance (descending)
    """
    
    # Resolve transformed feature names with robust fallbacks.
    feature_names = _resolve_feature_names(X_test, preprocessing_pipeline, X_raw=X_test_raw)
    
    print(f"Computing permutation importance for {len(feature_names)} features...")
    print(f"Using n_repeats={n_repeats}, n_jobs={n_jobs}")
    
    # Custom scorer using recall
    def custom_recall_scorer(estimator, X, y_true):
        y_pred = estimator.predict(X)
        return recall_score(y_true, y_pred)
    
    # Compute permutation importance
    result = permutation_importance(
        estimator=model,
        X=X_test,
        y=y_test,
        scoring=custom_recall_scorer,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=n_jobs
    )
    
    # Sort by importance (descending)
    sorted_idx = result.importances_mean.argsort()[::-1]
    
    importance_df = pd.DataFrame({
        'feature': [feature_names[i] for i in sorted_idx],
        'importance_mean': result.importances_mean[sorted_idx],
        'importance_std': result.importances_std[sorted_idx]
    })
    
    return importance_df


def save_feature_importance(importance_df, output_path="analysis/models/feature_importance_results.pkl"):
    """Save feature importance results to cache file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(importance_df, output_path)
    print(f"✓ Saved feature importance to {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    
    # Setup paths
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Load artifacts
    print("Loading model and preprocessor...")
    model = joblib.load(project_root / "analysis" / "models" / "custom_qda_model_for_flask.pkl")
    preprocessor = joblib.load(project_root / "analysis" / "features" / "pycaret_preprocessing_pipeline.pkl")
    
    # Load and prepare test data (replicating notebook workflow)
    print("Loading and preparing test data...")
    from sklearn.model_selection import train_test_split
    from imblearn.over_sampling import SMOTE
    
    df_abt = pd.read_csv(project_root / "data" / "processed" / "aml_clean.csv")
    df_abt['date'] = pd.to_datetime(df_abt['date']).dt.date
    df_abt['time'] = pd.to_datetime(df_abt['time'], format='%H:%M:%S').dt.time
    df_abt_cleaned = df_abt.dropna(subset=['is_laundering'])
    
    key_vars = [
        'date', 'time', 's_bank_name', 's_bank_id', 's_entity_id',
        's_entity_name', 's_entity_type', 's_latitude', 's_longitude',
        'r_bank_name', 'r_bank_id', 'r_entity_id', 'r_entity_name',
        'r_entity_type', 'r_latitude', 'r_longitude'
    ]
    target = 'is_laundering'
    
    subset_proportion = 0.1
    if subset_proportion < 1.0:
        df_abt_subset, _ = train_test_split(
            df_abt_cleaned,
            train_size=subset_proportion,
            random_state=42,
            stratify=df_abt_cleaned[target]
        )
    else:
        df_abt_subset = df_abt_cleaned.copy()
    
    train_df, test_df = train_test_split(
        df_abt_subset,
        test_size=0.2,
        random_state=42,
        stratify=df_abt_subset[target]
    )
    
    X_test_raw = test_df.drop(columns=key_vars + [target])
    y_test = test_df[target]
    X_test_preprocessed = preprocessor.transform(X_test_raw)
    
    # Compute and save
    print("\nComputing feature importance (this may take a moment)...")
    importance_df = compute_feature_importance(
        X_test_preprocessed, y_test, model, preprocessor,
        n_repeats=3,
        n_jobs=2,
        random_state=42,
        X_test_raw=X_test_raw,
    )
    
    save_feature_importance(importance_df)
    
    print("\nTop 10 Most Important Features (by Recall):")
    print(importance_df.head(10).to_string(index=False))
