import pandas as pd
from analysis.cleaning.cleaning import clean_aml
from analysis.cleaning.visualization import build_transactions_df, build_accounts_df, build_money_df

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