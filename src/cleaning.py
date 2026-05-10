"""
aml_cleaner.py
--------------
End-to-end cleaning pipeline for the HI-Small AML dataset.

Usage
-----
    from aml_cleaner import clean_aml

    df = clean_aml(
        trans_path="data/raw/HI-Small_Trans.csv",
        accounts_path="data/raw/HI-Small_accounts.csv",
        output_path="data/processed/aml_clean.csv",   # optional
        geocode=True,                                 # set False to skip API calls
    )

Functions exposed
-----------------
    clean_aml()         – main pipeline (calls all steps below)
    clean_transactions()
    clean_accounts()
    merge_datasets()
"""

import os
import re
import time
import logging

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# City → Country lookup (manually verified for the HI-Small synthetic dataset)
# ---------------------------------------------------------------------------
CITY_COUNTRY: dict[str, str] = {
    "Albany": "USA", "Arkadelphia": "USA", "Augusta": "USA", "Billings": "USA",
    "Boston": "USA", "Bridgeport": "USA", "Butte": "USA", "Chicago": "USA",
    "Cleveland": "USA", "Columbus": "USA", "Dallas": "USA", "Danbury": "USA",
    "Denver": "USA", "Detroit": "USA", "Fairfield": "USA", "Fort Wayne": "USA",
    "Harrisburg": "USA", "Hartford": "USA", "Helena": "USA", "Houston": "USA",
    "Huron": "USA", "Indianapolis": "USA", "Lacrosse": "USA", "Los Angeles": "USA",
    "Laramie": "USA", "Madison": "USA", "Miami": "USA", "Milford": "USA",
    "New Orleans": "USA", "New York": "USA", "Newport": "USA", "Omaha": "USA",
    "Philadelphia": "USA", "Phoenix": "USA", "Pittsburgh": "USA", "Plattsburg": "USA",
    "Portland": "USA", "Providence": "USA", "Sacramento": "USA", "Seattle": "USA",
    "Springfield": "USA", "Tampa": "USA", "the East": "USA", "the North": "USA",
    "the South": "USA", "the Valley": "USA", "the West": "USA", "Topeka": "USA",
    "Tuscon": "USA", "Watertown": "USA",
    "Lincoln": "UK", "Newbury": "UK", "Portsmouth": "UK",
    "Montpelier": "Canada",
}


# ---------------------------------------------------------------------------
# Accounts helpers
# ---------------------------------------------------------------------------

def _find_country(bank_name: str) -> str:
    """Extract a country / city token from the synthetic bank name string."""
    if re.search(r"Bank #\d+$", bank_name):
        match = re.search(r"^([A-Za-z ]+?) Bank", bank_name)
        if match:
            return match.group(1)
    if re.search(r"Bank of", bank_name):
        match = re.search(r"Bank of ([A-Za-z ]+?)$", bank_name)
        if match:
            return match.group(1)
    return "other"


