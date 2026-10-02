import argparse

from src.ingestion.weather_client import WeatherAPIClient
from src.pipeline.incremental_weather_etl import run_incremental_weather_etl
from src.storage.database import get_connection
from src.storage.raw_storage import RawWeatherStorage


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the historical weather ETL pipeline."
    )

    parser.add_argument(
        "--location",
        required=True,
        help="Location name used for the weather load.",
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

    with get_connection() as connection:
        result = run_incremental_weather_etl(
            location=args.location,
            latitude=args.latitude,
            longitude=args.longitude,
            requested_start_date=args.start_date,
            requested_end_date=args.end_date,
            client=client,
            storage=storage,
            connection=connection,
        )

    if result is None:
        print("No new weather data to load.")
        return

    print(f"Raw file: {result.raw_path}")
    print(f"Transformed observations: {result.transformed_count}")
    print(f"Inserted observations: {result.inserted_count}")


if __name__ == "__main__":
    main()
