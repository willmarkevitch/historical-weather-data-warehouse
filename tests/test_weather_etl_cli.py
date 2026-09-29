import pytest

from src.pipeline.run_weather_etl import parse_args


def test_parse_args_requires_arguments():
    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args():
    args = parse_args(
        [
            "--location",
            "san_francisco",
            "--latitude",
            "37.7749",
            "--longitude",
            "-122.4194",
            "--start-date",
            "2025-01-03",
            "--end-date",
            "2025-01-03",
        ]
    )

    assert args.location == "san_francisco"
    assert args.latitude == 37.7749
    assert args.longitude == -122.4194
    assert args.start_date == "2025-01-03"
    assert args.end_date == "2025-01-03"
