CREATE TABLE IF NOT EXISTS weather_observations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    observed_at TIMESTAMPTZ NOT NULL,

    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,

    temperature_c DOUBLE PRECISION,
    relative_humidity_pct INTEGER,
    precipitation_mm DOUBLE PRECISION,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT weather_observations_humidity_check
        CHECK (
            relative_humidity_pct IS NULL
            OR relative_humidity_pct BETWEEN 0 AND 100
        ),

    CONSTRAINT weather_observations_precipitation_check
        CHECK (
            precipitation_mm IS NULL
            OR precipitation_mm >= 0
        ),

    CONSTRAINT weather_observations_location_time_unique
        UNIQUE (observed_at, latitude, longitude)
);