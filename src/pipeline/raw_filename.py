from datetime import datetime, timezone


def build_raw_filename(
    location: str,
    start_date: str,
    end_date: str,
    ingested_at: datetime,
) -> str:
    if (
        ingested_at.tzinfo is None
        or ingested_at.utcoffset() is None
    ):
        raise ValueError("ingested_at must be timezone-aware")

    utc_timestamp = ingested_at.astimezone(timezone.utc)
    timestamp = utc_timestamp.strftime("%Y%m%dT%H%M%SZ")

    if start_date == end_date:
        date_part = start_date
    else:
        date_part = f"{start_date}_{end_date}"

    return f"{location}_{date_part}_{timestamp}.json"
