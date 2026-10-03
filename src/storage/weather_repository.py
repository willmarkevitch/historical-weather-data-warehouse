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
        precipitation_mm,
        location_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (
        location_id,
        observed_at
    )
    DO NOTHING;
"""


def _observation_to_params(
    observation: WeatherObservation,
    location_id: int,
) -> tuple:
    return (
        observation.timestamp,
        observation.latitude,
        observation.longitude,
        observation.temperature_c,
        observation.relative_humidity_pct,
        observation.precipitation_mm,
        location_id,
    )


def insert_weather_observation(
    connection: Connection,
    observation: WeatherObservation,
    location_id: int,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            INSERT_WEATHER_OBSERVATION,
            _observation_to_params(
                observation,
                location_id,
            ),
        )
        return cursor.rowcount


def insert_weather_observations(
    connection: Connection,
    observations: list[WeatherObservation],
    location_id: int,
) -> int:
    if not observations:
        return 0

    inserted_count = 0

    with connection.cursor() as cursor:
        for observation in observations:
            cursor.execute(
                INSERT_WEATHER_OBSERVATION,
                _observation_to_params(
                    observation,
                    location_id,
                ),
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
