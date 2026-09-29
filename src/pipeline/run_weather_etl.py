import argparse
from datetime import datetime, timezone

from src.pipeline.raw_filename import build_raw_filename
from src.ingestion.weather_client import WeatherAPIClient
from src.pipeline.weather_etl import run_weather_etl
from src.storage.database import get_connection
from src.storage.raw_storage import RawWeatherStorage


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the historical weather ETL pipeline."
    )

    parser.add_argument(
        "--location",
        required=True,
        help="Location name used for the raw snapshot filename.",
    )

    parser.add_argument(
        "--latitude",
        type=float,
        required=True,
        help="Latitude of the weather location.",
    )

    parser.add_argument(
        "--longitude",
        type=float,
        required=True,
        help="Longitude of the weather location.",
    )

    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--end-date",
        required=True,
        help="End date in YYYY-MM-DD format.",
    )

    return parser.parse_args(argv)

def main():
    args = parse_args()

    client = WeatherAPIClient(timeout=30)
    storage = RawWeatherStorage(base_dir="data/raw")

    filename = build_raw_filename(
        location=args.location,
        start_date=args.start_date,
        end_date=args.end_date,
        ingested_at=datetime.now(timezone.utc),
    )

    with get_connection() as connection:
        result = run_weather_etl(
            latitude=args.latitude,
            longitude=args.longitude,
            start_date=args.start_date,
            end_date=args.end_date,
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
