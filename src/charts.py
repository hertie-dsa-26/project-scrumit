import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
import json
import os

#-----------------------------------------------
# DASHBOARD PLOTS UTILS 
#-----------------------------------------------

def _save(fig, path):
    """Helper to serialize and write a figure to disk."""
    with open(path, "w") as f:
        f.write(json.dumps(fig, cls=PlotlyJSONEncoder))

LAYOUT = dict(
    margin=dict(t=10, r=10, b=50, l=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans, sans-serif', size=11, color='#6b6b65'),
    xaxis=dict(gridcolor='#e8e6df', zerolinecolor='#e8e6df'),
    yaxis=dict(gridcolor='#e8e6df', zerolinecolor='#e8e6df'),
)

## TEMPORAL VIEW -------------------------------

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def save_hourly_laundering_rate(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        mode='lines+markers',
        line=dict(color='#2a5f8f', width=2.5),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(42,95,143,0.07)',
        hovertemplate='Hour %{x}:00<br>Rate: %{y:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT, 
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Hour of Day'},
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}

    
    traces = []
    ## global trace
    hourly_all = (
        df.groupby("hour")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    traces.append(go.Scatter(name="All Countries", visible=True,
                             x=hourly_all.index.tolist(), 
                             y=hourly_all["rate"].tolist(),
                             **trace_style))
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        hourly = (
            df[df["s_country"] == country]
            .groupby("hour")["is_laundering"]
            .agg(total="sum", count="count")
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
        )
        traces.append(go.Scatter(name=country, visible=False,
                                 x=hourly.index.tolist(), 
                                 y=hourly["rate"].tolist(),
                                 **trace_style))

    fig = go.Figure(traces)
    fig.update_layout(**layout)
    with open(f"{output_dir}/hourly_chart.json", "w") as f:
        f.write(json.dumps(fig, cls=PlotlyJSONEncoder))

def save_daily_volume(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        marker=dict(color='#b5d4f4', line=dict(color='#2a5f8f', width=1)),
        hovertemplate='%{x}<br>Transactions: %{y:,}<extra></extra>'
    )
    layout = {**LAYOUT,
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Number of Transactions'}}
 
    traces = []
    ## global trace
    daily_all = df.groupby("day_of_week").size().reindex(DAY_ORDER)
    traces.append(go.Bar(name="All Countries", visible=True,
                         x=DAY_ORDER, y=daily_all.tolist(),
                         **trace_style))
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        daily = (
            df[df["s_country"] == country]
            .groupby("day_of_week").size().reindex(DAY_ORDER)
        )
        traces.append(go.Bar(name=country, visible=False,
                             x=DAY_ORDER, y=daily.tolist(),
                             **trace_style))
 
    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/volume_chart.json")

def save_daily_laundering_rate(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        marker=dict(color='#f4b5b5', line=dict(color='#9b2c2c', width=1)),
        hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}
 
    traces = []
    ## global trace
    daily_all = (
        df.groupby("day_of_week")["is_laundering"]
        .agg(total="sum", count="count")
        .reindex(DAY_ORDER)
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    traces.append(go.Bar(name="All Countries", visible=True,
                         x=DAY_ORDER, y=daily_all["rate"].tolist(),
                         **trace_style))
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        daily = (
            df[df["s_country"] == country]
            .groupby("day_of_week")["is_laundering"]
            .agg(total="sum", count="count")
            .reindex(DAY_ORDER)
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
        )
        traces.append(go.Bar(name=country, visible=False,
                             x=DAY_ORDER, y=daily["rate"].tolist(),
                             **trace_style))

    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/daily_rate_chart.json")

## CURRENCY VIEW -------------------------------

def save_laundering_by_payment_format(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        orientation='h',
        marker=dict(color='#b5d4f4', line=dict(color='#2a5f8f', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'}}

    traces = []
    ## global trace
    fmt_all = (
        df.groupby("payment_format")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .sort_values("rate", ascending=True)
    )
    traces.append(go.Bar(name="All Countries", visible=True,
                         x=fmt_all["rate"].tolist(), y=fmt_all.index.tolist(),
                         **trace_style))
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        fmt = (
            df[df["s_country"] == country]
            .groupby("payment_format")["is_laundering"]
            .agg(total="sum", count="count")
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
            .sort_values("rate", ascending=True)
        )
        traces.append(go.Bar(name=country, visible=False,
                             x=fmt["rate"].tolist(), y=fmt.index.tolist(),
                             **trace_style))

    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/payment_format_chart.json")

def save_laundering_by_amount_bucket(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        marker=dict(color='#c9b5f4', line=dict(color='#4a2a8f', width=1)),
        hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Transaction Amount'},
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}
 
    bins = [0, 1_000, 10_000, 50_000, 100_000, float("inf")]
    labels = ["<1K", "1K–10K", "10K–50K", "50K–100K", ">100K"]

    traces = []
    ## global trace
    df_all = df.copy()
    df_all["amount_bucket"] = pd.cut(df_all["amount_paid"], bins=bins, labels=labels)
    bucketed_all = (
        df_all.groupby("amount_bucket", observed=True)["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
    )
    traces.append(go.Bar(name="All Countries", visible=True,
                         x=bucketed_all.index.astype(str).tolist(),
                         y=bucketed_all["rate"].tolist(),
                         **trace_style))
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        df_c = df[df["s_country"] == country].copy()
        df_c["amount_bucket"] = pd.cut(df_c["amount_paid"], bins=bins, labels=labels)
        bucketed = (
            df_c.groupby("amount_bucket", observed=True)["is_laundering"]
            .agg(total="sum", count="count")
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
        )
        traces.append(go.Bar(name=country, visible=False,
                             x=bucketed.index.astype(str).tolist(),
                             y=bucketed["rate"].tolist(),
                             **trace_style))

    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/amount_bucket_chart.json")

def save_laundering_rate_by_currency(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        orientation='h',
        marker=dict(color='#f4d5b5', line=dict(color='#9b5a2c', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'}}

    traces = []
    ## global trace
    curr_all = (
        df.groupby("payment_currency")["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .sort_values("rate", ascending=True)
    )
    traces.append(go.Bar(name="All Countries", visible=True,
                         x=curr_all["rate"].tolist(), y=curr_all.index.tolist(),
                         **trace_style))
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        curr = (
            df[df["s_country"] == country]
            .groupby("payment_currency")["is_laundering"]
            .agg(total="sum", count="count")
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
            .sort_values("rate", ascending=True)
        )
        traces.append(go.Bar(name=country, visible=False,
                             x=curr["rate"].tolist(), y=curr.index.tolist(),
                             **trace_style))

    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/laundering_rate_by_currency_chart.json")

def save_currency_volume(df_money: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        type='bar',
        marker=dict(color='#b5d4f4', line=dict(color='#2a5f8f', width=1)),
        hovertemplate='%{x}<br>Transactions: %{y:,}<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': '', 'tickangle': -30},
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Transactions'}}

    ## This chart IS the currency breakdown — no per-country filter needed
    df_sorted = df_money.sort_values('n_transactions', ascending=False)
    fig = go.Figure(go.Bar(
        x=df_sorted['payment_currency'].tolist(),
        y=df_sorted['n_transactions'].tolist(),
        **trace_style
    ))

    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/currency_volume_chart.json")

def save_currency_laundering_rate(df_money: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        type='bar',
        marker=dict(color='#f4b5b5', line=dict(color='#9b2c2c', width=1)),
        hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': '', 'tickangle': -30},
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}

    ## This chart IS the currency breakdown — no per-country filter needed
    df_sorted = df_money.sort_values('n_transactions', ascending=False)
    fig = go.Figure(go.Bar(
        x=df_sorted['payment_currency'].tolist(),
        y=(df_sorted['laundering_rate'] * 100).round(3).tolist(),
        **trace_style
    ))

    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/currency_laundering_rate_chart.json")

# GEOGRAPHICAL VIEW -------------------------------

def save_top_country_corridors(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        orientation='h',
        marker=dict(color='#f4b5b5', line=dict(color='#9b2c2c', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
              'yaxis': {**LAYOUT['yaxis'], 'title': ''}}
 
    def get_top_corridors(data):
        corridors = (
            data.groupby(["s_country", "r_country"])["is_laundering"]
            .agg(total="sum", count="count")
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
            .reset_index()
        )
        corridors = corridors[corridors["s_country"] != corridors["r_country"]]
        corridors = corridors[corridors["count"] > 10]
        corridors["corridor"] = corridors["s_country"] + " → " + corridors["r_country"]
        return corridors.nlargest(15, "rate").sort_values("rate", ascending=True)

 
    traces = []
    ## global trace
    top_all = get_top_corridors(df)
    traces.append(go.Bar(name="All Countries", visible=True,
                         x=top_all["rate"].tolist(), y=top_all["corridor"].tolist(),
                         **trace_style))
    ## country-specific traces
    ## filtered by s_country — corridors from selected country
    for country in sorted(df["s_country"].dropna().unique()):
        top = get_top_corridors(df[df["s_country"] == country])
        traces.append(go.Bar(name=country, visible=False,
                             x=top["rate"].tolist(), y=top["corridor"].tolist(),
                             **trace_style))

    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/top_corridors_chart.json")

def save_domestic_vs_crossborder(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    # colors vary by bar category so trace_style is partial here
    layout = {**LAYOUT,
              'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'},
              'xaxis': {**LAYOUT['xaxis'], 'title': ''}}
 
    colors = {"Domestic": "#b5d4f4", "Cross-Border": "#f4b5b5"}
    border_colors = {"Domestic": "#2a5f8f", "Cross-Border": "#9b2c2c"}
 
    def make_trace(data, name, visible):
        data = data.copy()
        data["transfer_type"] = data["country_mismatch"].apply(
            lambda x: "Cross-Border" if x == 1 else "Domestic"
        )
        grouped = (
            data.groupby("transfer_type")["is_laundering"]
            .agg(total="sum", count="count")
            .assign(rate=lambda x: x["total"] / x["count"] * 100)
        )
        return go.Bar(
            name=name,
            visible=visible,
            x=grouped.index.tolist(),
            y=grouped["rate"].tolist(),
            marker=dict(
                color=[colors.get(t, "#ccc") for t in grouped.index.tolist()],
                line=dict(color=[border_colors.get(t, "#999") for t in grouped.index.tolist()], width=1)
            ),
            hovertemplate='%{x}<br>Rate: %{y:.3f}%<extra></extra>'
        )
 
    ## global trace
    traces = [make_trace(df, "All Countries", True)]
    ## country-specific traces
    for country in sorted(df["s_country"].dropna().unique()):
        traces.append(make_trace(df[df["s_country"] == country], country, False))
 
    fig = go.Figure(traces)
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/domestic_vs_crossborder_chart.json")

def save_top_sender_countries(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        orientation='h',
        marker=dict(color='#c9b5f4', line=dict(color='#4a2a8f', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
              'yaxis': {**LAYOUT['yaxis'], 'title': ''}}
 
    ## This chart IS the country breakdown — no per-country filter needed
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
        **trace_style
    ))
 
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/top_sender_countries_chart.json")
 
def save_top_receiver_countries(df: pd.DataFrame, output_dir: str):
    
    # Define graph style
    trace_style = dict(
        orientation='h',
        marker=dict(color='#f4d5b5', line=dict(color='#9b5a2c', width=1)),
        hovertemplate='%{y}<br>Rate: %{x:.3f}%<extra></extra>'
    )
    layout = {**LAYOUT,
              'xaxis': {**LAYOUT['xaxis'], 'title': 'Laundering Rate (%)'},
              'yaxis': {**LAYOUT['yaxis'], 'title': ''}}
 
    ## This chart IS the country breakdown — no per-country filter needed
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
        **trace_style
    ))

    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/top_receiver_countries_chart.json")

def save_corridor_bubble(df: pd.DataFrame, output_dir: str):
    corridors = (
        df.groupby(["s_country", "r_country"])["is_laundering"]
        .agg(total="sum", count="count")
        .assign(rate=lambda x: x["total"] / x["count"] * 100)
        .reset_index()
    )
    corridors = corridors[corridors["s_country"] != corridors["r_country"]]
    corridors = corridors[corridors["count"] >= 500]
    corridors["corridor"] = corridors["s_country"] + " → " + corridors["r_country"]

    fig = go.Figure(go.Scatter(
        x=corridors["count"].tolist(),
        y=corridors["rate"].tolist(),
        mode='markers',
        marker=dict(
            size=corridors["total"].apply(lambda x: max(6, min(40, x * 0.3))).tolist(),
            color='#f4b5b5',
            line=dict(color='#9b2c2c', width=1),
            opacity=0.7,
        ),
        text=corridors["corridor"].tolist(),
        customdata=list(zip(corridors["total"].tolist(), corridors["count"].tolist())),
        hovertemplate='<b>%{text}</b><br>Rate: %{y:.2f}%<br>Cases: %{customdata[0]}<br>Transactions: %{customdata[1]:,}<extra></extra>'
    ))

    layout = {**LAYOUT,
            'xaxis': {**LAYOUT['xaxis'], 'title': 'Transaction Volume', 'type': 'log'},
            'yaxis': {**LAYOUT['yaxis'], 'title': 'Laundering Rate (%)'}}
    fig.update_layout(**layout)
    _save(fig, f"{output_dir}/corridor_bubble_chart.json")

# STATS OVERVIEW -------------------------------

def save_overview(df: pd.DataFrame, df_accounts: pd.DataFrame, df_clean: pd.DataFrame, output_dir: str):
    from src.cleaning_visualization import (
        get_top_laundering_countries, get_top_country_corridors,
        get_bank_type_stats, get_entity_type_stats,
        get_top_laundering_payment_format
    )

    top_accounts = (
        df_accounts
        .sort_values("laundering_rate", ascending=False)
        .head(10)
        .assign(laundering_rate=lambda x: (x["laundering_rate"] * 100).round(2))
        [["entity_name", "country", "n_transactions", "laundering_rate"]]
        .to_dict("records")
    )
    
    countries = sorted(df_clean["s_country"].dropna().unique().tolist())
    
    # build per-country data
    by_country = {}
    for c in countries:
        df_c = df[df["s_country"] == c]
        by_country[c] = {
            "total_transactions": f"{len(df_c):,}",
            "laundering_cases":   f"{int(df_c['is_laundering'].sum()):,}",
            "laundering_rate":    f"{round(df_c['is_laundering'].mean() * 100, 2)}%",
            "top_countries":      get_top_laundering_countries(df_clean, top_n=5, country=c),
            "top_corridors":      get_top_country_corridors(df_clean, top_n=5, country=c),
            "bank_stats":         get_bank_type_stats(df_clean, country=c),
            "entity_stats":       get_entity_type_stats(df_clean, country=c),
            "top_payment_format": get_top_laundering_payment_format(df_clean, country=c),
    }

    overview = {
        "total_transactions": f"{len(df):,}",
        "laundering_cases":   f"{int(df['is_laundering'].sum()):,}",
        "laundering_rate":    f"{round(df['is_laundering'].mean() * 100, 2)}%",
        "top_accounts":       top_accounts,
        "top_countries":      get_top_laundering_countries(df_clean, top_n=5),
        "top_corridors":      get_top_country_corridors(df_clean, top_n=5),
        "bank_stats":         get_bank_type_stats(df_clean),
        "entity_stats":       get_entity_type_stats(df_clean),
        "top_payment_format": get_top_laundering_payment_format(df_clean), 
        "countries_list":     countries,
        "by_country":         by_country,
    }

    with open(f"{output_dir}/overview.json", "w") as f:
        json.dump(overview, f)
 
#-----------------------------------------------
# precompute all
#-----------------------------------------------

def precompute_all(df: pd.DataFrame, df_money: pd.DataFrame, df_accounts: pd.DataFrame, df_clean: pd.DataFrame, 
                   output_dir: str = "app/static/charts"):
    os.makedirs(output_dir, exist_ok=True)
 
    print("Saving hourly laundering rate...")
    save_hourly_laundering_rate(df, output_dir)
 
    print("Saving daily volume...")
    save_daily_volume(df, output_dir)
 
    print("Saving daily laundering rate...")
    save_daily_laundering_rate(df, output_dir)
 
    print("Saving laundering by payment format...")
    save_laundering_by_payment_format(df, output_dir)
 
    print("Saving laundering by amount bucket...")
    save_laundering_by_amount_bucket(df, output_dir)
 
    print("Saving laundering rate by currency...")
    save_laundering_rate_by_currency(df, output_dir)

    print("Saving currency volume...")
    save_currency_volume(df_money, output_dir)

    print("Saving currency laundering rate...")
    save_currency_laundering_rate(df_money, output_dir)
 
    print("Saving top country corridors...")
    save_top_country_corridors(df, output_dir)
 
    print("Saving domestic vs cross-border...")
    save_domestic_vs_crossborder(df, output_dir)
 
    print("Saving top sender countries...")
    save_top_sender_countries(df, output_dir)
 
    print("Saving top receiver countries...")
    save_top_receiver_countries(df, output_dir)

    print("Saving overview stats...")
    save_overview(df, df_accounts, df_clean, output_dir)
    
    print("Saving corridor bubble chart...")
    save_corridor_bubble(df, output_dir)

    print(f"All charts saved to {output_dir}")

    
