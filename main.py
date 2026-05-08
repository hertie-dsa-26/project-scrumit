import pandas as pd
from src.cleaning import clean_aml
from src.cleaning_visualization import build_transactions_df, build_accounts_df, build_money_df
from src.charts import precompute_all
from src.utils import precompute_map


if __name__ == '__main__':
    print("Running cleaning pipeline...")
    clean_aml(
       trans_path="data/raw/HI-Small_Trans.csv",
       accounts_path="data/raw/HI-Small_accounts.csv",
       output_path="data/processed/aml_clean.csv",
       geocode=False,
       overwrite=False,
    )

    print("Building visualization dataframes...")
    df = pd.read_csv("data/processed/aml_clean.csv")
    df_trans    = build_transactions_df(df, convert_eur=False)
    df_accounts = build_accounts_df(df_trans)
    df_money    = build_money_df(df_trans)

    df_trans.to_csv("data/processed/aml_trans.csv", index=False)
    df_accounts.to_csv("data/processed/aml_accounts.csv", index=False)
    df_money.to_csv("data/processed/aml_money.csv", index=False)
    print("Done!")

    df          = pd.read_csv("data/processed/aml_trans.csv")
    df_money    = pd.read_csv("data/processed/aml_money.csv")
    df_accounts = pd.read_csv("data/processed/aml_accounts.csv")
    df_clean    = pd.read_csv("data/processed/aml_clean.csv")
    precompute_all(df, df_money, df_accounts, df_clean)
    precompute_map(df_clean)