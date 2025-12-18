"""this file tests the create_financial_data function & mocks (redis_client, webhooks, API responses)"""

import pytest
from unittest.mock import patch, MagicMock
import json
import pandas as pd

from backend.ingest.fetch import create_financial_data


@pytest.fixture
def sample_financial_data():
    df_income = pd.DataFrame([{
        "income": 150000,
        "general_and_administrative": 10000,
        "r_and_d": 50000,
        "ebit": 30000,
        "taxes": 6000,
    }])
    df_income["ticker"] = "TSLA"
    df_income["statement_type"] = "income-statement"

    df_balance = pd.DataFrame([{
        "marketable_securities": 18000,
        "cash": 20000,
        "equipment": 11000,
        "brand_name": 2000,
    }])
    df_balance["ticker"] = "TSLA"
    df_balance["statement_type"] = "balance-sheet-statement"

    return [
        {"statement_type": "income-statement",
         "data": df_income.to_dict("records")},
        {"statement_type": "balance-sheet-statement",
         "data": df_balance.to_dict("records")},
    ]


def test_cache_and_webhook(sample_financial_data):
    ticker = "TSLA"

    with patch("backend.ingest.fetch.redis_client") as mock_redis, \
         patch("backend.ingest.fetch.notify_cache_expiry") as mock_webhook, \
         patch("backend.ingest.fetch.requests.get") as mock_fetch:

        # IMPORTANT: we should redis_client truthy in boolean context
        # The fetch code checks if redis_client and ticker_data:
        mock_redis.__bool__ = lambda self: True
        
        # Fake API response for ALL required statements
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        # Return data for each statement type
        mock_resp.json.return_value = [{"anything": 1000}]
        mock_fetch.return_value = mock_resp

        # Cache miss -> first call returns None (no cached data)
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        dfs = create_financial_data([ticker])
        assert dfs
        # On cache miss, webhook should be called because it's first time caching
        assert mock_webhook.called, "Webhook should be called on cache miss"
        assert mock_webhook.call_count == 1

        # Reset for next test
        mock_webhook.reset_mock()
        mock_redis.reset_mock()

        # Cache hit -> return the cached data
        mock_redis.get.return_value = json.dumps(sample_financial_data)

        dfs2 = create_financial_data([ticker])
        assert dfs2
        # On cache hit with same data, webhook should NOT be called
        assert not mock_webhook.called, "Webhook should not be called when data unchanged"

        # Verify Redis was accessed
        mock_redis.get.assert_called()
        # On cache hit, set should not be called since we return early
        # mock_redis.set.assert_not_called()


def test_webhook_called_on_data_change(sample_financial_data):
    """Test that webhook IS called when cached data changes"""
    ticker = "TSLA"
    
    # Modified data (different values, to mimick change)
    modified_data = [
        {"statement_type": "income-statement",
         "data": [{"income": 999999, "ebit": 50000, "ticker": "TSLA", "statement_type": "income-statement"}]},
        {"statement_type": "balance-sheet-statement",
         "data": [{"cash": 99999, "equipment": 88888, "ticker": "TSLA", "statement_type": "balance-sheet-statement"}]},
    ]

    with patch("backend.ingest.fetch.redis_client") as mock_redis, \
         patch("backend.ingest.fetch.notify_cache_expiry") as mock_webhook, \
         patch("backend.ingest.fetch.requests.get") as mock_fetch:

        mock_redis.__bool__ = lambda self: True
        
        # Mock API to return new data
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{"income": 999999, "ebit": 50000}]
        mock_fetch.return_value = mock_resp

        # Return old cached data
        mock_redis.get.return_value = json.dumps(sample_financial_data)
        mock_redis.set.return_value = True

        dfs = create_financial_data([ticker])
        assert dfs
        
        # Webhook should be called because data changed
        assert mock_webhook.called, "Webhook should be called when data changes"