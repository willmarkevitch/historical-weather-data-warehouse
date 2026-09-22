from datetime import datetime, timezone

from src.ingestion.ingestion_record import create_ingestion_record


def test_create_ingestion_record():
    weather_data = {
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
        }
    }

    record = create_ingestion_record(
        data=weather_data,
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-07",
    )

    metadata = record["metadata"]

    assert record["data"] == weather_data
    assert metadata["source"] == "open-meteo"
    assert metadata["latitude"] == 37.7749
    assert metadata["longitude"] == -122.4194
    assert metadata["start_date"] == "2025-01-01"
    assert metadata["end_date"] == "2025-01-07"

    ingestion_time = datetime.fromisoformat(
        metadata["ingested_at"]
    )

    assert ingestion_time.tzinfo is not None
    assert ingestion_time.utcoffset() == timezone.utc.utcoffset(None)