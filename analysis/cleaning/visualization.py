"""
aml_viz.py
----------
Functions to build the three analysis dataframes used for visualizations.

Usage
-----
    from aml_viz import build_transactions_df, build_accounts_df, build_money_df

    df_trans    = build_transactions_df(df)
    df_accounts = build_accounts_df(df)
    df_money    = build_money_df(df)
"""

import requests
import pandas as pd


# ---------------------------------------------------------------------------
# Currency helpers
# ---------------------------------------------------------------------------

CURRENCY_MAP: dict[str, str] = {
    "US Dollar":       "USD",
    "Bitcoin":         "BTC",
    "Euro":            "EUR",
    "Australian Dollar": "AUD",
    "Yuan":            "CNY",
    "Rupee":           "INR",
    "Mexican Peso":    "MXN",
    "Yen":             "JPY",
    "UK Pound":        "GBP",
    "Ruble":           "RUB",
    "Canadian Dollar": "CAD",
    "Swiss Franc":     "CHF",
    "Brazil Real":     "BRL",
    "Saudi Riyal":     "SAR",
    "Shekel":          "ILS",
}

BTC_EUR_RATE = 20_222.71  # Fixed rate: Bitcoin → EUR as of September 2022


def _fetch_rate(date_str: str, from_currency: str, to_currency: str = "EUR") -> float:
    """Fetch a single exchange rate from the Frankfurter API for a given date."""
    code = CURRENCY_MAP.get(from_currency, from_currency)

    if code == "BTC":
        return BTC_EUR_RATE
    if code == to_currency:
        return 1.0

    url = f"https://api.frankfurter.app/{date_str}"
    response = requests.get(url, params={"from": code, "to": to_currency})
    response.raise_for_status()
    return response.json()["rates"][to_currency]


def _build_rate_cache(df: pd.DataFrame) -> dict[tuple, float]:
    """
    Collect every unique (date_str, currency) pair from both the received and
    paid columns, fetch each rate exactly once, and return a lookup dict.
    Falls back to 1.0 if a fetch fails.
    """
    date_strings = df["date"].dt.strftime("%Y-%m-%d")
    all_pairs = set(zip(date_strings, df["receiving_currency"])) | \
                set(zip(date_strings, df["payment_currency"]))

    cache: dict[tuple, float] = {}
    for date_str, currency in all_pairs:
        try:
            cache[(date_str, currency)] = _fetch_rate(date_str, currency)
        except Exception:
            cache[(date_str, currency)] = 1.0

    return cache


def _apply_eur_conversion(df: pd.DataFrame, cache: dict[tuple, float]) -> pd.DataFrame:
    """Add amount_received_eur and amount_paid_eur columns using a pre-built rate cache."""
    df = df.copy()

    date_strings = df["date"].dt.strftime("%Y-%m-%d")

    df["amount_received_eur"] = [
        round(amt * cache[(d, cur)], 2)
        for amt, d, cur in zip(df["amount_received"], date_strings, df["receiving_currency"])
    ]
    df["amount_paid_eur"] = [
        round(amt * cache[(d, cur)], 2)
        for amt, d, cur in zip(df["amount_paid"], date_strings, df["payment_currency"])
    ]

    return df


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def build_transactions_df(df: pd.DataFrame, convert_eur: bool = True) -> pd.DataFrame:
    """
    Enrich the cleaned AML dataframe with columns useful for time-based
    and currency visualizations.

    Adds
    ----
    - hour           : integer hour extracted from the time column
    - day_of_week    : weekday name (Monday … Sunday)
    - country_mismatch : bool, True when sender and receiver countries differ
    - amount_received_eur / amount_paid_eur : EUR-converted amounts
      (only when convert_eur=True; requires internet access)

    Parameters
    ----------
    df : pd.DataFrame
        Output of the cleaning pipeline (aml_cleaner.clean_aml).
    convert_eur : bool
        Whether to fetch exchange rates and add EUR columns.
        Set to False to skip the API calls.

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    
    _time_parsed = pd.to_datetime(df["time"], format="%H:%M:%S")
    df["time"] = _time_parsed.dt.time
    df["hour"] = _time_parsed.dt.hour
    df["day_of_week"] = df["date"].dt.day_name()

    df["country_mismatch"] = df["s_country"] != df["r_country"]

    if convert_eur:
        cache = _build_rate_cache(df)
        df = _apply_eur_conversion(df, cache)

    return df

def build_accounts_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate the cleaned AML dataframe to one row per sender account.

    Columns
    -------
    s_entity_id, entity_name, entity_type, bank, country,
    n_transactions, n_laundering, laundering_rate,
    total_sent, avg_sent, n_unique_recipients, n_countries_sent_to

    Parameters
    ----------
    df : pd.DataFrame
        Output of the cleaning pipeline (or build_transactions_df).

    Returns
    -------
    pd.DataFrame  — shape (n_unique_senders, 12)
    """
    return df.groupby("s_entity_id").agg(
        entity_name         =("s_entity_name",  "first"),
        entity_type         =("s_entity_type",  "first"),
        bank                =("s_bank_name",    "first"),
        country             =("s_country",      "first"),
        n_transactions      =("is_laundering",  "count"),
        n_laundering        =("is_laundering",  "sum"),
        laundering_rate     =("is_laundering",  "mean"),
        total_sent          =("amount_paid",    "sum"),
        avg_sent            =("amount_paid",    "mean"),
        n_unique_recipients =("r_entity_id",    "nunique"),
        n_countries_sent_to =("r_country",      "nunique"),
    ).reset_index()

def build_money_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate the cleaned AML dataframe to one row per payment currency.

    Requires a country_mismatch column — run build_transactions_df first,
    or add it manually: df['country_mismatch'] = df['s_country'] != df['r_country']

    Columns
    -------
    payment_currency, n_transactions, total_volume, avg_transaction,
    laundering_rate, n_countries, n_cross_border

    Parameters
    ----------
    df : pd.DataFrame
        Output of build_transactions_df (must contain country_mismatch).

    Returns
    -------
    pd.DataFrame  — shape (n_unique_currencies, 7)
    """
    if "country_mismatch" not in df.columns:
        df = df.copy()
        df["country_mismatch"] = df["s_country"] != df["r_country"]

    return df.groupby("payment_currency").agg(
        n_transactions  =("amount_paid",      "count"),
        total_volume    =("amount_paid",      "sum"),
        avg_transaction =("amount_paid",      "mean"),
        laundering_rate =("is_laundering",    "mean"),
        n_countries     =("s_country",        "nunique"),
        n_cross_border  =("country_mismatch", "sum"),
    ).reset_index()