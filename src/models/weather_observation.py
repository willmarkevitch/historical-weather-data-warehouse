from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WeatherObservation:
    timestamp: datetime
    latitude: float
    longitude: float
    temperature_c: float | None
    relative_humidity_pct: int | None
    precipitation_mm: float | None