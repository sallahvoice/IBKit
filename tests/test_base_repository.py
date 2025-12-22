import pytest
from unittest.mock import MagicMock, patch

from db.repositories.base_repository import BaseRepository


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor #cursor is a used in BaseRepository as a context manager
    cursor.__exit__.return_value = None

    cursor.lastrowid = 101
    cursor.fetchone.return_value = {"id": 1, "name": "brian"}
    cursor.fetchall.return_value = [
        {"name": "stacy"},
        {"name": "derek"},
    ]
    cursor.rowcount = 1
    return cursor


def test_create(mock_cursor):
    with patch("db.repositories.base_repository.database.get_cursor",return_value=mock_cursor):
        repo = BaseRepository("users")
        new_id = repo.create({"name": "lina"})

        assert new_id == 101
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (name) VALUES (%s)", ("lina",),
        )
        with pytest.raises(ValueError, match="No data provided"):
            repo.create({})


def test_find_by_id(mock_cursor):
    with patch("db.repositories.base_repository.database.get_cursor",return_value=mock_cursor):
        repo = BaseRepository("suppliers")
        row = repo.find_by_id(1)

        assert row == {"id": 1, "name": "brian"}
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM suppliers WHERE id = %s", (1,),
        )


def test_find_all(mock_cursor):
    with patch("db.repositories.base_repository.database.get_cursor",return_value=mock_cursor):
        repo = BaseRepository("goods")
        rows = repo.find_all(limit=2)

        assert rows == [
            {"name": "stacy"},
            {"name": "derek"},
        ]
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM goods LIMIT %s",
            (2,),
        )


def test_update(mock_cursor):
    with patch("db.repositories.base_repository.database.get_cursor",return_value=mock_cursor):
        repo = BaseRepository("electronics")
        success = repo.update(1, {"name": "samy"})

        assert success is True
        mock_cursor.execute.assert_called_once()


def test_delete_by_id(mock_cursor):
    with patch("db.repositories.base_repository.database.get_cursor",return_value=mock_cursor):
        repo = BaseRepository("books")
        success = repo.delete_by_id(1)

        assert success is True
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM books WHERE id = %s", (1,),
        )
