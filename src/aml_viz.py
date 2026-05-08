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

#currency visualizations 
def plotly_laundering_by_payment_format(df: pd.DataFrame) -> str:
    fmt = (
        df.groupby("payment_format")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .sort_values("rate", ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=fmt["rate"].tolist(),
        y=fmt.index.tolist(),
        orientation='h',
        marker=dict(color='#b5d4f4', line=dict(color='#2a5f8f', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def plotly_laundering_by_amount_bucket(df: pd.DataFrame) -> str:
    df = df.copy()
    df["amount_bucket"] = pd.cut(
        df["amount_paid"],
        bins=[0, 1_000, 10_000, 50_000, 100_000, float("inf")],
        labels=["<1K", "1K–10K", "10K–50K", "50K–100K", ">100K"]
    )
    bucketed = (
        df.groupby("amount_bucket", observed=True)["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    fig = go.Figure(go.Bar(
        x=bucketed.index.astype(str).tolist(),
        y=bucketed["rate"].tolist(),
        marker=dict(color='#c9b5f4', line=dict(color='#4a2a8f', width=1)),
        hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Transaction Amount'},
                         'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def plotly_laundering_by_currency(df: pd.DataFrame) -> str:
    curr = (
        df.groupby("payment_currency")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .sort_values("rate", ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=curr["rate"].tolist(),
        y=curr.index.tolist(),
        orientation='h',
        marker=dict(color='#f4d5b5', line=dict(color='#9b5a2c', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def plotly_laundering_rate_by_currency(df: pd.DataFrame) -> str:
    curr = (
        df.groupby("payment_currency")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .sort_values("rate", ascending=True)  #ascending=True so highest appears at top in horizontal bar
    )
    fig = go.Figure(go.Bar(
        x=curr["rate"].tolist(),
        y=curr.index.tolist(),
        orientation='h',
        marker=dict(color='#9b5a2c'),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    ))
    layout = {
        **LAYOUT,
        'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
        'yaxis': {**LAYOUT['yaxis'], 'title': ''},
    }
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)

#currency visualisations over 

#geographic visualisations
def plotly_top_country_corridors(df: pd.DataFrame) -> str:
    corridors = (
        df.groupby(["s_country", "r_country"])["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .reset_index()
    )
    corridors = corridors[corridors["s_country"] != corridors["r_country"]]
    corridors["corridor"] = corridors["s_country"] + " → " + corridors["r_country"]
    top15 = corridors.nlargest(15, "rate").sort_values("rate", ascending=True)
    fig = go.Figure(go.Bar(
        x=top15["rate"].tolist(),
        y=top15["corridor"].tolist(),
        orientation='h',
        marker=dict(color='#f4b5b5', line=dict(color='#9b2c2c', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
                         'yaxis': {**LAYOUT['yaxis'], 'title': ''}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def plotly_domestic_vs_crossborder(df: pd.DataFrame) -> str:
    df = df.copy()
    df["transfer_type"] = df["country_mismatch"].apply(
        lambda x: "Cross-Border" if x == 1 else "Domestic"
    )
    grouped = (
        df.groupby("transfer_type")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    colors = {"Domestic": "#b5d4f4", "Cross-Border": "#f4b5b5"}
    fig = go.Figure(go.Bar(
        x=grouped.index.tolist(),
        y=grouped["rate"].tolist(),
        marker=dict(
            color=[colors.get(t, "#ccc") for t in grouped.index.tolist()],
            line=dict(color=['#2a5f8f', '#9b2c2c'], width=1)
        ),
        hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'},
                         'xaxis': {**LAYOUT['xaxis'], 'title': ''}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def plotly_top_sender_countries(df: pd.DataFrame) -> str:
    senders = (
        df.groupby("s_country")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .nlargest(15, "rate")
        .sort_values("rate", ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=senders["rate"].tolist(),
        y=senders.index.tolist(),
        orientation='h',
        marker=dict(color='#c9b5f4', line=dict(color='#4a2a8f', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
                         'yaxis': {**LAYOUT['yaxis'], 'title': ''}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def plotly_top_receiver_countries(df: pd.DataFrame) -> str:
    receivers = (
        df.groupby("r_country")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .nlargest(15, "rate")
        .sort_values("rate", ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=receivers["rate"].tolist(),
        y=receivers.index.tolist(),
        orientation='h',
        marker=dict(color='#f4d5b5', line=dict(color='#9b5a2c', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    ))
    layout = {**LAYOUT, 'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
                         'yaxis': {**LAYOUT['yaxis'], 'title': ''}}
    fig.update_layout(**layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)