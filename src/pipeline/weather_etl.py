from dataclasses import dataclass
from pathlib import Path

from psycopg import Connection

from src.ingestion.ingestion_record import create_ingestion_record
from src.ingestion.weather_client import WeatherAPIClient
from src.storage.raw_storage import RawWeatherStorage
from src.storage.weather_repository import insert_weather_observations
from src.transformation.weather_transformer import transform_ingestion_record


@dataclass(frozen=True)
class WeatherETLResult:
    raw_path: Path
    transformed_count: int
    inserted_count: int

def run_weather_etl(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    filename: str,
    client: WeatherAPIClient,
    storage: RawWeatherStorage,
    connection: Connection,
) -> WeatherETLResult:
    weather_data = client.fetch_weather(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )

    record = create_ingestion_record(
        data=weather_data,
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )

    raw_path = storage.save(
        data=record,
        filename=filename,
    )

    observations = transform_ingestion_record(record)

    inserted_count = insert_weather_observations(
        connection,
        observations,
    )

    return WeatherETLResult(
        raw_path=raw_path,
        transformed_count=len(observations),
        inserted_count=inserted_count,
    )
