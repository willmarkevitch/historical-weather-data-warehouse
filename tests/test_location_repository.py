from unittest.mock import MagicMock

from src.storage.location_repository import (
    create_location,
    get_location_id,
)


def test_get_location_id():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = (2,)

    result = get_location_id(
        connection,
        name="los_angeles",
    )

    assert result == 2

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "SELECT id" in query
    assert "FROM locations" in query
    assert "WHERE name = %s" in query
    assert params == ("los_angeles",)


def test_get_location_id_returns_none_when_location_does_not_exist():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = None

    result = get_location_id(
        connection,
        name="new_york",
    )

    assert result is None


def test_create_location():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = (3,)

    result = create_location(
        connection,
        name="new_york",
        requested_latitude=40.7128,
        requested_longitude=-74.0060,
    )

    assert result == 3

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "INSERT INTO locations" in query
    assert "RETURNING id" in query
    assert params == (
        "new_york",
        40.7128,
        -74.0060,
    )
