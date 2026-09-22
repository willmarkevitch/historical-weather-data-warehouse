from unittest.mock import patch

import pytest

from src.ingestion.weather_client import WeatherAPIClient

@pytest.mark.parametrize(
    "response",
    [
        # 1. Empty response
        {},

        # 2. Null response
        None,

        # 3. Incorrect response type
        [],

        # 4. API error response
        {
            "error": True,
            "reason": "Invalid request",
        },

        # 5. Missing required hourly fields
        {
            "hourly": {},
        },

        # 6. Empty hourly observations
        {
            "hourly": {
                "time": [],
                "temperature_2m": [],
                "relative_humidity_2m": [],
                "precipitation": [],
            },
        },

        # 7. Inconsistent array lengths
        {
            "hourly": {
                "time": ["2025-01-01T00:00"],
                "temperature_2m": [],
                "relative_humidity_2m": [75],
                "precipitation": [0.0],
            },
        },

        # 8. Incorrect field type
        {
            "hourly": {
                "time": ["2025-01-01T00:00"],
                "temperature_2m": "invalid",
                "relative_humidity_2m": [75],
                "precipitation": [0.0],
            },
        },
    ],
)
def test_invalid_api_response(response):
    with pytest.raises(ValueError):
        WeatherAPIClient.validate_response(response)


def test_valid_api_response():
    response = {
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
            "relative_humidity_2m": [75],
            "precipitation": [0.0],
        }
    }

    WeatherAPIClient.validate_response(response)


@patch("src.ingestion.weather_client.requests.get")
def test_fetch_weather_rejects_invalid_response(mock_get):
    mock_get.return_value.json.return_value = {
        "hourly": {}
    }

    client = WeatherAPIClient()

    with pytest.raises(
        ValueError,
        match="Missing required field",
    ):
        client.fetch_weather(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-01",
            end_date="2025-01-07",
        )

    mock_get.assert_called_once()
    mock_get.return_value.raise_for_status.assert_called_once()
