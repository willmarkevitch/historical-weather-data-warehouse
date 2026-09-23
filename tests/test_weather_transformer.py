import pytest

from datetime import datetime, timezone

from src.models.weather_observation import WeatherObservation
from src.transformation.weather_transformer import (
    transform_ingestion_record,
    transform_weather_data,
)


def test_transform_weather_data():
    data = {
        "latitude": 37.785587,
        "longitude": -122.40964,
        "hourly": {
            "time": [
                "2025-01-01T00:00",
                "2025-01-01T01:00",
            ],
            "temperature_2m": [
                10.1,
                11.0,
            ],
            "relative_humidity_2m": [
                80,
                71,
            ],
            "precipitation": [
                0.0,
                0.2,
            ],
        },
    }

    observations = transform_weather_data(data)

    assert len(observations) == 2

    assert observations[0] == WeatherObservation(
        timestamp=datetime(
            2025,
            1,
            1,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        latitude=37.785587,
        longitude=-122.40964,
        temperature_c=10.1,
        relative_humidity_pct=80,
        precipitation_mm=0.0,
    )

    assert observations[1] == WeatherObservation(
        timestamp=datetime(
            2025,
            1,
            1,
            1,
            0,
            tzinfo=timezone.utc,
        ),
        latitude=37.785587,
        longitude=-122.40964,
        temperature_c=11.0,
        relative_humidity_pct=71,
        precipitation_mm=0.2,
    )


def test_transform_preserves_missing_measurements():
    data = {
        "latitude": 37.785587,
        "longitude": -122.40964,
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [None],
            "relative_humidity_2m": [80],
            "precipitation": [None],
        },
    }

    observations = transform_weather_data(data)

    assert len(observations) == 1
    assert observations[0].temperature_c is None
    assert observations[0].relative_humidity_pct == 80
    assert observations[0].precipitation_mm is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("temperature_2m", float("nan")),
        ("relative_humidity_2m", 101),
        ("precipitation", -0.1),
    ],
)
def test_transform_rejects_invalid_measurements(field, value):
    data = {
        "latitude": 37.785587,
        "longitude": -122.40964,
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [10.1],
            "relative_humidity_2m": [80],
            "precipitation": [0.0],
        },
    }

    data["hourly"][field] = [value]

    with pytest.raises(ValueError):
        transform_weather_data(data)


def test_transform_rejects_mismatched_array_lengths():
    data = {
        "latitude": 37.785587,
        "longitude": -122.40964,
        "hourly": {
            "time": [
                "2025-01-01T00:00",
                "2025-01-01T01:00",
            ],
            "temperature_2m": [10.1],
            "relative_humidity_2m": [80, 81],
            "precipitation": [0.0, 0.0],
        },
    }

    with pytest.raises(ValueError):
        transform_weather_data(data)


def test_transform_rejects_invalid_timestamp():
    data = {
        "latitude": 37.785587,
        "longitude": -122.40964,
        "hourly": {
            "time": ["not-a-timestamp"],
            "temperature_2m": [10.1],
            "relative_humidity_2m": [80],
            "precipitation": [0.0],
        },
    }

    with pytest.raises(ValueError):
        transform_weather_data(data)


def test_transform_ingestion_record():
    record = {
        "metadata": {
            "source": "open-meteo",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "start_date": "2025-01-01",
            "end_date": "2025-01-01",
            "ingested_at": "2026-09-22T05:12:10+00:00",
        },
        "data": {
            "latitude": 37.785587,
            "longitude": -122.40964,
            "hourly": {
                "time": [
                    "2025-01-01T00:00",
                    "2025-01-01T01:00",
                ],
                "temperature_2m": [
                    10.1,
                    11.0,
                ],
                "relative_humidity_2m": [
                    80,
                    71,
                ],
                "precipitation": [
                    0.0,
                    0.2,
                ],
            },
        },
    }

    observations = transform_ingestion_record(record)

    assert len(observations) == 2

    assert observations[0].latitude == 37.785587
    assert observations[0].longitude == -122.40964
    assert observations[0].temperature_c == 10.1

    assert observations[1].temperature_c == 11.0
    assert observations[1].relative_humidity_pct == 71
    assert observations[1].precipitation_mm == 0.2
