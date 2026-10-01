from psycopg import Connection
from datetime import datetime, timezone

from src.pipeline.raw_filename import build_raw_filename
from src.pipeline.weather_etl import run_weather_etl

from src.ingestion.weather_client import WeatherAPIClient
from src.pipeline.incremental import calculate_incremental_date_range
from src.storage.location_repository import (
    create_location,
    get_location_id,
)
from src.storage.raw_storage import RawWeatherStorage
from src.storage.weather_repository import get_latest_observation_time


def run_incremental_weather_etl(
    location: str,
    latitude: float,
    longitude: float,
    requested_start_date: str,
    requested_end_date: str,
    client: WeatherAPIClient,
    storage: RawWeatherStorage,
    connection: Connection,
):
    location_id = get_location_id(
        connection,
        name=location,
    )

    if location_id is None:
        location_id = create_location(
            connection,
            name=location,
            requested_latitude=latitude,
            requested_longitude=longitude,
        )
        latest_observed_at = None
    else:
        latest_observed_at = get_latest_observation_time(
            connection,
            location_id=location_id,
        )

    date_range = calculate_incremental_date_range(
        requested_start_date=requested_start_date,
        requested_end_date=requested_end_date,
        latest_observed_at=latest_observed_at,
    )

    if date_range is None:
        return None

    incremental_start_date, incremental_end_date = date_range

    filename = build_raw_filename(
        location=location,
        start_date=incremental_start_date,
        end_date=incremental_end_date,
        ingested_at=datetime.now(timezone.utc),
    )

    return run_weather_etl(
        latitude=latitude,
        longitude=longitude,
        start_date=incremental_start_date,
        end_date=incremental_end_date,
        filename=filename,
        client=client,
        storage=storage,
        connection=connection,
        location_id=location_id,
    )
