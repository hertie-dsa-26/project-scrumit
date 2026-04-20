##utils.py will be used to store helper functions that will be used across the flask app program.
##calling on https://frankfurter.dev/docs/ for currency conversion.

##in terminal: uv sync
import requests as requests

#currency conversion function
def convert_currency(amount, from_currency, to_currency="EUR"):
    response = requests.get("https://api.frankfurter.app/latest",
                            params={"from": from_currency, "to": to_currency}
                            )
    response.raise_for_status()
    rate = response.json()["rates"][to_currency]
    return round(amount * rate, 2)

