"""
Financial data fetching and analysis module.
"""

import json
import os
from io import BytesIO
from typing import List, Tuple, Optional

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv


try:
    from backend.domain.comparables import ComparableSet
    from backend.simplai.ai import extract_info_gemini
    from backend.utils.decorators import retry
    from backend.utils.logger import get_logger
    from backend.utils.redis_client import redis_client
    from backend.ingest.webhook import notify_cache_expiry
except ImportError as e:
    print("IMPORT ERROR IN fetch.py:", e)
    raise


load_dotenv()
api_key = os.getenv("FINANCIAL-PREP-API-KEY")
currancy_api_key = os.getenv("CURRANCY-API-KEY")
logger = get_logger(__file__)


def are_dataframes_equal(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    Sophisticated DataFrame comparison that handles common financial data issues.
    """
    try:
        # Quick check: different shapes = definitely different
        if df1.shape != df2.shape:
            return False

        # Check if columns are the same (order doesn't matter)
        if set(df1.columns) != set(df2.columns):
            return False

        # Sort columns to ensure same order for comparison
        df1_sorted = df1.reindex(sorted(df1.columns), axis=1).reset_index(drop=True)
        df2_sorted = df2.reindex(sorted(df2.columns), axis=1).reset_index(drop=True)

        # Compare using pandas equals with some tolerance for floating point
        return df1_sorted.equals(df2_sorted)

    except (ValueError, KeyError):  # More specific exceptions
        # If comparison fails for any reason, assume they're different
        return False


def compare_ticker_data(new_data: list, cached_data: list) -> bool:
    """
    Compare ticker-level data (list of statement dictionaries).

    Args:
        new_data: List of {'statement_type': str, 'data': list} dicts
        cached_data: List of {'statement_type': str, 'data': list} dicts

    Returns:
        bool: True if data is the same, False if different
    """
    try:
        # Quick check: different number of statements
        if len(new_data) != len(cached_data):
            return False

        # Sort by statement type for consistent comparison
        new_sorted = sorted(new_data, key=lambda x: x["statement_type"])
        cached_sorted = sorted(cached_data, key=lambda x: x["statement_type"])

        # Compare each statement
        for new_stmt, cached_stmt in zip(new_sorted, cached_sorted):
            if new_stmt["statement_type"] != cached_stmt["statement_type"]:
                return False

            # Convert to DataFrames and compare
            new_df = pd.DataFrame(new_stmt["data"])
            cached_df = pd.DataFrame(cached_stmt["data"])

            if not are_dataframes_equal(new_df, cached_df):
                return False

        return True

    except (ValueError, KeyError):  # More specific exceptions
        # If comparison fails, assume data is different
        return False


BASE_URL = "https://financialmodelingprep.com/api/v3"
SCREENER_URL = "https://financialmodelingprep.com/stable/company-screener"
CURRANCY_URL = "https://api.beta.fastforex.io/"
REQUIRED_STATEMENTS = (
    "income-statement",
    "balance-sheet-statement",
    "cash-flow-statement",
)


@retry
def target_company_filters(target_company_ticker: str) -> Tuple[float, float]:
    """
    Get market cap and beta for the target company from Yahoo Finance.
    Returns a tuple (market_cap, beta).
    """
    if not target_company_ticker:
        return None

    yf_ticker = yf.Ticker(target_company_ticker)
    info = yf_ticker.info

    if not info:
        return None

    market_cap = info.get("marketCap")
    beta = info.get("beta")

    if market_cap is None or beta is None:
        return None

    return market_cap, beta


def screener(
    mc: float, beta: float, country: str = "US", limit: int = 100
) -> List[str]:
    """
    Returns a list of comparable tickers from FMP screener.
    """
    mc_low = 0.2 * mc
    mc_high = 5 * mc

    beta_low = 0.7 * beta
    beta_high = 1.5 * beta

    params = {
        "marketCapMoreThan": mc_low,
        "marketCapLowerThan": mc_high,
        "betaMoreThan": beta_low,
        "betaLowerThan": beta_high,
        "country": country,
        "limit": limit,
        "apikey": api_key,
    }

    try:
        response = requests.get(SCREENER_URL, params=params, timeout=4)
        response.raise_for_status()
        data = response.json()
        tickers = [c.get("symbol") for c in data if c.get("symbol")]
        return tickers

    except requests.RequestException as e:
        logger.error(f"Failed to fetch comparables: {e}")
        return []


@retry
def create_financial_data(tickers: List[str]) -> List[pd.DataFrame]: #target company+screener tickers
    """Fetch financial data with ticker-level caching and smart comparison"""
    if not api_key:
        return []

    if not tickers:
        return []

    dfs = []

    for ticker in tickers:
        cache_key = f"financial_data:{ticker}"
        cached_data_found = False

        # Try to get all statements for this ticker from cache
        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    cached_dict = json.loads(cached_data)
                    for statement_data in cached_dict:
                        cached_df = pd.DataFrame(statement_data["data"])
                        cached_df["ticker"] = ticker
                        cached_df["statement_type"] = statement_data["statement_type"]
                        dfs.append(cached_df)
                    if logger:
                        logger.info(f"Using cached data for {ticker}")
                    cached_data_found = True
                    continue
            except (json.JSONDecodeError, ConnectionError) as e:  # Specific exceptions
                if logger:
                    logger.warning(f"Cache read failed for {cache_key}: {e}")

        # Fetch from API if not in cache
        if not cached_data_found:
            ticker_data = []  # Store all statements for this ticker

            for statement in REQUIRED_STATEMENTS:
                try:
                    url = f"{BASE_URL}/{statement}/{ticker}?apikey={api_key}"
                    response = requests.get(url, timeout=10)

                    if response.status_code != 200:
                        if logger:
                            logger.warning(
                                f"Failed to fetch {ticker} {statement}: {response.status_code}"
                            )
                        continue

                    data = response.json()
                    if not data:
                        continue

                    # Create DataFrame
                    if isinstance(data, dict):
                        df = pd.DataFrame([data])
                    else:
                        df = pd.DataFrame(data)

                    df["ticker"] = ticker
                    df["statement_type"] = statement

                    # Store for caching
                    ticker_data.append(
                        {"statement_type": statement, "data": df.to_dict("records")}
                    )

                    dfs.append(df)

                except (
                    requests.RequestException,
                    ValueError,
                ) as e:
                    if logger:
                        logger.error(f"Error fetching {ticker} {statement}: {e}")
                    continue

            # Cache all statements for this ticker with smart comparison
            if redis_client and ticker_data:
                try:
                    # Check if data actually changed before notifying webhook
                    should_notify = False
                    try:
                        old_cached_data = redis_client.get(cache_key)
                        if old_cached_data:
                            old_data = json.loads(old_cached_data)
                            # Use sophisticated comparison instead of simple JSON comparison
                            if not compare_ticker_data(ticker_data, old_data): 
                                should_notify = True
                        else:
                            should_notify = True  # First time caching this ticker
                    except (json.JSONDecodeError, ConnectionError):
                        should_notify = True  # Error reading cache, assume data changed

                    # Always update cache with latest data
                    redis_client.set(cache_key, json.dumps(ticker_data))

                    # Only notify webhook if data actually changed
                    if should_notify:
                        notify_cache_expiry(cache_key)

                except ConnectionError as e:
                    if logger:
                        logger.warning(f"Cache write failed for {cache_key}: {e}")

    if dfs and logger:
        logger.info(f"Fetched {len(dfs)} datasets")
    return dfs


def transpose_dataframes(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """Transpose DataFrames for better readability"""
    if not dfs:
        return []

    transposed_dfs = []

    for df in dfs:
        if "date" in df.columns:
            try:
                transposed = df.set_index("date").T.reset_index()
                transposed = transposed.rename(columns={"index": "metric"})
                str_df = transposed.astype(str)
                transposed_dfs.append(str_df)
            except (ValueError, KeyError) as e:  # Specific exceptions
                if logger:
                    logger.warning(f"Transpose formatting failed: {e}")
                transposed_dfs.append(df)
        else:
            transposed_dfs.append(df)
    return transposed_dfs


def convert_to_millions(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """Convert large numeric values to millions for better readability"""
    if not dfs:
        return []

    formatted_dfs = []

    for df in dfs:
        try:
            df_formatted = df.copy()
            numeric_columns = df_formatted.select_dtypes(include=["number"]).columns

            for col in numeric_columns:
                mask = df_formatted[col].abs() >= 1_000_000
                df_formatted.loc[mask, col] = df_formatted.loc[mask, col] / 1_000_000

            formatted_dfs.append(df_formatted)

        except (ValueError, KeyError) as e:  # Specific exceptions
            if logger:
                logger.warning(f"Error converting to millions: {e}")
            formatted_dfs.append(df)
    return formatted_dfs


def convert_to_dollars(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """convets data frames currancies to american dollars"""
    if not dfs:
        return []

    converted_dfs = []
    for df in dfs:
        try:
            # need to make sure we can access currency by df attributes
            currency = df.attrs.get("currency", "USD")

            if currency == "USD":
                converted_dfs.append(df.copy())
                continue

            df_converted = df.copy()
            numeric_columns = df_converted.select_dtypes(include=["number"]).columns

            # fetch conversion ratio
            try:
                currancy_url = (
                f"{CURRANCY_URL}/convert?from={currency}&to=USD"
                f"&amount=1&api_key={currancy_api_key}"
                )

                response = requests.get(currancy_url, timeout=4)
                response.raise_for_status()
                data = response.json()
                ratio = data.get(
                    "value"
                )  # need to make sure api response provide "value"
                if not ratio:
                    converted_dfs.append(df)
                    continue
            except requests.RequestException as e:
                print(f"Currency conversion failed for {currency}: {e}")
                converted_dfs.append(df)
                continue

            for col in numeric_columns:
                mask = df_converted[col].abs() >= 1_000_000
                df_converted.loc[mask, col] = df_converted.loc[mask, col] / ratio

            df_converted.attrs["currency"] = "USD"
            converted_dfs.append(df_converted)

        except (ValueError, KeyError, TypeError) as e:
            print(f"Failed to process dataframe: {e}")
            converted_dfs.append(df)

    return converted_dfs


def save_as_excel(dfs: List[pd.DataFrame]) -> Optional[BytesIO]:
    """Save a list of DataFrames into an Excel file in memory."""
    if not dfs:
        if logger:
            logger.error("No DataFrames to save")
        return None

    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for i, df in enumerate(dfs):
                sheet_name = f"Sheet_{i+1}"
                if "ticker" in df.columns and "statement_type" in df.columns:
                    ticker = df["ticker"].iloc[0]
                    statement = df["statement_type"].iloc[0].replace("-statement", "")
                    sheet_name = f"{ticker}_{statement}"[:31]
                df.to_excel(writer, index=False, sheet_name=sheet_name)
        return output
    except (ValueError, KeyError, IOError) as e:  # Specific exceptions
        if logger:
            logger.error(f"Error saving Excel: {e}")
        return None


def ai_analysis(
    dfs: List[pd.DataFrame], user_prompt: Optional[str] = None
) -> Optional[str]:
    """Perform AI analysis on financial data"""
    if not dfs:
        if logger:
            logger.error("No DataFrames available for analysis")
        return None

    if not user_prompt:
        if logger:
            logger.warning("No user prompt provided")
        return None

    try:
        combined_data = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
        result = extract_info_gemini(combined_data, user_prompt)
        if logger:
            logger.info("AI analysis completed")
        return result
    except (ValueError, KeyError) as e:  # Specific exceptions
        if logger:
            logger.error(f"AI analysis failed: {e}")
        return None


def run_financial_analysis(user_prompt: Optional[str] = None) -> Optional[dict]:
    """Run the complete financial analysis pipeline"""

    if not ComparableSet or not hasattr(ComparableSet, "companies"):
        if logger:
            logger.error("ComparableSet not available")
        return None

    # Get tickers
    tickers = [c.ticker for c in ComparableSet.companies]
    if logger:
        logger.info(f"Processing {len(tickers)} tickers")

    # Step 1: Fetch data
    dfs = fetch_financial_data(tickers)
    if not dfs:
        if logger:
            logger.error("No data fetched")
        return None

    # Step 2: Process data
    transposed_dfs = transpose_dataframes(dfs)
    formatted_dfs = convert_to_millions(transposed_dfs)

    # Step 3: Save to Excel
    excel_file = save_as_excel(formatted_dfs)

    # Step 4: AI Analysis
    analysis_result = None
    if user_prompt:
        analysis_result = ai_analysis(formatted_dfs, user_prompt)

    pipeline_results = {
        "data": formatted_dfs,
        "excel_file": excel_file,
        "ai_analysis": analysis_result,
        "success": len(formatted_dfs) > 0,
    }

    if logger:
        logger.info(f"Pipeline completed - {len(formatted_dfs)} datasets processed")
    return pipeline_results


if __name__ == "__main__":
    
    main_results = run_financial_analysis(
        user_prompt="What revenue trends can you spot across these companies?"
    )

    if main_results and main_results["success"]:
        print(f"✅ Success! Processed {len(main_results['data'])} datasets")
        if main_results["ai_analysis"]:
            print(f"AI Analysis: {main_results['ai_analysis'][:200]}...")
    else:
        print("❌ Pipeline failed")