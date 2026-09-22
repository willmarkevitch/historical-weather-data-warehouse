from pathlib import Path

from src.ingestion.ingestion_record import create_ingestion_record
from src.ingestion.weather_client import WeatherAPIClient
from src.storage.raw_storage import RawWeatherStorage


def ingest_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    filename: str,
    client: WeatherAPIClient,
    storage: RawWeatherStorage,
) -> Path:
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

    return storage.save(
        data=record,
        filename=filename,
    )