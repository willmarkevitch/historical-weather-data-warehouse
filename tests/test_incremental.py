from datetime import datetime, timezone

from src.pipeline.incremental import (
    calculate_incremental_start_date,
    calculate_incremental_date_range,
)


def test_incremental_start_date_uses_requested_start_when_no_data():
    result = calculate_incremental_start_date(
        requested_start_date="2025-01-01",
        latest_observed_at=None,
    )

    assert result == "2025-01-01"


def test_incremental_start_date_moves_to_next_day_when_latest_day_is_complete():
    latest_observed_at = datetime(
        2025,
        1,
        3,
        23,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_incremental_start_date(
        requested_start_date="2025-01-01",
        latest_observed_at=latest_observed_at,
    )

    assert result == "2025-01-04"


def test_incremental_start_date_reloads_partial_day():
    latest_observed_at = datetime(
        2025,
        1,
        3,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_incremental_start_date(
        requested_start_date="2025-01-01",
        latest_observed_at=latest_observed_at,
    )

    assert result == "2025-01-03"


def test_incremental_start_date_never_precedes_requested_start():
    latest_observed_at = datetime(
        2025,
        1,
        3,
        23,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_incremental_start_date(
        requested_start_date="2025-06-01",
        latest_observed_at=latest_observed_at,
    )

    assert result == "2025-06-01"


def test_incremental_date_range_returns_none_when_data_is_current():
    latest_observed_at = datetime(
        2025,
        1,
        3,
        23,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_incremental_date_range(
        requested_start_date="2025-01-01",
        requested_end_date="2025-01-03",
        latest_observed_at=latest_observed_at,
    )

    assert result is None


def test_incremental_date_range_returns_missing_range():
    latest_observed_at = datetime(
        2025,
        1,
        3,
        23,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_incremental_date_range(
        requested_start_date="2025-01-01",
        requested_end_date="2025-01-10",
        latest_observed_at=latest_observed_at,
    )

    assert result == (
        "2025-01-04",
        "2025-01-10",
    )


def test_incremental_date_range_reloads_partial_day():
    latest_observed_at = datetime(
        2025,
        1,
        3,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_incremental_date_range(
        requested_start_date="2025-01-01",
        requested_end_date="2025-01-05",
        latest_observed_at=latest_observed_at,
    )

    assert result == (
        "2025-01-03",
        "2025-01-05",
    )
