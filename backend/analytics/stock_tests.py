"""statistical tests on the analyzed firm"""

try:
    import datetime as dt
    import os
    from datetime import datetime
    from typing import Dict

    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import requests
    import yfinance as yf
    from dotenv import load_dotenv
    from plotly.subplots import make_subplots
    from scipy.stats import gaussian_kde, norm
    from utils.decorators import disk_cache
except ImportError as e:
    raise ImportError(f"failed to import dependencies in {__file__}") from e


load_dotenv()
polyapi = os.getenv("POLYGON-API-KEY")


def beta_corr(
    target_company_ticker: str, timeframe: str, rolling_window: int
) -> Dict[str, go.Figure]:
    """
    Compute and plot rolling correlation and rolling beta of a stock vs. the S&P 500.

    Args:
        target_company_ticker (str): Stock ticker symbol.
        timeframe (str): One of {"ytd", "1y", "5yrs", "10yrs"}.
        rolling_window (int): Window size (in days) for rolling calculations.

    Returns:
        Dict[str, go.Figure]: Dictionary mapping ticker to Plotly figure.
    """
    if not target_company_ticker:
        return None

    end = dt.datetime.now()
    if timeframe == "ytd":
        start = dt.datetime(end.year, 1, 1)
    elif timeframe == "1y":
        start = end - dt.timedelta(days=365)
    elif timeframe == "5yrs":
        start = end - dt.timedelta(days=365 * 5)
    elif timeframe == "10yrs":
        start = end - dt.timedelta(days=365 * 10)
    else:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    tickers = [target_company_ticker, "^GSPC"]
    df = yf.download(tickers, start=start, end=end)["Adj Close"]
    returns = df.pct_change().dropna()

    # Rolling metrics
    rolling_corr = (
        returns[target_company_ticker]
        .rolling(window=rolling_window)
        .corr(returns["^GSPC"])
    )
    rolling_cov = (
        returns[target_company_ticker]
        .rolling(window=rolling_window)
        .cov(returns["^GSPC"])
    )
    rolling_var = returns["^GSPC"].rolling(window=rolling_window).var()
    rolling_beta = rolling_cov / rolling_var

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=rolling_corr.index,
            y=rolling_corr,
            name="Rolling Correlation",
            mode="lines",
            line={"color": "#FF00FF", "width": 1.5},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=rolling_beta.index,
            y=rolling_beta,
            name="Rolling Beta",
            mode="lines",
            line={"color": "#39FF14", "width": 1.5},
        )
    )

    fig.update_layout(
        title=f"{target_company_ticker}: Rolling Beta & Correlation vs S&P 500",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white", "size": 10},
        showlegend=True,
    )

    fig.update_xaxes(
        title_text="Date",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="rgba(128,128,128,0.5)",
    )

    fig.update_yaxes(
        title_text="Value",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="rgba(128,128,128,0.5)",
    )

    return {target_company_ticker: fig}


def stock_return_stat_tests(
    target_company_ticker: str, timeframe: str
) -> Dict[str, go.Figure]:
    """
    Plot empirical return distribution (KDE) against a fitted normal distribution.
    Also reports skewness and kurtosis.

    Args:
        target_company_ticker (str): Stock ticker symbol.
        timeframe (str): One of {"ytd", "1y", "5yrs", "10yrs"}.

    Returns:
        Dict[str, go.Figure]: Dictionary mapping ticker to Plotly figure.
    """
    if not target_company_ticker:
        return None

    end = dt.datetime.now()
    if timeframe == "ytd":
        start = dt.datetime(end.year, 1, 1)
    elif timeframe == "1y":
        start = end - dt.timedelta(days=365)
    elif timeframe == "5yrs":
        start = end - dt.timedelta(days=365 * 5)
    elif timeframe == "10yrs":
        start = end - dt.timedelta(days=365 * 10)
    else:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    df = yf.download(target_company_ticker, start=start, end=end)["Adj Close"]
    returns = df.pct_change().dropna()

    # Stats
    returns_mean = returns.mean()
    returns_std = returns.std()
    returns_kurt = returns.kurtosis() + 3  # excess → normal kurtosis
    returns_skew = returns.skew()

    # KDE of actual returns
    kde_returns = gaussian_kde(returns)

    # Range for KDE and normal PDF
    x_range = np.linspace(
        returns.min(),
        returns.max(),
        1000,
    )

    # Normal distribution PDF
    normal_pdf = norm.pdf(x_range, loc=returns_mean, scale=returns_std)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=kde_returns(x_range),
            name="Empirical KDE",
            mode="lines",
            line={"color": "#39FF14", "width": 2},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=normal_pdf,
            name="Normal PDF",
            mode="lines",
            line={"color": "#FF10F0", "width": 2},
        )
    )

    fig.update_layout(
        title=(
            f"{target_company_ticker} Returns Distribution vs Normal<br>"
            f"Returns Kurtosis: {returns_kurt:.2f} (Normal: 3.00)<br>"
            f"Returns Skewness: {returns_skew:.2f} (Normal: 0.00)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white", "size": 10},
        showlegend=True,
    )

    fig.update_xaxes(
        title_text="Returns",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="rgba(128,128,128,0.5)",
    )

    fig.update_yaxes(
        title_text="Density",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="rgba(128,128,128,0.5)",
    )

    return {target_company_ticker: fig}


