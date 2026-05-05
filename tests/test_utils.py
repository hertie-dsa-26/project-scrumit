##test_utils.py exists to test all the existing functions within utils.py to ensure they are working as expected. This will be done using pytest.

##libraries
import pytest as pytest 
import requests as requests
from  utils import convert_currency 

def test_currency_conversion_mock(): 
    #test currency conversion from USD to EUR
    amount = 100
    date = "2023-01-01"
    from_currency = "USD"
    to_currency = "EUR"
    converted_amount = convert_currency(amount, date, from_currency, to_currency)
    assert isinstance(converted_amount, float)
    assert converted_amount > 0
    assert converted_amount != amount
