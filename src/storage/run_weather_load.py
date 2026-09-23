import json
from pathlib import Path

from src.storage.database import get_connection
from src.storage.weather_repository import insert_weather_observations
from src.transformation.weather_transformer import transform_ingestion_record


RAW_FILE = Path("data/raw/san_francisco_2025-01-01.json")


def main():
    with RAW_FILE.open("r", encoding="utf-8") as file:
        record = json.load(file)

    observations = transform_ingestion_record(record)

    with get_connection() as connection:
        inserted_count = insert_weather_observations(
            connection,
            observations,
        )

    print(f"Transformed observations: {len(observations)}")
    print(f"Inserted observations: {inserted_count}")


if __name__ == "__main__":
    main()