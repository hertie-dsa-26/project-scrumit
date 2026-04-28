from flask import Blueprint, render_template
import pandas as pd, json
from pathlib import Path
from analysis.visuals.aml_viz import plotly_hourly_laundering_rate, plotly_daily_volume, plotly_daily_laundering_rate

dashboard_bp = Blueprint('dashboard', __name__)

_data = None

def get_data():
    global _data
    if _data is None:
        root = Path(__file__).parent.parent.parent
        _data = {
            'trans':    pd.read_csv(root / 'data/processed/aml_trans.csv'),
            'accounts': pd.read_csv(root / 'data/processed/aml_accounts.csv'),
            'money':    pd.read_csv(root / 'data/processed/aml_money.csv'),
        }
    return _data

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    data = get_data()
    df       = data['trans']
    df_money = data['money'].sort_values('n_transactions', ascending=False)
    top_accounts = data['accounts'].sort_values('laundering_rate', ascending=False).head(10)

    return render_template('dashboard.html',
        total_transactions=f"{len(df):,}",
        laundering_cases=f"{int(df['is_laundering'].sum()):,}",
        laundering_rate=f"{round(df['is_laundering'].mean()*100,2)}%",
        hourly_chart=plotly_hourly_laundering_rate(df),
        volume_chart=plotly_daily_volume(df),
        daily_rate_chart=plotly_daily_laundering_rate(df),
        currency_names=json.dumps(df_money['payment_currency'].tolist()),
        currency_volumes=json.dumps(df_money['n_transactions'].tolist()),
        currency_rates=json.dumps((df_money['laundering_rate']*100).round(3).tolist()),
        top_accounts=json.dumps(top_accounts[['entity_name','country','n_transactions','laundering_rate']].assign(laundering_rate=lambda x: (x['laundering_rate']*100).round(2)).to_dict('records')),
    )