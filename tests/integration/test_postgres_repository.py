import pytest
import psycopg
from datetime import datetime, timezone

from src.models.weather_observation import WeatherObservation
from src.storage.database import get_connection
from src.storage.weather_repository import insert_weather_observation

pytestmark = pytest.mark.integration

def test_insert_weather_observation_into_postgres():
    observation = WeatherObservation(
        timestamp=datetime(2099, 1, 1, tzinfo=timezone.utc),
        latitude=10.123456,
        longitude=-20.654321,
        temperature_c=21.5,
        relative_humidity_pct=65,
        precipitation_mm=1.2,
    )

    with get_connection() as connection:
        insert_weather_observation(
            connection,
            observation,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    observed_at,
                    latitude,
                    longitude,
                    temperature_c,
                    relative_humidity_pct,
                    precipitation_mm
                FROM weather_observations
                WHERE observed_at = %s
                  AND latitude = %s
                  AND longitude = %s;
                """,
                (
                    observation.timestamp,
                    observation.latitude,
                    observation.longitude,
                ),
            )

            row = cursor.fetchone()

            assert row == (
                observation.timestamp,
                observation.latitude,
                observation.longitude,
                observation.temperature_c,
                observation.relative_humidity_pct,
                observation.precipitation_mm,
            )

            cursor.execute(
                """
                DELETE FROM weather_observations
                WHERE observed_at = %s
                  AND latitude = %s
                  AND longitude = %s;
                """,
                (
                    observation.timestamp,
                    observation.latitude,
                    observation.longitude,
                ),
            )


def test_duplicate_weather_observation_is_not_inserted():
    observation = WeatherObservation(
        timestamp=datetime(2099, 1, 2, tzinfo=timezone.utc),
        latitude=10.123456,
        longitude=-20.654321,
        temperature_c=20.0,
        relative_humidity_pct=70,
        precipitation_mm=0.0,
    )

    with get_connection() as connection:
        first_result = insert_weather_observation(
            connection,
            observation,
        )

        second_result = insert_weather_observation(
            connection,
            observation,
        )

        assert first_result == 1
        assert second_result == 0

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM weather_observations
                WHERE observed_at = %s
                  AND latitude = %s
                  AND longitude = %s;
                """,
                (
                    observation.timestamp,
                    observation.latitude,
                    observation.longitude,
                ),
            )

            count = cursor.fetchone()[0]

            assert count == 1

            cursor.execute(
                """
                DELETE FROM weather_observations
                WHERE observed_at = %s
                  AND latitude = %s
                  AND longitude = %s;
                """,
                (
                    observation.timestamp,
                    observation.latitude,
                    observation.longitude,
                ),
            )


def test_postgres_rejects_invalid_humidity():
    with get_connection() as connection:
        with pytest.raises(psycopg.errors.CheckViolation):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        relative_humidity_pct,
                        precipitation_mm
                    )
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        datetime(2099, 1, 3, tzinfo=timezone.utc),
                        10.123456,
                        -20.654321,
                        20.0,
                        101,
                        0.0,
                    ),
                )
