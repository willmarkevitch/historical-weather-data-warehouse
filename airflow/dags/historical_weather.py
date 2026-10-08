from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from src.ingestion.weather_client import WeatherAPIClient
from src.pipeline.incremental_weather_etl import run_incremental_weather_etl
from src.storage.database import get_connection
from src.storage.raw_storage import RawWeatherStorage


def load_weather(
    location: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> None:
    client = WeatherAPIClient()
    storage = RawWeatherStorage(
        base_dir="/opt/airflow/data/raw",
    )

    with get_connection() as connection:
        result = run_incremental_weather_etl(
            location=location,
            latitude=latitude,
            longitude=longitude,
            requested_start_date=start_date,
            requested_end_date=end_date,
            client=client,
            storage=storage,
            connection=connection,
        )

    if result is None:
        print(f"No new weather data to load for {location}.")
    else:
        print(f"Incremental weather ETL completed for {location}.")


with DAG(
    dag_id="historical_weather",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["weather", "data-engineering"],
) as dag:

    load_san_francisco = PythonOperator(
        task_id="load_san_francisco",
        python_callable=load_weather,
        op_kwargs={
            "location": "San Francisco",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "start_date": "2025-01-01",
            "end_date": "2025-01-05",
        },
    )

    load_los_angeles = PythonOperator(
        task_id="load_los_angeles",
        python_callable=load_weather,
        op_kwargs={
            "location": "Los Angeles",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "start_date": "2025-01-01",
            "end_date": "2025-01-05",
        },
    )
