from datetime import datetime, timezone

import pytest

from src.models.weather_observation import WeatherObservation


def test_weather_observation_creation():
    observation = WeatherObservation(
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

    assert observation.timestamp == datetime(
        2025,
        1,
        1,
        0,
        0,
        tzinfo=timezone.utc,
    )
    assert observation.latitude == 37.785587
    assert observation.longitude == -122.40964
    assert observation.temperature_c == 10.1
    assert observation.relative_humidity_pct == 80
    assert observation.precipitation_mm == 0.0


def test_weather_observation_is_immutable():
    observation = WeatherObservation(
        timestamp=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        latitude=37.785587,
        longitude=-122.40964,
        temperature_c=10.1,
        relative_humidity_pct=80,
        precipitation_mm=0.0,
    )

    with pytest.raises(AttributeError):
        observation.temperature_c = 20.0