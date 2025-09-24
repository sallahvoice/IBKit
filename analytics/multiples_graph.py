import plotly.graph_objects as go
from typing import List, Dict, Any
import plotly.graph_objects as go
import datetime as dt
import statsmodels.api as sm
import statsmodels.api as sm
import numpy as np


def firms_multiples_graph(compSet: ComparableSet):
    if not compSet:
        return None
    
    data = compSet.companies_as_dict_list()
    multiples = {
        "Forward Price to Book": {c["ticker"]: c["forward_price_to_book"] for c in data},
        "Forward PE": {c["ticker"]: c["forward_pe"] for c in data},
        "Trailing PE": {c["ticker"]: c["trailing_pe"] for c in data},
        "Forward PS": {c["ticker"]: c["forward_price_to_sale"] for c in data},
        "Trailing EV/EBIT": {c["ticker"]: c["trailing_ev_to_ebit"] for c in data},
        "Trailing EV/S": {c["ticker"]: c["trailing_ev_to_sales"] for c in data},
    }
    
    figures : Dict[str, figure] = {}

    for attr, mapping in multiples.items():
        tickers = list(mapping.keys())
        values = list(mapping.values())
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=tickers,
                y=values,
                name=attr,
                mode="markers",
                text=[f"{t}: {v}" for t, v in mapping.items()],  # hover text
                hoverinfo="text",
                marker={"color": "#2E86C1", "size": 10}
            )
        )

        fig.update_layout(
            title=attr,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"showgrid": False, "zeroline": False},
            yaxis={"showgrid": False, "zeroline": False},
            xaxis_title="Ticker",
            yaxis_title=attr,
            font={"size": 10},
            margin={"l": 10, "r": 10, "t": 30, "b": 10}
        )
        
        figures[attr] = fig

    return figures


def target_company_beta_regression(target_company_ticker: str, timeframe: str) -> Dict[str, Any]:
    if not target_company_ticker or not timeframe:
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
        return None

    tickers = [target_company_ticker, "^GSPC"]
    df = yf.download(tickers, start=start, end=end)["Adj Close"]

    weekly_returns = df.resample("W").ffill().pct_change().dropna()

    x = weekly_returns["^GSPC"]
    y = weekly_returns[target_company_ticker]

    model = sm.OLS(y, sm.add_constant(x))
    results = model.fit()

    # --- regression line ---
    alpha, beta = results.params["const"], results.params[x.name]
    x_range = np.linspace(x.min(), x.max(), 100)
    y_pred = alpha + beta * x_range

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name="Weekly Returns",
        text=[f"Date: {d.date()}, Stock: {s:.2%}, Market: {m:.2%}"
              for d, s, m in zip(weekly_returns.index, y, x)],
        hoverinfo="text",
        marker=dict(color="#2E86C1")
    ))

    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode="lines",
        name=f"Fit: y = {alpha:.3f} + {beta:.3f}x",
        line=dict(color="red")
    ))

    fig.update_layout(
        title=f"{target_company_ticker} vs Market ({timeframe})",
        xaxis_title="Market Returns (^GSPC)",
        yaxis_title=f"{target_company_ticker} Returns",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # --- Return structured output ---
    return {
        "figure": fig,
        "stats": {
            "alpha": float(alpha),
            "beta": float(beta),
            "r_squared": float(results.rsquared),
            "p_values": results.pvalues.to_dict()
        }
    }