import pytest

from pathlib import Path
from unittest.mock import MagicMock

from src.pipeline.weather_etl import run_weather_etl


def test_run_weather_etl():
    client = MagicMock()
    storage = MagicMock()
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1

    weather_data = {
        "latitude": 37.785587,
        "longitude": -122.40964,
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [10.1],
            "relative_humidity_2m": [80],
            "precipitation": [0.0],
        },
    }

    client.fetch_weather.return_value = weather_data
    storage.save.return_value = Path(
        "data/raw/san_francisco_2025-01-01.json"
    )

    result = run_weather_etl(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-01",
        filename="san_francisco_2025-01-01.json",
        client=client,
        storage=storage,
        connection=connection,
        location_id=2,
    )

    assert result.raw_path == Path(
        "data/raw/san_francisco_2025-01-01.json"
    )
    assert result.transformed_count == 1
    assert result.inserted_count == 1

    client.fetch_weather.assert_called_once_with(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-01",
    )

    storage.save.assert_called_once()

    saved_record = storage.save.call_args.kwargs["data"]

    assert saved_record["data"] == weather_data
    assert saved_record["metadata"]["source"] == "open-meteo"
    assert saved_record["metadata"]["latitude"] == 37.7749
    assert saved_record["metadata"]["longitude"] == -122.4194
    assert saved_record["metadata"]["start_date"] == "2025-01-01"
    assert saved_record["metadata"]["end_date"] == "2025-01-01"

    assert storage.save.call_args.kwargs["filename"] == (
        "san_francisco_2025-01-01.json"
    )

    _, params = cursor.execute.call_args.args

    assert params[-1] == 2


def test_run_weather_etl_stops_when_extraction_fails():
    client = MagicMock()
    storage = MagicMock()
    connection = MagicMock()

    client.fetch_weather.side_effect = RuntimeError("API unavailable")

    with pytest.raises(RuntimeError, match="API unavailable"):
        run_weather_etl(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-01",
            end_date="2025-01-01",
            filename="san_francisco_2025-01-01.json",
            client=client,
            storage=storage,
            connection=connection,
            location_id=1,
        )

    storage.save.assert_not_called()
    connection.cursor.assert_not_called()
