from src.ingestion.pipeline import ingest_weather
from src.ingestion.weather_client import WeatherAPIClient
from src.storage.raw_storage import RawWeatherStorage


def main() -> None:
    client = WeatherAPIClient(timeout=30)
    storage = RawWeatherStorage(base_dir="data/raw")

    file_path = ingest_weather(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-01",
        filename="san_francisco_2025-01-01.json",
        client=client,
        storage=storage,
    )

    print(f"Weather data saved to: {file_path}")


if __name__ == "__main__":
    main()