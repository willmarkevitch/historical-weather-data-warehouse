from datetime import datetime, timezone

from src.pipeline.raw_filename import build_raw_filename
from src.ingestion.weather_client import WeatherAPIClient
from src.pipeline.weather_etl import run_weather_etl
from src.storage.database import get_connection
from src.storage.raw_storage import RawWeatherStorage


def main():
    client = WeatherAPIClient(timeout=30)
    storage = RawWeatherStorage(base_dir="data/raw")

    filename = build_raw_filename(
        location="san_francisco",
        start_date="2025-01-02",
        end_date="2025-01-02",
        ingested_at=datetime.now(timezone.utc),
    )

    with get_connection() as connection:
        result = run_weather_etl(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-02",
            end_date="2025-01-02",
            filename=filename,
            client=client,
            storage=storage,
            connection=connection,
        )

    print(f"Raw file: {result.raw_path}")
    print(f"Transformed observations: {result.transformed_count}")
    print(f"Inserted observations: {result.inserted_count}")


if __name__ == "__main__":
    main()
