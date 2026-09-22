from datetime import date

import requests

class WeatherAPIClient:
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @staticmethod
    def validate_inputs(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> None:

        if not isinstance(latitude, (int, float)) or isinstance(latitude, bool):
            raise ValueError("Latitude must be numeric")

        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")

        if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
            raise ValueError("Longitude must be numeric")

        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except (ValueError, TypeError):
            raise ValueError("Dates must use YYYY-MM-DD format") from None

        if start.isoformat() != start_date or end.isoformat() != end_date:
            raise ValueError("Dates must use YYYY-MM-DD format")

        if start > end:
            raise ValueError("Start date cannot be after end date")

    @staticmethod
    def validate_response(data: dict) -> None:
        if not isinstance(data, dict):
            raise ValueError("API response must be a JSON object")

        if data.get("error") is True:
            raise ValueError(
                f"API returned an error: {data.get('reason', 'Unknown error')}"
            )

        hourly = data.get("hourly")

        if not isinstance(hourly, dict):
            raise ValueError("Missing or invalid hourly data")

        required_fields = (
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
        )

        for field in required_fields:
            if field not in hourly:
                raise ValueError(f"Missing required field: {field}")

            if not isinstance(hourly[field], list):
                raise ValueError(f"Field must be a list: {field}")

        expected_length = len(hourly["time"])

        if expected_length == 0:
            raise ValueError("Hourly data cannot be empty")

        for field in required_fields:
            if len(hourly[field]) != expected_length:
                raise ValueError(
                    f"Field {field} has an inconsistent length"
                )

    def fetch_weather(
            self,
            latitude: float,
            longitude: float,
            start_date: str,
            end_date: str
    ) -> dict:

        self.validate_inputs(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
        )

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation"
            ),
            "timezone": "UTC",
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout
        )

        response.raise_for_status()

        data = response.json()

        self.validate_response(data)

        return data