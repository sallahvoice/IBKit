"""
A module focused on graphing stocks,
dedicated to the user target company (the company being analyzed).
"""

try:
    import datetime as dt
    from typing import Dict

    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import yfinance as yf
    from matplotlib.figure import Figure as MPLFigure
    from plotly.graph_objs import Figure as PlotlyFigure
except ImportError as e:
    raise ImportError(f"failed to import libraries in {__file__}") from e


def graph_target_ticker_price_vol(
    target_company_ticker: str, timeframe: str
) -> Dict[str, PlotlyFigure]:
    """User target company graph: price + volume (Plotly)"""
    if not target_company_ticker:
        return {}

    end = dt.datetime.now()
    if timeframe == "1week":
        start = end - dt.timedelta(days=7)
    elif timeframe == "1month":
        start = end - dt.timedelta(days=30)
    elif timeframe == "ytd":
        start = dt.datetime(end.year, 1, 1)
    elif timeframe == "1y":
        start = end - dt.timedelta(days=365)
    elif timeframe == "10yrs":
        start = end - dt.timedelta(days=365 * 10)
    else:
        return {}

    df = yf.download(target_company_ticker, start=start, end=end)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"].round(2),
            mode="lines",
            name="Close Price",
            line={"color": "#2E86C1", "width": 2},
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            yaxis="y2",
            opacity=0.3,
            marker_color="#85929E",
        )
    )

    fig.update_layout(
        title=f"{target_company_ticker} - {timeframe.upper()}",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"showgrid": False, "zeroline": False},
        yaxis={"title": "Price", "showgrid": False, "zeroline": False},
        yaxis2={
            "title": "Volume",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
            "zeroline": False,
        },
        font={"size": 10},
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
    )

    return {target_company_ticker: fig}


def graph_target_ticker_basic_stats(
    target_company_ticker: str, timeframe: str
) -> Dict[str, MPLFigure]:
    """User target company stats: simple summary table (Matplotlib)"""
    if not target_company_ticker:
        return {}

    end = dt.datetime.now()
    if timeframe == "1week":
        start = end - dt.timedelta(days=7)
    elif timeframe == "1month":
        start = end - dt.timedelta(days=30)
    elif timeframe == "ytd":
        start = dt.datetime(end.year, 1, 1)
    elif timeframe == "1y":
        start = end - dt.timedelta(days=365)
    elif timeframe == "10yrs":
        start = end - dt.timedelta(days=365 * 10)
    else:
        return {}

    df = yf.download(target_company_ticker, start=start, end=end)
    target_company_stats = df["Close"].describe(percentiles=[0.1, 0.5, 0.9])

    fig, ax = plt.subplots(figsize=(3, 2))
    ax.axis("off")

    table = ax.table(
        cellText=[[f"${val:.2f}"] for val in target_company_stats.values],
        rowLabels=target_company_stats.index,
        colLabels=[f"{target_company_ticker} ({timeframe})"],
        cellLoc="center",
        loc="center",
        colWidths=[0.3],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.5)

    fig.patch.set_alpha(0)
    plt.tight_layout()

    return {target_company_ticker: fig}
