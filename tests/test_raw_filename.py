import pytest
from datetime import datetime, timezone

from src.pipeline.raw_filename import build_raw_filename


def test_build_raw_filename():
    ingested_at = datetime(
        2026, 9, 25, 6, 32, 15, tzinfo=timezone.utc
    )

    filename = build_raw_filename(
        location="san_francisco",
        start_date="2025-01-02",
        end_date="2025-01-02",
        ingested_at=ingested_at,
    )

    assert filename == (
        "san_francisco_2025-01-02_20260925T063215Z.json"
    )


def test_build_raw_filename_rejects_naive_timestamp():
    ingested_at = datetime(2026, 9, 25, 6, 32, 15)

    with pytest.raises(
        ValueError,
        match="ingested_at must be timezone-aware",
    ):
        build_raw_filename(
            location="san_francisco",
            start_date="2025-01-02",
            end_date="2025-01-02",
            ingested_at=ingested_at,
        )


def test_build_raw_filename_converts_timestamp_to_utc():
    ingested_at = datetime.fromisoformat(
        "2026-09-24T23:32:15-07:00"
    )

    filename = build_raw_filename(
        location="san_francisco",
        start_date="2025-01-02",
        end_date="2025-01-02",
        ingested_at=ingested_at,
    )

    assert filename == (
        "san_francisco_2025-01-02_20260925T063215Z.json"
    )
