import os
from pathlib import Path

import pytest
from airflow.models.dagbag import DagBag


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DAGS_FOLDER = Path(
    os.getenv("AIRFLOW_TEST_DAGS_FOLDER", PROJECT_ROOT / "airflow" / "dags")
)


@pytest.fixture(scope="module")
def dagbag():
    return DagBag(dag_folder=str(DAGS_FOLDER))


def test_historical_weather_dag_loads(dagbag):
    assert dagbag.import_errors == {}
    assert "historical_weather" in dagbag.dags


def test_historical_weather_dag_has_expected_tasks(dagbag):
    dag = dagbag.get_dag("historical_weather")

    assert dag is not None
    assert set(dag.task_ids) == {
        "load_san_francisco",
        "load_los_angeles",
    }


def test_historical_weather_dag_is_manually_triggered(dagbag):
    dag = dagbag.get_dag("historical_weather")

    assert dag is not None
    assert dag.schedule is None
    assert dag.catchup is False


def test_historical_weather_tasks_have_correct_parameters(dagbag):
    dag = dagbag.get_dag("historical_weather")

    assert dag is not None

    sf = dag.get_task("load_san_francisco")
    la = dag.get_task("load_los_angeles")

    assert sf.op_kwargs["location"] == "San Francisco"
    assert sf.op_kwargs["latitude"] == 37.7749
    assert sf.op_kwargs["longitude"] == -122.4194

    assert la.op_kwargs["location"] == "Los Angeles"
    assert la.op_kwargs["latitude"] == 34.0522
    assert la.op_kwargs["longitude"] == -118.2437
