import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
import json

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

LAYOUT = dict(
    margin=dict(t=10, r=10, b=50, l=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans, sans-serif', size=11, color='#6b6b65'),
    xaxis=dict(gridcolor='#e8e6df', zerolinecolor='#e8e6df'),
    yaxis=dict(gridcolor='#e8e6df', zerolinecolor='#e8e6df'),
)

def plotly_hourly_laundering_rate(df: pd.DataFrame) -> str:
    hourly = (
        df.groupby("hour")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    fig = go.Figure(go.Scatter(
        x=hourly.index.tolist(),
        y=hourly["rate"].tolist(),
        mode='lines+markers',
        line=dict(color='#2a5f8f', width=2.5),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(42,95,143,0.07)',
        hovertemplate='Hour %{x}:00<br>Rate: %{y:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Hour of Day'},
                         'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def plotly_daily_volume(df: pd.DataFrame) -> str:
    daily_counts = df.groupby("day_of_week").size().reindex(DAY_ORDER)
    fig = go.Figure(go.Bar(
        x=DAY_ORDER,
        y=daily_counts.tolist(),
        marker=dict(color='#b5d4f4', line=dict(color='#2a5f8f', width=1)),
        hovertemplate='%{x}<br>Transactions: %{y:,}<extra></extra>'
    ))
    layout = {**LAYOUT, 'yaxis': {**LAYOUT['yaxis'], 'title': 'Number of Transactions'}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def plotly_daily_laundering_rate(df: pd.DataFrame) -> str:
    daily = (
        df.groupby("day_of_week")["is_laundering"]
        .agg(total="sum", count="count")
        .reindex(DAY_ORDER)
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    fig = go.Figure(go.Bar(
        x=DAY_ORDER,
        y=daily["rate"].tolist(),
        marker=dict(color='#f4b5b5', line=dict(color='#9b2c2c', width=1)),
        hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)