from datetime import datetime, timezone


def create_ingestion_record(
    data: dict,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    return {
        "metadata": {
            "source": "open-meteo",
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        },
        "data": data,
    }