def _city_to_country(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Replace city names with their country using *mapping*."""
    df = df.copy()
    df["Country"] = df["Country"].map(lambda x: mapping.get(x, x))
    return df


def _find_bank_type(name: str) -> str | None:
    """Classify a bank name into a coarse type category."""
    n = name.lower()
    if "credit union" in n or "cooperative" in n:
        return "Cooperative"
    if "bancorp" in n:
        return "Holding"
    if "trust" in n:
        return "Trust"
    if "savings" in n or "thrift" in n:
        return "Savings"
    if "bank" in n:
        return "Commercial"
    return None


def _geocode_countries(countries: pd.Series) -> pd.DataFrame:
    """
    Use geopy / Nominatim to get (latitude, longitude) for each unique country.
    Respects the 1-req/s rate-limit with a 1-second sleep between calls.

    Returns a DataFrame with columns ['Country', 'Latitude', 'Longitude'].
    """
    try:
        from geopy.geocoders import Nominatim
    except ImportError:
        log.warning("geopy not installed – skipping geocoding. Install with: pip install geopy")
        return pd.DataFrame({"Country": countries, "Latitude": np.nan, "Longitude": np.nan})

    geolocator = Nominatim(user_agent="aml-cleaner-script")

    rows = []
    for country in countries:
        lat, lon = None, None
        try:
            time.sleep(1)
            loc = geolocator.geocode(country)
            if loc:
                lat, lon = loc.latitude, loc.longitude
        except Exception as exc:
            log.debug("Geocoding failed for %s: %s", country, exc)
        rows.append({"Country": country, "Latitude": lat, "Longitude": lon})

    return pd.DataFrame(rows)


def clean_accounts(accounts_path: str, geocode: bool = True) -> pd.DataFrame:
    """
    Load and clean the accounts CSV.

    Steps
    -----
    1. Extract entity type from Entity Name.
    2. Build a bank-level lookup with Country, Latitude, Longitude, Bank Type.
    3. Merge the lookup back onto the accounts DataFrame.

    Parameters
    ----------
    accounts_path : str
        Path to HI-Small_accounts.csv (or equivalent).
    geocode : bool
        Whether to call the Nominatim geocoding API (requires internet).
        If False, Latitude / Longitude columns are filled with NaN.

    Returns
    -------
    pd.DataFrame
        Cleaned accounts with added columns: Entity Type, Country,
        Latitude, Longitude, Bank Type.
    """
    log.info("Loading accounts from %s", accounts_path)
    accounts = pd.read_csv(accounts_path)

    # Extract entity type from the "Entity Name" column (e.g. "Corporation #42")
    accounts["Entity Type"] = accounts["Entity Name"].str.extract(r"^([A-Za-z ]+?) #")

    # ------------------------------------------------------------------
    # Build bank-level lookup table
    # ------------------------------------------------------------------
    bank_map = accounts[["Bank Name"]].drop_duplicates().reset_index(drop=True)

    # Country / location
    bank_map["Country"] = bank_map["Bank Name"].apply(_find_country)
    bank_map = _city_to_country(bank_map, CITY_COUNTRY)
    bank_map["Country"] = bank_map["Country"].replace("Crytpo", "Crypto")  # typo fix

    # Geocoordinates
    if geocode:
        geocodable = bank_map.loc[
            ~bank_map["Country"].isin(["Crypto", "other", "Other"]), "Country"
        ].drop_duplicates()
        coords = _geocode_countries(geocodable)
        bank_map = bank_map.merge(coords, on="Country", how="left")
    else:
        bank_map["Latitude"] = np.nan
        bank_map["Longitude"] = np.nan

    # Bank type
    bank_map["Bank Type"] = bank_map["Bank Name"].apply(_find_bank_type)

    # Merge enriched bank info back onto accounts
    accounts = accounts.merge(bank_map, on="Bank Name", how="left")

    log.info("Accounts cleaned: %d rows, %d columns", *accounts.shape)
    return accounts


# ---------------------------------------------------------------------------
# Transaction helpers
# ---------------------------------------------------------------------------

def clean_transactions(trans_path: str) -> pd.DataFrame:
    """
    Load and clean the transactions CSV.

    Steps
    -----
    1. Parse Timestamp → separate Date and Time columns.
    2. Drop transactions with Amount Paid ≤ 0.
    3. Add binary currency_mismatch flag.
    4. Keep only the relevant columns.

    Parameters
    ----------
    trans_path : str
        Path to HI-Small_Trans.csv (or equivalent).

    Returns
    -------
    pd.DataFrame
        Cleaned transactions DataFrame.
    """
    log.info("Loading transactions from %s", trans_path)
    trans = pd.read_csv(trans_path)

    # Parse timestamp
    trans["Timestamp"] = pd.to_datetime(trans["Timestamp"], format="%Y/%m/%d %H:%M")
    trans["Date"] = trans["Timestamp"].dt.normalize()
    trans["Time"] = trans["Timestamp"].dt.strftime("%H:%M:%S")

    # Remove non-positive amounts
    before = len(trans)
    trans = trans[trans["Amount Paid"] > 0].copy()
    log.info("Dropped %d non-positive transactions", before - len(trans))

    # Currency mismatch flag
    trans["currency_mismatch"] = (
        trans["Payment Currency"] != trans["Receiving Currency"]
    ).astype(int)

    # Keep only relevant columns
    keep = [
        "Date", "Time", "From Bank", "Account",
        "To Bank", "Account.1",
        "Amount Received", "Receiving Currency",
        "Amount Paid", "Payment Currency",
        "currency_mismatch", "Payment Format", "Is Laundering",
    ]
    trans = trans[keep]

    log.info("Transactions cleaned: %d rows, %d columns", *trans.shape)
    return trans


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names to snake_case."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def _prefix_accounts(df: pd.DataFrame, prefix: str, rename_to: str) -> pd.DataFrame:
    """Add *prefix* to all column names and rename the account-number column."""
    df = df.copy()
    df.columns = prefix + df.columns
    df = df.rename(columns={f"{prefix}account_number": rename_to})
    return df

# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_datasets(trans: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    """
    Merge cleaned transactions with cleaned accounts for both sender and receiver.

    Parameters
    ----------
    trans : pd.DataFrame
        Output of :func:`clean_transactions` (after column normalisation).
    accounts : pd.DataFrame
        Output of :func:`clean_accounts` (after column normalisation).

    Returns
    -------
    pd.DataFrame
        Fully merged AML dataset.
    """
    s_accounts = _prefix_accounts(accounts, "s_", "account")
    r_accounts = _prefix_accounts(accounts, "r_", "account.1")

    aml = trans.merge(s_accounts, on="account", how="left")
    aml = aml.merge(r_accounts, on="account.1", how="left")

    log.info("Merged dataset: %d rows, %d columns", *aml.shape)
    return aml


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def clean_aml(
    trans_path: str,
    accounts_path: str,
    output_path: str | None = None,
    geocode: bool = True,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Full end-to-end AML cleaning pipeline.

    Parameters
    ----------
    trans_path : str
        Path to the raw transactions CSV (e.g. HI-Small_Trans.csv).
    accounts_path : str
        Path to the raw accounts CSV (e.g. HI-Small_accounts.csv).
    output_path : str | None
        If provided, the cleaned DataFrame is saved as a CSV at this path.
        Directories are created automatically. Pass None to skip saving.
    geocode : bool
        Whether to call the Nominatim API to fetch lat/lon for each country.
        Set to False if you are offline or want a faster run.
    overwrite : bool
        If False (default) and *output_path* already exists, the file is not
        overwritten and the existing file is loaded instead.

    Returns
    -------
    pd.DataFrame
        The cleaned, merged AML dataset.

    Examples
    --------
    >>> df = clean_aml(
    ...     trans_path="data/raw/HI-Small_Trans.csv",
    ...     accounts_path="data/raw/HI-Small_accounts.csv",
    ...     output_path="data/processed/aml_clean.csv",
    ...     geocode=False,
    ... )
    >>> df.shape
    (N, 31)
    """
    # Short-circuit if output already exists and overwrite is disabled
    if output_path and os.path.exists(output_path) and not overwrite:
        log.info("Output already exists at %s – loading it.", output_path)
        return pd.read_csv(output_path)

    # 1. Clean individual sources
    accounts = clean_accounts(accounts_path, geocode=geocode)
    trans = clean_transactions(trans_path)

    # 2. Normalise column names
    accounts = _clean_columns(accounts)
    trans = _clean_columns(trans)

    # 3. Merge
    aml_clean = merge_datasets(trans, accounts)

    # 4. Optionally save
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        aml_clean.to_csv(output_path, index=False)
        log.info("Saved cleaned dataset to %s", output_path)

    return aml_clean