# pylint: disable=redefined-outer-name
"""Tests for create_financial_data function with mocked redis_client, webhooks, and API responses"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from backend.ingest import fetch
from backend.ingest.fetch import REQUIRED_STATEMENTS


def sample_financial_data():
    """fake api data, 3 required statements"""
    df_income = pd.DataFrame(
        [
            {
                "income": 150000,
                "general_and_administrative": 10000,
                "r_and_d": 50000,
                "ebit": 30000,
                "taxes": 6000,
            }
        ]
    )
    df_income["ticker"] = "TSLA"
    df_income["statement_type"] = "income-statement"

    df_balance = pd.DataFrame(
        [
            {
                "marketable_securities": 18000,
                "cash": 20000,
                "equipment": 11000,
                "brand_name": 2000,
            }
        ]
    )
    df_balance["ticker"] = "TSLA"
    df_balance["statement_type"] = "balance-sheet-statement"

    df_cashflow = pd.DataFrame(
        [
            {
                "operating_cash_flow": 50000,
                "capital_expenditure": 20000,
                "free_cash_flow": 30000,
            }
        ]
    )
    df_cashflow["ticker"] = "TSLA"
    df_cashflow["statement_type"] = "cash-flow-statement"

    return [
        {"statement_type": "income-statement", "data": df_income.to_dict("records")},
        {
            "statement_type": "balance-sheet-statement",
            "data": df_balance.to_dict("records"),
        },
        {
            "statement_type": "cash-flow-statement",
            "data": df_cashflow.to_dict("records"),
        },
    ]


@pytest.fixture
def financial_data_factory():
    return sample_financial_data


def test_cache_and_webhook(financial_data_factory):
    """Test that webhook is called on cache miss but not on cache hit"""
    ticker = "TSLA"
    cached_data = financial_data_factory()

    with (
        patch.object(fetch, "redis_client") as mock_redis,
        patch.object(fetch, "notify_cache_expiry") as mock_webhook,
        patch.object(fetch, "requests") as mock_requests,
    ):

        mock_redis.__bool__ = lambda self: True

        # Mock API responses for all 3 required statements
        mock_responses = []
        for stmt in REQUIRED_STATEMENTS:
            resp = MagicMock()
            resp.status_code = 200
            if "income" in stmt:
                resp.json.return_value = [{"income": 150000, "ebit": 30000}]
            elif "balance" in stmt:
                resp.json.return_value = [{"cash": 20000, "equipment": 11000}]
            elif "cash" in stmt:
                resp.json.return_value = [{"operating_cash_flow": 50000}]
            mock_responses.append(resp)

        mock_requests.get.side_effect = mock_responses
        mock_requests.RequestException = Exception

        # CACHE MISS TEST
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        result = fetch.create_financial_data([ticker])

        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) == 3, f"Should return 3 DataFrames, got {len(result)}"
        assert mock_redis.set.called, "Redis set should be called"
        assert mock_webhook.called, "Webhook should be called on cache miss"

        # Reset for cache hit test
        mock_webhook.reset_mock()
        mock_redis.reset_mock()
        mock_requests.reset_mock()

        # CACHE HIT TEST
        mock_redis.get.return_value = json.dumps(cached_data)

        dfs2 = fetch.create_financial_data([ticker])

        assert isinstance(dfs2, list), f"Expected list, got {type(dfs2)}"
        assert len(dfs2) == 3, "Should return 3 cached DataFrames"
        assert not mock_webhook.called, "Webhook should not be called on cache hit"
        assert not mock_redis.set.called, "Redis set should NOT be called on cache hit"


def test_webhook_called_on_data_change(financial_data_factory):
    """Test that webhook IS called when fetched data differs from cached data"""
    ticker = "TSLA"
    cached_data = financial_data_factory()

    with (
        patch.object(fetch, "redis_client") as mock_redis,
        patch.object(fetch, "notify_cache_expiry") as mock_webhook,
        patch.object(fetch, "requests") as mock_requests,
    ):

        mock_redis.__bool__ = lambda self: True

        # Mock API to return DIFFERENT data
        mock_responses = []
        for stmt in REQUIRED_STATEMENTS:
            resp = MagicMock()
            resp.status_code = 200
            if "income" in stmt:
                resp.json.return_value = [{"income": 999999, "ebit": 88888}]
            elif "balance" in stmt:
                resp.json.return_value = [{"cash": 777777, "equipment": 66666}]
            elif "cash" in stmt:
                resp.json.return_value = [{"operating_cash_flow": 555555}]
            mock_responses.append(resp)

        mock_requests.get.side_effect = mock_responses
        mock_requests.RequestException = Exception

        # First get: None (cache miss), second get: old data
        mock_redis.get.side_effect = [
            None,
            json.dumps(cached_data),
        ]
        mock_redis.set.return_value = True

        dfs = fetch.create_financial_data([ticker])

        assert isinstance(dfs, list), f"Expected list, got {type(dfs)}"
        assert len(dfs) == 3, "Should return 3 DataFrames"
        assert mock_webhook.called, "Webhook should be called when data changes"


def test_no_webhook_when_data_unchanged():
    """Test that webhook is NOT called when fetched data matches cached data"""
    ticker = "TSLA"

    # Same data for both API and cache
    same_data = [
        {
            "statement_type": "income-statement",
            "data": [
                {
                    "income": 150000,
                    "ebit": 30000,
                    "ticker": "TSLA",
                    "statement_type": "income-statement",
                }
            ],
        },
        {
            "statement_type": "balance-sheet-statement",
            "data": [
                {
                    "cash": 20000,
                    "equipment": 11000,
                    "ticker": "TSLA",
                    "statement_type": "balance-sheet-statement",
                }
            ],
        },
        {
            "statement_type": "cash-flow-statement",
            "data": [
                {
                    "operating_cash_flow": 50000,
                    "ticker": "TSLA",
                    "statement_type": "cash-flow-statement",
                }
            ],
        },
    ]

    with (
        patch.object(fetch, "redis_client") as mock_redis,
        patch.object(fetch, "notify_cache_expiry") as mock_webhook,
        patch.object(fetch, "requests") as mock_requests,
    ):

        mock_redis.__bool__ = lambda self: True

        # Mock API to return SAME data as cached
        mock_responses = []
        for stmt in REQUIRED_STATEMENTS:
            resp = MagicMock()
            resp.status_code = 200
            if "income" in stmt:
                resp.json.return_value = [{"income": 150000, "ebit": 30000}]
            elif "balance" in stmt:
                resp.json.return_value = [{"cash": 20000, "equipment": 11000}]
            elif "cash" in stmt:
                resp.json.return_value = [{"operating_cash_flow": 50000}]
            mock_responses.append(resp)

        mock_requests.get.side_effect = mock_responses
        mock_requests.RequestException = Exception

        # First get: None (cache miss), second get: same data
        mock_redis.get.side_effect = [
            None,
            json.dumps(same_data),
        ]
        mock_redis.set.return_value = True

        dfs = fetch.create_financial_data([ticker])

        assert isinstance(dfs, list), f"Expected list, got {type(dfs)}"
        assert mock_redis.set.called, "Redis set should be called"
        assert (
            not mock_webhook.called
        ), "Webhook should NOT be called when data unchanged"


def test_convert_to_dollars_converts_all_numeric_columns():
    """Non-USD numeric values should be converted to USD using the API ratio."""
    df = pd.DataFrame([{"revenue": 10.0, "expense": 2.5, "name": "A"}])
    df.attrs["currency"] = "EUR"

    with patch.object(fetch, "requests") as mock_requests:
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": 1.2}
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        converted = fetch.convert_to_dollars([df])

    assert converted[0].attrs["currency"] == "USD"
    assert converted[0]["revenue"].iloc[0] == pytest.approx(12.0)
    assert converted[0]["expense"].iloc[0] == pytest.approx(3.0)


def test_convert_to_dollars_skips_usd_data():
    """USD data should return unchanged and should not call conversion API."""
    df = pd.DataFrame([{"revenue": 10.0}])
    df.attrs["currency"] = "USD"

    with patch.object(fetch, "requests") as mock_requests:
        converted = fetch.convert_to_dollars([df])

    mock_requests.get.assert_not_called()
    assert converted[0].equals(df)
