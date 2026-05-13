from app import create_app
import pandas as pd
import pytest

#test client fixture for flask app; avoid making real http requests
@pytest.fixture()
def client(): 
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

#mock transactions for src and models; avoid hardcoding mock DF for each test and keeps test data structure consistent
@pytest.fixture()
def sample_transactions():
    return pd.DataFrame({
        "date":                 ["2022-01-01",      "2022-01-02",          "2022-01-03"],
        "time":                 ["10:00:00",         "14:30:00",            "09:15:00"],
        "from_bank":            [1001,               2002,                  1001],
        "account":              [8000001111,         8000002222,            8000001111],
        "to_bank":              [2002,               3003,                  4004],
        "account.1":            [8000002222,         8000003333,            8000004444],
        "amount_received":      [1000.00,            50000.00,              200.00],
        "receiving_currency":   ["US Dollar",        "US Dollar",           "Euro"],
        "amount_paid":          [1000.00,            50000.00,              200.00],
        "payment_currency":     ["US Dollar",        "Bitcoin",             "Euro"],
        "currency_mismatch":    [0,                  1,                     0],
        "payment_format":       ["Wire",             "Bitcoin",             "Cash"],
        "is_laundering":        [0,                  1,                     0],
        "s_bank_name":          ["Boston Bank #1",   "Dallas Savings Bank", "Boston Bank #1"],
        "s_entity_name":        ["Corporation #1",   "Individual #2",       "Corporation #1"],
        "s_entity_type":        ["Corporation",      "Individual",          "Corporation"],
        "s_country":            ["USA",              "USA",                 "USA"],
        "s_latitude":           [42.36,              32.78,                 42.36],
        "s_longitude":          [-71.06,             -96.80,                -71.06],
        "s_bank_type":          ["Commercial",       "Savings",             "Commercial"],
        "r_bank_name":          ["Dallas Savings Bank", "Chicago Bank #3",  "Miami Bank #5"],
        "r_entity_name":        ["Corporation #5",   "Individual #9",       "Corporation #7"],
        "r_entity_type":        ["Corporation",      "Individual",          "Corporation"],
        "r_country":            ["Italy",            "USA",                 "France"],
        "r_latitude":           [32.78,              41.88,                 25.77],
        "r_longitude":          [-96.80,             -87.63,                -80.19],
        "r_bank_type":          ["Savings",          "Commercial",          "Commercial"],
    })