from datetime import datetime, timezone
import math

import pytest

from src.models.weather_observation import WeatherObservation
from src.validation.weather_validation import validate_weather_observation


def make_observation(**overrides):
    values = {
        "timestamp": datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        "latitude": 37.785587,
        "longitude": -122.40964,
        "temperature_c": 10.1,
        "relative_humidity_pct": 80,
        "precipitation_mm": 0.0,
    }

    values.update(overrides)

    return WeatherObservation(**values)


def test_valid_weather_observation():
    observation = make_observation()

    validate_weather_observation(observation)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("latitude", -91),
        ("latitude", 91),
        ("longitude", -181),
        ("longitude", 181),
        ("temperature_c", math.nan),
        ("temperature_c", math.inf),
        ("temperature_c", -math.inf),
        ("relative_humidity_pct", -1),
        ("relative_humidity_pct", 101),
        ("precipitation_mm", -0.1),
        ("precipitation_mm", math.nan),
        ("precipitation_mm", math.inf),
    ],
)
def test_invalid_weather_observation(field, value):
    observation = make_observation(
        **{field: value}
    )

    with pytest.raises(ValueError):
        validate_weather_observation(observation)


def test_naive_timestamp_is_rejected():
    observation = make_observation(
        timestamp=datetime(2025, 1, 1)
    )

    with pytest.raises(ValueError):
        validate_weather_observation(observation)


@pytest.mark.parametrize(
    "field",
    [
        "temperature_c",
        "relative_humidity_pct",
        "precipitation_mm",
    ],
)
def test_missing_measurement_is_allowed(field):
    observation = make_observation(
        **{field: None}
    )

    validate_weather_observation(observation)
