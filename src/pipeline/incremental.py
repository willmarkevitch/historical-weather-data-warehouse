from datetime import date, datetime, timedelta


def calculate_incremental_start_date(
    requested_start_date: str,
    latest_observed_at: datetime | None,
) -> str:
    requested_start = date.fromisoformat(requested_start_date)

    if latest_observed_at is None:
        return requested_start.isoformat()

    latest_date = latest_observed_at.date()

    if latest_observed_at.hour == 23:
        incremental_start = latest_date + timedelta(days=1)
    else:
        incremental_start = latest_date

    return max(
        requested_start,
        incremental_start,
    ).isoformat()

def calculate_incremental_date_range(
    requested_start_date: str,
    requested_end_date: str,
    latest_observed_at: datetime | None,
) -> tuple[str, str] | None:
    incremental_start = calculate_incremental_start_date(
        requested_start_date=requested_start_date,
        latest_observed_at=latest_observed_at,
    )

    if incremental_start > requested_end_date:
        return None

    return incremental_start, requested_end_date
