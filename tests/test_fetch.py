"""this file test the create_financial_data function & mocks (redis_client, webhooks, API responses)"""

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

        # Fake API response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{"anything": 1000}]
        mock_fetch.return_value = mock_resp

        # Cache miss
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        dfs = create_financial_data([ticker])
        assert dfs
        assert mock_webhook.called

        mock_webhook.reset_mock()

        # Cache hit
        mock_redis.get.return_value = json.dumps(sample_financial_data).encode("utf-8")

        dfs2 = create_financial_data([ticker])
        assert dfs2
        assert not mock_webhook.called

        mock_redis.get.assert_called()
        mock_redis.set.assert_called()
