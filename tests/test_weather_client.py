from unittest.mock import patch, Mock

import pytest
import requests

from src.ingestion.weather_client import WeatherAPIClient

@patch("src.ingestion.weather_client.requests.get")
def test_fetch_weather_success(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
            "relative_humidity_2m": [75],
            "precipitation": [0.0],
        },
    }

    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = WeatherAPIClient()

    result = client.fetch_weather(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-01",
    )

    assert result == mock_response.json.return_value

    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()

@patch("src.ingestion.weather_client.requests.get")
def test_fetch_weather_request_parameters(mock_get):
    client = WeatherAPIClient(timeout=15)

    mock_get.return_value.json.return_value = {
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
            "relative_humidity_2m": [75],
            "precipitation": [0.0],
        }
    }

    client.fetch_weather(
        latitude=37.7749,
        longitude=-122.4194,
        start_date="2025-01-01",
        end_date="2025-01-07",
    )

    mock_get.assert_called_once_with(
        WeatherAPIClient.BASE_URL,
        params={
            "latitude": 37.7749,
            "longitude": -122.4194,
            "start_date": "2025-01-01",
            "end_date": "2025-01-07",
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation"
            ),
            "timezone": "UTC",
        },
        timeout=15,
    )


@patch("src.ingestion.weather_client.requests.get")
def test_fetch_weather_http_error(mock_get):
    mock_response = Mock()

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )

    mock_get.return_value = mock_response

    client = WeatherAPIClient()

    with pytest.raises(requests.exceptions.HTTPError):
        client.fetch_weather(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-01",
            end_date="2025-01-07",
        )

    mock_response.json.assert_not_called()


@patch("src.ingestion.weather_client.requests.get")
def test_fetch_weather_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout(
        "Request timed out"
    )

    client = WeatherAPIClient(timeout=5)

    with pytest.raises(requests.exceptions.Timeout):
        client.fetch_weather(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-01",
            end_date="2025-01-07",
        )

    mock_get.assert_called_once()


@patch("src.ingestion.weather_client.requests.get")
def test_fetch_weather_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError(
        "Unable to connect"
    )

    client = WeatherAPIClient()

    with pytest.raises(requests.exceptions.ConnectionError):
        client.fetch_weather(
            latitude=37.7749,
            longitude=-122.4194,
            start_date="2025-01-01",
            end_date="2025-01-07",
        )

    mock_get.assert_called_once()