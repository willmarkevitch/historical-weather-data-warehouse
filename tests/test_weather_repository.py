from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.storage.weather_repository import get_latest_observation_time
from src.models.weather_observation import WeatherObservation
from src.storage.weather_repository import (
    insert_weather_observation,
    insert_weather_observations,
)


def create_observation() -> WeatherObservation:
    return WeatherObservation(
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        latitude=37.785587,
        longitude=-122.40964,
        temperature_c=10.1,
        relative_humidity_pct=80,
        precipitation_mm=0.0,
    )


def test_insert_weather_observation():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1

    observation = create_observation()

    result = insert_weather_observation(
        connection,
        observation,
    )

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "INSERT INTO weather_observations" in query
    assert params == (
        observation.timestamp,
        observation.latitude,
        observation.longitude,
        observation.temperature_c,
        observation.relative_humidity_pct,
        observation.precipitation_mm,
    )
    assert result == 1


def test_insert_weather_observation_with_missing_measurements():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1

    observation = WeatherObservation(
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        latitude=37.785587,
        longitude=-122.40964,
        temperature_c=None,
        relative_humidity_pct=None,
        precipitation_mm=None,
    )

    insert_weather_observation(connection, observation)

    _, params = cursor.execute.call_args.args

    assert params == (
        observation.timestamp,
        observation.latitude,
        observation.longitude,
        None,
        None,
        None,
    )


def test_insert_weather_observation_duplicate_returns_zero():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.rowcount = 0

    result = insert_weather_observation(
        connection,
        create_observation(),
    )

    assert result == 0


def test_insert_weather_observations():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1

    observations = [
        create_observation(),
        WeatherObservation(
            timestamp=datetime(2025, 1, 1, 1, tzinfo=timezone.utc),
            latitude=37.785587,
            longitude=-122.40964,
            temperature_c=9.8,
            relative_humidity_pct=82,
            precipitation_mm=0.0,
        ),
    ]

    result = insert_weather_observations(
        connection,
        observations,
    )

    assert cursor.execute.call_count == 2
    assert result == 2


def test_insert_weather_observations_empty_list():
    connection = MagicMock()

    result = insert_weather_observations(
        connection,
        [],
    )

    connection.cursor.assert_not_called()
    assert result == 0


def test_insert_weather_observations_counts_only_inserted_rows():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    observations = [
        create_observation(),
        WeatherObservation(
            timestamp=datetime(2025, 1, 1, 1, tzinfo=timezone.utc),
            latitude=37.785587,
            longitude=-122.40964,
            temperature_c=9.8,
            relative_humidity_pct=82,
            precipitation_mm=0.0,
        ),
    ]

    cursor.rowcount = 1

    original_execute = cursor.execute

    def execute_with_rowcounts(*args, **kwargs):
        if cursor.execute.call_count == 1:
            cursor.rowcount = 1
        else:
            cursor.rowcount = 0

    cursor.execute.side_effect = execute_with_rowcounts

    result = insert_weather_observations(
        connection,
        observations,
    )

    assert cursor.execute.call_count == 2
    assert result == 1


def test_get_latest_observation_time():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    latest_time = datetime(
        2025,
        1,
        3,
        23,
        0,
        tzinfo=timezone.utc,
    )

    cursor.fetchone.return_value = (latest_time,)

    result = get_latest_observation_time(
        connection,
        location_id=2,
    )

    assert result == latest_time

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "MAX(observed_at)" in query
    assert "WHERE location_id = %s" in query
    assert params == (2,)


def test_get_latest_observation_time_returns_none_when_no_data():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = (None,)

    result = get_latest_observation_time(
        connection,
        location_id=3,
    )

    assert result is None
