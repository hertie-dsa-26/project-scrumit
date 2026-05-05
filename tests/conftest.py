#fake http requests 

from flask import app
import pandas as pd

import pytest as pytest 

#test client fixture for flask app; avoid making real http requests
@pytest.fixture()
def client(): 
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

#mock transactions for src and models; avoid hardcoding mock DF for each test and keeps test data structure consistent
@pytest.fixture()
def sample_transactions():
    return pd.DataFrame({...})