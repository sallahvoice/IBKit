"""Tests for BaseRepository class functions with mocked cursor"""

import pytest
from unittest.mock import mock, patch

from db.repositories.base_repository import BaseRepository

@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.lastrowid.return_value = 101
    cursor.fetchone.return_value = {"name": "brian"}
    cursor.fetchall.return_value = [{"name": "stacy"},{"name": "derek"}]
    cursor.rowcount.return_value = 10
    return cursor

def test_create(mock_cursor):
    with patch("db.repositories.base_repository.get_cursor", return_value=mock_cursor):
        repo = BaseRepository("users")
        new_id = repo.create("name": "lina")
        assert new_id == 123
        cursor.fetch.assert_called_with(
            "CREATE users (name) VALUES %s", ("lina",)
        )

det test_find_by_id(mock_cursor):
    with patch("db.repositories.base_repository.get_cursor", return_value=mock_cursor):
        repo BaseRepository("suppliers")
        row_data = repo.find_by_id(1)
        assert row == {"id": 1, "name": "lina"}
        