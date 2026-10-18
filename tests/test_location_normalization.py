import pytest

from src.storage.location_normalization import normalize_location_name


@pytest.mark.parametrize(
    "name, expected",
    [
        ("San Francisco", "san_francisco"),
        ("san_francisco", "san_francisco"),
        ("san francisco", "san_francisco"),
        ("  SAN FRANCISCO  ", "san_francisco"),
        ("Los Angeles", "los_angeles"),
        ("los_angeles", "los_angeles"),
    ],
)
def test_normalize_location_name(name, expected):
    assert normalize_location_name(name) == expected
