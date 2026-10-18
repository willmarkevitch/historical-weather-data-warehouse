-- Normalize location names and consolidate duplicate locations.
-- Run inside a transaction.

-- Allow repeated execution within the same transaction.
DROP TABLE IF EXISTS pg_temp.location_merge_map;

-- Step 1: Build a mapping of each location to its canonical location.
CREATE TEMP TABLE location_merge_map ON COMMIT DROP AS
WITH normalized AS (
    SELECT
        id,
        name,
        REPLACE(
        REGEXP_REPLACE(
            LOWER(BTRIM(name)),
            '[[:space:]]+',
            '_',
            'g'
        ),
        '-',
        '_'
    ) AS canonical_name
    FROM locations
),
canonical AS (
    SELECT
        canonical_name,
        COALESCE(
            MIN(id) FILTER (
                WHERE name = canonical_name
            ),
            MIN(id)
        ) AS canonical_id
    FROM normalized
    GROUP BY canonical_name
)
SELECT
    n.id AS old_id,
    c.canonical_id,
    n.canonical_name
FROM normalized n
JOIN canonical c
    ON n.canonical_name = c.canonical_name;

-- Step 1b: Reject conflicting observations across all locations
-- that normalize to the same canonical name.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM weather_observations AS observation_a
        JOIN location_merge_map AS mapping_a
            ON observation_a.location_id = mapping_a.old_id
        JOIN weather_observations AS observation_b
            ON observation_a.observed_at = observation_b.observed_at
           AND observation_a.id < observation_b.id
        JOIN location_merge_map AS mapping_b
            ON observation_b.location_id = mapping_b.old_id
        WHERE mapping_a.canonical_id = mapping_b.canonical_id
          AND (
              observation_a.temperature_c
                  IS DISTINCT FROM observation_b.temperature_c
              OR observation_a.relative_humidity_pct
                  IS DISTINCT FROM observation_b.relative_humidity_pct
              OR observation_a.precipitation_mm
                  IS DISTINCT FROM observation_b.precipitation_mm
              OR observation_a.latitude
                  IS DISTINCT FROM observation_b.latitude
              OR observation_a.longitude
                  IS DISTINCT FROM observation_b.longitude
          )
    ) THEN
        RAISE EXCEPTION
            'Location normalization aborted: conflicting weather observations detected';
    END IF;
END
$$;

-- Step 2: Remove redundant observations after conflict validation.
-- Prefer canonical observations, then the lowest observation ID.

WITH ranked_observations AS (
    SELECT
        observation.id,
        ROW_NUMBER() OVER (
            PARTITION BY
                mapping.canonical_id,
                observation.observed_at
            ORDER BY
                CASE
                    WHEN observation.location_id = mapping.canonical_id
                    THEN 0
                    ELSE 1
                END,
                observation.id
        ) AS row_number
    FROM weather_observations AS observation
    JOIN location_merge_map AS mapping
        ON observation.location_id = mapping.old_id
)
DELETE FROM weather_observations AS observation
USING ranked_observations AS ranked
WHERE observation.id = ranked.id
  AND ranked.row_number > 1;

-- Step 3: Move remaining observations to the canonical location.
UPDATE weather_observations AS observation
SET location_id = mapping.canonical_id
FROM location_merge_map AS mapping
WHERE observation.location_id = mapping.old_id
  AND mapping.old_id <> mapping.canonical_id;


-- Step 4: Remove redundant location records.
DELETE FROM locations AS location
USING location_merge_map AS mapping
WHERE location.id = mapping.old_id
  AND mapping.old_id <> mapping.canonical_id;


-- Step 5: Standardize the remaining location names.
UPDATE locations AS location
SET name = mapping.canonical_name
FROM location_merge_map AS mapping
WHERE location.id = mapping.canonical_id
  AND location.name <> mapping.canonical_name;
