CREATE TABLE locations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    name TEXT NOT NULL,

    requested_latitude DOUBLE PRECISION NOT NULL,
    requested_longitude DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT locations_name_unique
        UNIQUE (name),

    CONSTRAINT locations_latitude_check
        CHECK (
            requested_latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT locations_longitude_check
        CHECK (
            requested_longitude BETWEEN -180 AND 180
        )
);


-- Seed the locations that already have observations in the warehouse.
INSERT INTO locations (
    name,
    requested_latitude,
    requested_longitude
)
VALUES
    ('san_francisco', 37.7749, -122.4194),
    ('los_angeles', 34.0522, -118.2437);


-- Add a location reference to existing weather observations.
-- It is initially nullable so existing rows can be backfilled.
ALTER TABLE weather_observations
ADD COLUMN location_id BIGINT;

ALTER TABLE weather_observations
ADD CONSTRAINT weather_observations_location_id_fkey
FOREIGN KEY (location_id)
REFERENCES locations(id);


-- Backfill the existing San Francisco observations.
UPDATE weather_observations
SET location_id = (
    SELECT id
    FROM locations
    WHERE name = 'san_francisco'
)
WHERE latitude = 37.785587
  AND longitude = -122.40964;


-- Backfill the existing Los Angeles observations.
UPDATE weather_observations
SET location_id = (
    SELECT id
    FROM locations
    WHERE name = 'los_angeles'
)
WHERE latitude = 34.059753
  AND longitude = -118.2375;


-- All existing observations now have a location, so enforce it.
ALTER TABLE weather_observations
ALTER COLUMN location_id SET NOT NULL;