from flask import Blueprint, render_template
import pandas as pd, json
from pathlib import Path
from analysis.visuals.aml_viz import (
    plotly_hourly_laundering_rate, plotly_daily_volume, plotly_daily_laundering_rate,
    plotly_laundering_by_payment_format, plotly_laundering_by_amount_bucket,
    plotly_laundering_by_currency, plotly_laundering_rate_by_currency,
    plotly_top_country_corridors, plotly_domestic_vs_crossborder,
    plotly_top_sender_countries, plotly_top_receiver_countries
)
from analysis.cleaning.visualization import get_top_laundering_countries, get_top_country_corridors, get_bank_type_stats, get_entity_type_stats

dashboard_bp = Blueprint('dashboard', __name__)

_data = None
CACHE_PATH = Path(__file__).parent.parent.parent / 'data/processed/charts_cache.json'

def get_data():
    global _data
    if _data is None:
        root = Path(__file__).parent.parent.parent
        _data = {
            'trans':    pd.read_csv(root / 'data/processed/aml_trans.csv'),
            'accounts': pd.read_csv(root / 'data/processed/aml_accounts.csv'),
            'money':    pd.read_csv(root / 'data/processed/aml_money.csv'),
        }
        get_charts(_data['trans'])
    return _data

def get_charts(df):
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    charts = {
        'hourly_chart': plotly_hourly_laundering_rate(df),
        'volume_chart': plotly_daily_volume(df),
        'daily_rate_chart': plotly_daily_laundering_rate(df),
        'payment_format_chart': plotly_laundering_by_payment_format(df),
        'amount_bucket_chart': plotly_laundering_by_amount_bucket(df),
        'laundering_by_currency_chart': plotly_laundering_by_currency(df),
        'laundering_rate_by_currency_chart': plotly_laundering_rate_by_currency(df),
        'top_corridors_chart': plotly_top_country_corridors(df),
        'domestic_vs_crossborder_chart': plotly_domestic_vs_crossborder(df),
        'top_sender_countries_chart': plotly_top_sender_countries(df),
        'top_receiver_countries_chart': plotly_top_receiver_countries(df),
    }
    with open(CACHE_PATH, 'w') as f:
        json.dump(charts, f)
    return charts

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    data = get_data()
    df       = data['trans']
    df_money = data['money'].sort_values('n_transactions', ascending=False)
    top_accounts = data['accounts'].sort_values('laundering_rate', ascending=False).head(10)
    charts = get_charts(df)

    df_clean = pd.read_csv(Path(__file__).parent.parent.parent / 'data/processed/aml_clean.csv')
    top_countries = get_top_laundering_countries(df_clean, top_n=5)
    top_corridors = get_top_country_corridors(df_clean, top_n=5)
    bank_stats    = get_bank_type_stats(df_clean)
    entity_stats  = get_entity_type_stats(df_clean)

    return render_template('dashboard.html',
        total_transactions=f"{len(df):,}",
        laundering_cases=f"{int(df['is_laundering'].sum()):,}",
        laundering_rate=f"{round(df['is_laundering'].mean()*100,2)}%",
        currency_names=json.dumps(df_money['payment_currency'].tolist()),
        currency_volumes=json.dumps(df_money['n_transactions'].tolist()),
        currency_rates=json.dumps((df_money['laundering_rate']*100).round(3).tolist()),
        top_accounts=json.dumps(top_accounts[['entity_name','country','n_transactions','laundering_rate']].assign(laundering_rate=lambda x: (x['laundering_rate']*100).round(2)).to_dict('records')),
        top_countries=top_countries,
        top_corridors=top_corridors,
        bank_stats=bank_stats,
        entity_stats=entity_stats,
        **charts,
    )