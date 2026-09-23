from datetime import datetime, timezone

from src.models.weather_observation import WeatherObservation
from src.validation.weather_validation import validate_weather_observation


def transform_weather_data(
    data: dict,
) -> list[WeatherObservation]:
    hourly = data["hourly"]

    observations = []

    for (
        timestamp,
        temperature,
        humidity,
        precipitation,
    ) in zip(
        hourly["time"],
        hourly["temperature_2m"],
        hourly["relative_humidity_2m"],
        hourly["precipitation"],
        strict=True,
    ):
        observation = WeatherObservation(
            timestamp=datetime.fromisoformat(
                timestamp
            ).replace(tzinfo=timezone.utc),
            latitude=data["latitude"],
            longitude=data["longitude"],
            temperature_c=temperature,
            relative_humidity_pct=humidity,
            precipitation_mm=precipitation,
        )

        validate_weather_observation(observation)

        observations.append(observation)

    return observations

def transform_ingestion_record(
    record: dict,
) -> list[WeatherObservation]:
    return transform_weather_data(record["data"])
