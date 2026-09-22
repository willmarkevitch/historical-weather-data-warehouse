import json
from unittest.mock import Mock

import pytest

from src.ingestion.pipeline import ingest_weather
from src.storage.raw_storage import RawWeatherStorage


def test_ingest_weather_saves_api_response(tmp_path):
    weather_data = {
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
            "relative_humidity_2m": [75],
            "precipitation": [0.0],
        }
    }

    mock_client = Mock()
    mock_client.fetch_weather.return_value = weather_data

    storage = RawWeatherStorage(base_dir=tmp_path)

    file_path = ingest_weather(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-07",
        filename="weather.json",
        client=mock_client,
        storage=storage,
    )

    mock_client.fetch_weather.assert_called_once_with(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-07",
    )

    assert file_path.exists()

    with file_path.open("r", encoding="utf-8") as file:
        saved_record = json.load(file)

    assert saved_record["data"] == weather_data
    assert saved_record["metadata"]["source"] == "open-meteo"
    assert saved_record["metadata"]["latitude"] == 37.7749
    assert saved_record["metadata"]["longitude"] == -122.4194
    assert saved_record["metadata"]["start_date"] == "2025-01-01"
    assert saved_record["metadata"]["end_date"] == "2025-01-07"
    assert "ingested_at" in saved_record["metadata"]


def test_ingest_weather_does_not_save_when_api_fails(tmp_path):
    mock_client = Mock()
    mock_client.fetch_weather.side_effect = ConnectionError(
        "Simulated API failure"
    )

    storage = RawWeatherStorage(base_dir=tmp_path)

    with pytest.raises(ConnectionError, match="Simulated API failure"):
        ingest_weather(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-01",
            end_date="2025-01-07",
            filename="weather.json",
            client=mock_client,
            storage=storage,
        )

    mock_client.fetch_weather.assert_called_once()
    assert list(tmp_path.iterdir()) == []


def test_ingest_weather_does_not_overwrite_existing_file(tmp_path):
    mock_client = Mock()
    mock_client.fetch_weather.return_value = {
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
            "relative_humidity_2m": [75],
            "precipitation": [0.0],
        }
    }

    storage = RawWeatherStorage(base_dir=tmp_path)

    arguments = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "start_date": "2025-01-01",
        "end_date": "2025-01-07",
        "filename": "weather.json",
        "client": mock_client,
        "storage": storage,
    }

    file_path = ingest_weather(**arguments)
    original_contents = file_path.read_text(encoding="utf-8")

    with pytest.raises(FileExistsError):
        ingest_weather(**arguments)

    assert file_path.read_text(encoding="utf-8") == original_contents
    assert len(list(tmp_path.iterdir())) == 1
    assert mock_client.fetch_weather.call_count == 2
