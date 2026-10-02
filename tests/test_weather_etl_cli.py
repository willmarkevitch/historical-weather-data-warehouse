import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.pipeline.run_weather_etl import main, parse_args
from src.pipeline.weather_etl import WeatherETLResult


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


@patch("src.pipeline.run_weather_etl.run_incremental_weather_etl")
@patch("src.pipeline.run_weather_etl.get_connection")
@patch("src.pipeline.run_weather_etl.parse_args")
def test_main_runs_incremental_etl(
    mock_parse_args,
    mock_get_connection,
    mock_run_incremental_weather_etl,
    capsys,
):
    mock_parse_args.return_value = MagicMock(
        location="los_angeles",
        latitude=34.0522,
        longitude=-118.2437,
        start_date="2025-01-01",
        end_date="2025-01-05",
    )

    connection = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = connection

    mock_run_incremental_weather_etl.return_value = WeatherETLResult(
        raw_path=Path("data/raw/los_angeles_incremental.json"),
        transformed_count=48,
        inserted_count=48,
    )

    main()

    mock_run_incremental_weather_etl.assert_called_once()

    call_kwargs = mock_run_incremental_weather_etl.call_args.kwargs

    assert call_kwargs["location"] == "los_angeles"
    assert call_kwargs["latitude"] == 34.0522
    assert call_kwargs["longitude"] == -118.2437
    assert call_kwargs["requested_start_date"] == "2025-01-01"
    assert call_kwargs["requested_end_date"] == "2025-01-05"
    assert call_kwargs["connection"] is connection

    output = capsys.readouterr().out

    assert "Raw file: data" in output
    assert "Transformed observations: 48" in output
    assert "Inserted observations: 48" in output


@patch("src.pipeline.run_weather_etl.run_incremental_weather_etl")
@patch("src.pipeline.run_weather_etl.get_connection")
@patch("src.pipeline.run_weather_etl.parse_args")
def test_main_reports_when_no_new_data(
    mock_parse_args,
    mock_get_connection,
    mock_run_incremental_weather_etl,
    capsys,
):
    mock_parse_args.return_value = MagicMock(
        location="los_angeles",
        latitude=34.0522,
        longitude=-118.2437,
        start_date="2025-01-01",
        end_date="2025-01-03",
    )

    connection = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = connection

    mock_run_incremental_weather_etl.return_value = None

    main()

    output = capsys.readouterr().out

    assert "No new weather data to load." in output
