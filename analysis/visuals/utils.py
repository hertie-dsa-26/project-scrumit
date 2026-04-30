import pandas as pd


# This function computes the laundering rates for each country based on sender and receiver data.

NAME_TO_ISO = {
    'Australia': 36,
    'Austria': 40,
    'Belgium': 56,
    'Brazil': 76,
    'Canada': 124,
    'China': 156,
    'Croatia': 191,
    'Cyprus': 196,
    'Estonia': 233,
    'Finland': 246,
    'France': 250,
    'Germany': 276,
    'Greece': 300,
    'India': 356,
    'Ireland': 372,
    'Israel': 376,
    'Italy': 380,
    'Japan': 392,
    'Latvia': 428,
    'Lithuania': 440,
    'Luxembourg': 442,
    'Malta': 470,
    'Mexico': 484,
    'Netherlands': 528,
    'Portugal': 620,
    'Russia': 643,
    'Saudi Arabia': 682,
    'Slovakia': 703,
    'Slovenia': 705,
    'Spain': 724,
    'Switzerland': 756,
    'UK': 826,
    'USA': 840,
}

def compute_country_rates(df):
    sender = df.groupby('s_country').agg(total=('is_laundering','count'), laundering=('is_laundering','sum'))
    receiver = df.groupby('r_country').agg(total=('is_laundering','count'), laundering=('is_laundering','sum'))
    sender.index.name = 'country'
    receiver.index.name = 'country'
    combined = sender.add(receiver, fill_value=0)
    combined['rate'] = combined['laundering'] / combined['total'] * 100

    result = {}
    for name, rate in combined['rate'].items():
        iso = NAME_TO_ISO.get(name)
        if iso:
            result[iso] = round(rate, 4)
    return result
    return combined['rate'].round(4).to_dict()