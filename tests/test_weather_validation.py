from unittest.mock import patch

import pytest

from src.ingestion.weather_client import WeatherAPIClient


@pytest.mark.parametrize(
    "latitude, longitude, start_date, end_date",
    [
        (91, 0, "2025-01-01", "2025-01-07"),
        (-91, 0, "2025-01-01", "2025-01-07"),
        (0, 181, "2025-01-01", "2025-01-07"),
        (0, -181, "2025-01-01", "2025-01-07"),
        ("invalid", 0, "2025-01-01", "2025-01-07"),
        (0, None, "2025-01-01", "2025-01-07"),
        (float("nan"), 0, "2025-01-01", "2025-01-07"),
        (float("inf"), 0, "2025-01-01", "2025-01-07"),
        (0, 0, "invalid", "2025-01-07"),
        (0, 0, "2025-02-30", "2025-03-01"),
        (0, 0, "2025-01-07", "2025-01-01"),
    ],
)
@patch("src.ingestion.weather_client.requests.get")
def test_invalid_inputs(
    mock_get,
    latitude,
    longitude,
    start_date,
    end_date,
):
    client = WeatherAPIClient()

    with pytest.raises(ValueError):
        client.fetch_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
        )

    mock_get.assert_not_called()