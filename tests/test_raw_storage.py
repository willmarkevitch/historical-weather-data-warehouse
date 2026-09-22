from unittest.mock import patch

import json

import pytest

from src.storage.raw_storage import RawWeatherStorage

@pytest.fixture
def sample_weather():
    return {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [12.5],
            "relative_humidity_2m": [75],
            "precipitation": [0.0],
        },
    }


def test_save_creates_file(tmp_path, sample_weather):
    storage = RawWeatherStorage(base_dir=tmp_path)

    file_path = storage.save(
        data=sample_weather,
        filename="weather.json",
    )

    assert file_path.exists()
    assert file_path.is_file()


def test_save_preserves_json(tmp_path, sample_weather):
    storage = RawWeatherStorage(base_dir=tmp_path)

    file_path = storage.save(
        data=sample_weather,
        filename="weather.json",
    )

    with file_path.open("r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == sample_weather


def test_save_creates_directories(tmp_path, sample_weather):
    nested_dir = tmp_path / "data" / "raw" / "weather"

    assert not nested_dir.exists()

    storage = RawWeatherStorage(base_dir=nested_dir)

    file_path = storage.save(
        data=sample_weather,
        filename="weather.json",
    )

    assert nested_dir.is_dir()
    assert file_path.exists()


def test_save_prevents_overwrite(tmp_path, sample_weather):
    storage = RawWeatherStorage(base_dir=tmp_path)

    file_path = storage.save(
        data=sample_weather,
        filename="weather.json",
    )

    original_contents = file_path.read_text(encoding="utf-8")

    with pytest.raises(FileExistsError):
        storage.save(
            data={"unexpected": "replacement"},
            filename="weather.json",
        )

    assert file_path.read_text(encoding="utf-8") == original_contents


def test_save_returns_correct_path(tmp_path, sample_weather):
    storage = RawWeatherStorage(base_dir=tmp_path)

    file_path = storage.save(
        data=sample_weather,
        filename="weather.json",
    )

    assert file_path == tmp_path / "weather.json"


@pytest.mark.parametrize(
    "filename",
    [
        "../outside.json",
        "nested/weather.json",
        "/tmp/weather.json",
        "weather.txt",
        "",
    ],
)
def test_save_rejects_invalid_filename(tmp_path, sample_weather, filename):
    storage = RawWeatherStorage(base_dir=tmp_path / "raw")

    with pytest.raises(ValueError):
        storage.save(
            data=sample_weather,
            filename=filename,
        )


def test_save_does_not_create_file_when_serialization_fails(tmp_path):
    storage = RawWeatherStorage(base_dir=tmp_path)

    invalid_data = {
        "temperature": {12.5, 13.0},
    }

    with pytest.raises(TypeError):
        storage.save(
            data=invalid_data,
            filename="weather.json",
        )

    assert not (tmp_path / "weather.json").exists()


@patch(
    "src.storage.raw_storage.os.link",
    side_effect=OSError("Simulated publish failure"),
)
def test_save_cleans_up_temp_file_on_publish_failure(
    mock_link,
    tmp_path,
    sample_weather,
):
    storage = RawWeatherStorage(base_dir=tmp_path)

    with pytest.raises(
        OSError,
        match="Simulated publish failure",
    ):
        storage.save(
            data=sample_weather,
            filename="weather.json",
        )

    mock_link.assert_called_once()

    assert list(tmp_path.iterdir()) == []
