import math

from src.models.weather_observation import WeatherObservation


def validate_weather_observation(
    observation: WeatherObservation,
) -> None:
    if (
        observation.timestamp.tzinfo is None
        or observation.timestamp.utcoffset() is None
    ):
        raise ValueError(
            "Timestamp must be timezone-aware"
        )

    if not -90 <= observation.latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90"
        )

    if not -180 <= observation.longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180"
        )

    if (
        observation.temperature_c is not None
        and not math.isfinite(observation.temperature_c)
    ):
        raise ValueError(
            "Temperature must be finite"
        )

    if (
        observation.relative_humidity_pct is not None
        and not 0 <= observation.relative_humidity_pct <= 100
    ):
        raise ValueError(
            "Relative humidity must be between 0 and 100"
        )

    if observation.precipitation_mm is not None:
        if (
            not math.isfinite(observation.precipitation_mm)
            or observation.precipitation_mm < 0
        ):
            raise ValueError(
                "Precipitation must be finite and non-negative"
            )