from psycopg import Connection
from datetime import datetime

from src.models.weather_observation import WeatherObservation


INSERT_WEATHER_OBSERVATION = """
    INSERT INTO weather_observations (
        observed_at,
        latitude,
        longitude,
        temperature_c,
        relative_humidity_pct,
        precipitation_mm
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (
        observed_at,
        latitude,
        longitude
    )
    DO NOTHING;
"""


def _observation_to_params(
    observation: WeatherObservation,
) -> tuple:
    return (
        observation.timestamp,
        observation.latitude,
        observation.longitude,
        observation.temperature_c,
        observation.relative_humidity_pct,
        observation.precipitation_mm,
    )


def insert_weather_observation(
    connection: Connection,
    observation: WeatherObservation,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            INSERT_WEATHER_OBSERVATION,
            _observation_to_params(observation),
        )

        return cursor.rowcount


def insert_weather_observations(
    connection: Connection,
    observations: list[WeatherObservation],
) -> int:
    if not observations:
        return 0

    inserted_count = 0

    with connection.cursor() as cursor:
        for observation in observations:
            cursor.execute(
                INSERT_WEATHER_OBSERVATION,
                _observation_to_params(observation),
            )

            inserted_count += cursor.rowcount

    return inserted_count

def get_latest_observation_time(
    connection: Connection,
    location_id: int,
) -> datetime | None:
    query = """
        SELECT MAX(observed_at)
        FROM weather_observations
        WHERE location_id = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (location_id,),
        )
        row = cursor.fetchone()

    return row[0]