@disk_cache(namespace="polygon")
def fetch_polygon_realized_vol(
    target_company_ticker: str, rolling_window: int, api_key: str
) -> pd.Series:
    """
    Fetch realized volatility (annualized) from Polygon API.
    """
    url = (
        f"https://api.polygon.io/v1/indicators/volatility/{target_company_ticker}"
        f"?timespan=day&window={rolling_window}&series_type=close&apiKey={api_key}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            raise ValueError(f"No 'results' in Polygon response: {data}")

        dates = [
            datetime.fromtimestamp(item["timestamp"] / 1000) for item in data["results"]
        ]
        values = [float(item["value"]) for item in data["results"]]

        return pd.Series(
            data=values,
            index=pd.to_datetime(dates),
            name=f"realized_{rolling_window}d_vol",
        )

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch or format realized vol in {__file__} "
            f"for {target_company_ticker}: {e}"
        ) from e


def rolling_and_implied_vol(
    target_company_ticker: str, timeframe: str
) -> Dict[str, go.Figure]:
    """
    Build a 1x2 subplot figure for a target company:
      - left: time series of returns
      - right: volatility measures panel

    Args:
        target_company_ticker (str): Ticker symbol (e.g. "AAPL").
        timeframe (str): One of: "1y", "5yrs", "10yrs".

    Returns:
        Dict[str, go.Figure]: Mapping ticker -> configured Plotly figure.
    """

    if not target_company_ticker:
        return None

    end = dt.datetime.now()
    if timeframe == "1y":
        start = end - dt.timedelta(days=365)
    elif timeframe == "5yrs":
        start = end - dt.timedelta(days=365 * 5)
    elif timeframe == "10yrs":
        start = end - dt.timedelta(days=365 * 10)
    else:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    df = yf.download(target_company_ticker, start=start, end=end)["Adj Close"]
    returns = df.pct_change().dropna()

    sq_7d_dev = (returns - returns.rolling(window=7).mean()) ** 2 * 252
    sq_30d_dev = (returns - returns.rolling(window=30).mean()) ** 2 * 252

    # Only fetch if API key is available
    realized_7d_vol = None
    realized_30d_vol = None
    if polyapi:
        try:
            realized_7d_vol = fetch_polygon_realized_vol(
                target_company_ticker=target_company_ticker,
                rolling_window=7,
                api_key=polyapi,
            )
            realized_30d_vol = fetch_polygon_realized_vol(
                target_company_ticker=target_company_ticker,
                rolling_window=30,
                api_key=polyapi,
            )
        except Exception:
            pass  # Continue without Polygon data

    returns = returns[30:]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=[f"{target_company_ticker} Returns", "Volatility Measures"],
        horizontal_spacing=0.1,
    )

    # Stock returns graph
    fig.add_trace(
        go.Scatter(
            x=returns.index,
            y=returns.values,
            name="Returns",
            mode="lines",
            line={"color": "#FF00FF", "width": 1.5},
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # Add Polygon data if available
    if realized_7d_vol is not None:
        fig.add_trace(
            go.Scatter(
                x=realized_7d_vol.index,
                y=realized_7d_vol,
                name="7d Realized Vol",
                mode="lines",
                line={"color": "#00FF00", "width": 1.5},
                showlegend=True,
            ),
            row=1,
            col=2,
        )

    if realized_30d_vol is not None:
        fig.add_trace(
            go.Scatter(
                x=realized_30d_vol.index,
                y=realized_30d_vol,
                name="30d Realized Vol",
                mode="lines",
                line={"color": "#39FF14", "width": 1.5},
                showlegend=True,
            ),
            row=1,
            col=2,
        )

    fig.add_trace(
        go.Scatter(
            x=sq_30d_dev.index,
            y=np.sqrt(sq_30d_dev.rolling(30).mean()),
            name="30d rolling Vol",
            mode="lines",
            line={"color": "#FF10F0", "width": 1.5},
            showlegend=True,
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=sq_7d_dev.index,
            y=np.sqrt(sq_7d_dev.rolling(7).mean()),
            name="7d Rolling Vol",
            mode="lines",
            line={"color": "#FF3131", "width": 1.5},
            showlegend=True,
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white", "size": 10},
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
    )

    for col in [1, 2]:
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="rgba(128,128,128,0.5)",
            row=1,
            col=col,
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="rgba(128,128,128,0.5)",
            title_text="Returns" if col == 1 else "Volatility",
            row=1,
            col=col,
        )

    return {target_company_ticker: fig}
