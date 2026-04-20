import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.custom_qda import CustomQDA


def main():
    df_abt = pd.read_csv("data/processed/aml_clean.csv")
    df_abt["date"] = pd.to_datetime(df_abt["date"]).dt.date
    df_abt["time"] = pd.to_datetime(df_abt["time"], format="%H:%M:%S").dt.time
    df_abt_cleaned = df_abt.dropna(subset=["is_laundering"])

    key_vars = [
        "date",
        "time",
        "s_bank_name",
        "s_bank_id",
        "s_entity_id",
        "s_entity_name",
        "s_entity_type",
        "s_latitude",
        "s_longitude",
        "r_bank_name",
        "r_bank_id",
        "r_entity_id",
        "r_entity_name",
        "r_entity_type",
        "r_latitude",
        "r_longitude",
    ]
    target = "is_laundering"

    subset_proportion = 0.1
    if subset_proportion < 1.0:
        df_abt_subset, _ = train_test_split(
            df_abt_cleaned,
            train_size=subset_proportion,
            random_state=42,
            stratify=df_abt_cleaned[target],
        )
    else:
        df_abt_subset = df_abt_cleaned.copy()

    train_df, _ = train_test_split(
        df_abt_subset,
        test_size=0.2,
        random_state=42,
        stratify=df_abt_subset[target],
    )

    loaded_preprocessing_pipeline = joblib.load("analysis/features/pycaret_preprocessing_pipeline.pkl")
    X_train_raw = train_df.drop(columns=key_vars + [target])
    y_train = train_df[target]
    X_train_preprocessed = loaded_preprocessing_pipeline.transform(X_train_raw)

    smote_instance = SMOTE(k_neighbors=3, random_state=42, sampling_strategy=0.2)
    X_train_smoted, y_train_smoted = smote_instance.fit_resample(X_train_preprocessed, y_train)

    custom_qda_model = CustomQDA(reg_param=0.14)
    custom_qda_model.fit(X_train_smoted, y_train_smoted)

    out_path = "analysis/models/custom_qda_model_for_flask.pkl"
    joblib.dump(custom_qda_model, out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
