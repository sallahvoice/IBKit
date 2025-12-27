"""file that test db repositories BaseRepository class behaviour"""

from unittest.mock import MagicMock, patch

import pytest

from db.repositories.base_repository import BaseRepository


@pytest.fixture
def cursor_mock():
    """Mock DB cursor behaving as a context manager."""
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = None

    cursor.lastrowid = 101
    cursor.fetchone.return_value = {"id": 1, "name": "brian"}
    cursor.fetchall.return_value = [
        {"name": "stacy"},
        {"name": "derek"},
    ]
    cursor.rowcount = 1
    return cursor


def test_create(cursor_mock):
    """Create inserts a record and returns its ID."""
    with patch(
        "db.repositories.base_repository.database.get_cursor",
        return_value=cursor_mock,
    ):
        repo = BaseRepository("users")
        new_id = repo.create({"name": "lina"})

        assert new_id == 101
        cursor_mock.execute.assert_called_once_with(
            "INSERT INTO users (name) VALUES (%s)",
            ("lina",),
        )

        with pytest.raises(ValueError, match="No data provided"):
            repo.create({})


def test_find_by_id(cursor_mock):
    """Find by ID returns the expected row."""
    with patch(
        "db.repositories.base_repository.database.get_cursor",
        return_value=cursor_mock,
    ):
        repo = BaseRepository("suppliers")
        row = repo.find_by_id(1)

        assert row == {"id": 1, "name": "brian"}
        cursor_mock.execute.assert_called_once_with(
            "SELECT * FROM suppliers WHERE id = %s",
            (1,),
        )


def test_find_all(cursor_mock):
    """Find all returns rows with a limit."""
    with patch(
        "db.repositories.base_repository.database.get_cursor",
        return_value=cursor_mock,
    ):
        repo = BaseRepository("goods")
        rows = repo.find_all(limit=2)

        assert rows == [
            {"name": "stacy"},
            {"name": "derek"},
        ]
        cursor_mock.execute.assert_called_once_with(
            "SELECT * FROM goods LIMIT %s",
            (2,),
        )


def test_update(cursor_mock):
    """Update returns True on success."""
    with patch(
        "db.repositories.base_repository.database.get_cursor",
        return_value=cursor_mock,
    ):
        repo = BaseRepository("electronics")
        success = repo.update(1, {"name": "samy"})

        assert success is True
        cursor_mock.execute.assert_called_once()


def test_delete_by_id(cursor_mock):
    """Delete by ID returns True on success."""
    with patch(
        "db.repositories.base_repository.database.get_cursor",
        return_value=cursor_mock,
    ):
        repo = BaseRepository("books")
        success = repo.delete_by_id(1)

        assert success is True
        cursor_mock.execute.assert_called_once_with(
            "DELETE FROM books WHERE id = %s",
            (1,),
        )
