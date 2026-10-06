from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def verify_airflow_setup() -> None:
    print("Historical weather Airflow DAG is running.")


with DAG(
    dag_id="historical_weather",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["weather", "data-engineering"],
) as dag:
    verify_setup = PythonOperator(
        task_id="verify_airflow_setup",
        python_callable=verify_airflow_setup,
    )
