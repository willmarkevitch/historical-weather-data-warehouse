from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

from src.pipeline.incremental_weather_etl import run_incremental_weather_etl


def test_incremental_etl_skips_when_requested_range_is_current():
    connection = MagicMock()
    client = MagicMock()
    storage = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value

    # get_location_id("los_angeles") -> 2
    # get_latest_observation_time(2) -> 2025-01-03 23:00 UTC
    cursor.fetchone.side_effect = [
        (2,),
        (
            datetime(
                2025,
                1,
                3,
                23,
                0,
                tzinfo=timezone.utc,
            ),
        ),
    ]

    result = run_incremental_weather_etl(
        location="los_angeles",
        latitude=34.0522,
        longitude=-118.2437,
        requested_start_date="2025-01-01",
        requested_end_date="2025-01-03",
        client=client,
        storage=storage,
        connection=connection,
    )

    assert result is None

    client.fetch_weather.assert_not_called()
    storage.save.assert_not_called()


def test_incremental_etl_uses_only_missing_date_range():
    connection = MagicMock()
    client = MagicMock()
    storage = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.side_effect = [
        (2,),
        (
            datetime(
                2025,
                1,
                3,
                23,
                0,
                tzinfo=timezone.utc,
            ),
        ),
    ]

    client.fetch_weather.return_value = {
        "latitude": 34.059753,
        "longitude": -118.2375,
        "hourly": {
            "time": [
                "2025-01-04T00:00",
            ],
            "temperature_2m": [15.0],
            "relative_humidity_2m": [60],
            "precipitation": [0.0],
        },
    }

    storage.save.return_value = Path(
        "data/raw/los_angeles_incremental.json"
    )

    cursor.rowcount = 1

    result = run_incremental_weather_etl(
        location="los_angeles",
        latitude=34.0522,
        longitude=-118.2437,
        requested_start_date="2025-01-01",
        requested_end_date="2025-01-05",
        client=client,
        storage=storage,
        connection=connection,
    )

    client.fetch_weather.assert_called_once_with(
        latitude=34.0522,
        longitude=-118.2437,
        start_date="2025-01-04",
        end_date="2025-01-05",
    )

    assert result.transformed_count == 1
    assert result.inserted_count == 1


def test_incremental_etl_creates_location_when_missing():
    connection = MagicMock()
    client = MagicMock()
    storage = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.side_effect = [
        None,   # get_location_id()
        (3,),   # create_location() RETURNING id
    ]

    client.fetch_weather.return_value = {
        "latitude": 40.710335,
        "longitude": -74.01101,
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [5.0],
            "relative_humidity_2m": [70],
            "precipitation": [0.0],
        },
    }

    storage.save.return_value = Path(
        "data/raw/new_york_incremental.json"
    )

    cursor.rowcount = 1

    result = run_incremental_weather_etl(
        location="new_york",
        latitude=40.7128,
        longitude=-74.0060,
        requested_start_date="2025-01-01",
        requested_end_date="2025-01-01",
        client=client,
        storage=storage,
        connection=connection,
    )

    client.fetch_weather.assert_called_once_with(
        latitude=40.7128,
        longitude=-74.0060,
        start_date="2025-01-01",
        end_date="2025-01-01",
    )

    assert result.transformed_count == 1
    assert result.inserted_count == 1

    insert_calls = [
        call
        for call in cursor.execute.call_args_list
        if "INSERT INTO weather_observations" in call.args[0]
    ]

    assert len(insert_calls) == 1
    assert insert_calls[0].args[1][-1] == 3
