##utils.py will be used to store helper functions that will be used across the flask app program.

import pandas as pd

#----------------------------------------------
# MAP INTERFACE UTILS
#----------------------------------------------

NAME_TO_ISO = NAME_TO_ISO = {
    'Austria':      40,
    'Australia':    36,
    'Belgium':      56,
    'Brazil':       76,
    'Canada':       124,
    'China':        156,
    'Croatia':      191,
    'Cyprus':       196,
    'Estonia':      233,
    'Finland':      246,
    'France':       250,
    'Germany':      276,
    'Greece':       300,
    'India':        356,
    'Ireland':      372,
    'Israel':       376,
    'Italy':        380,
    'Japan':        392,
    'Latvia':       428,
    'Lithuania':    440,
    'Luxembourg':   442,
    'Malta':        470,
    'Mexico':       484,
    'Netherlands':  528,
    'Portugal':     620,
    'Russia':       643,
    'Saudi Arabia': 682,
    'Slovakia':     703,
    'Slovenia':     705,
    'Spain':        724,
    'Switzerland':  756,
    'UK':           826,
    'USA':          840,
}

# This function computes the laundering rates for each country based on sender and receiver data.
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

# This function computes the laundering rates for each corridor (sender-receiver pair) and returns a list of corridors with their rates and counts.
def compute_corridors(df):
    corridors = (
        df.groupby(['s_country', 'r_country', 's_latitude', 's_longitude', 'r_latitude', 'r_longitude'])
        ['is_laundering']
        .agg(total='sum', count='count')
        .reset_index()
    )
    corridors = corridors[corridors['s_country'] != corridors['r_country']]
    corridors['rate'] = corridors['total'] / corridors['count'] * 100
    
    result = []
    for _, row in corridors.iterrows():
        result.append({
            'from': [row['s_longitude'], row['s_latitude']],
            'to': [row['r_longitude'], row['r_latitude']],
            'rate': round(row['rate'], 4),
            'count': int(row['count']),
            's_country': row['s_country'],
            'r_country': row['r_country'],
            's_iso': NAME_TO_ISO.get(row['s_country']),
            'r_iso': NAME_TO_ISO.get(row['r_country'])
        })
    return result
