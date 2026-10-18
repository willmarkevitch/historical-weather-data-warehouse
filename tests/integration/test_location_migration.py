from pathlib import Path

import psycopg
import pytest


pytestmark = pytest.mark.integration

MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "sql"
    / "004_normalize_location_names.sql"
)


def test_location_migration_preserves_observations():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="weather_test",
        user="weather_user",
        password="weather_password",
    )

    try:
        with connection.transaction(force_rollback=True):
            with connection.cursor() as cursor:
                # Create duplicate location.
                cursor.execute(
                    """
                    INSERT INTO locations (
                        name,
                        requested_latitude,
                        requested_longitude
                    )
                    VALUES ('San Francisco', 37.7749, -122.4194)
                    RETURNING id;
                    """
                )
                duplicate_id = cursor.fetchone()[0]

                # Add one observation to the canonical location.
                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES (
                        '2099-01-01 00:00:00+00',
                        37.7749,
                        -122.4194,
                        15.0,
                        1
                    );
                    """
                )

                # Add an overlapping observation to the duplicate.
                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES (
                        '2099-01-01 00:00:00+00',
                        37.7749,
                        -122.4194,
                        15.0,
                        %s
                    );
                    """,
                    (duplicate_id,),
                )

                # Add a unique observation to the duplicate.
                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES (
                        '2099-01-01 01:00:00+00',
                        37.7749,
                        -122.4194,
                        16.0,
                        %s
                    );
                    """,
                    (duplicate_id,),
                )

                # Apply the migration.
                migration_sql = MIGRATION_PATH.read_text(
                    encoding="utf-8"
                )
                cursor.execute(migration_sql)

                # Verify only the canonical location remains.
                cursor.execute(
                    """
                    SELECT name
                    FROM locations
                    WHERE name IN (
                        'san_francisco',
                        'San Francisco'
                    )
                    ORDER BY name;
                    """
                )
                assert cursor.fetchall() == [
                    ("san_francisco",)
                ]

                # Verify both distinct timestamps survive.
                cursor.execute(
                    """
                    SELECT observed_at, temperature_c
                    FROM weather_observations
                    WHERE location_id = 1
                    ORDER BY observed_at;
                    """
                )
                rows = cursor.fetchall()

                assert len(rows) == 2
                assert [row[1] for row in rows] == [
                    15.0,
                    16.0,
                ]

                # Verify the migration is idempotent.
                cursor.execute(migration_sql)

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM weather_observations
                    WHERE location_id = 1;
                    """
                )
                assert cursor.fetchone()[0] == 2


    finally:
        connection.close()


def test_location_migration_rejects_conflicting_observations():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="weather_test",
        user="weather_user",
        password="weather_password",
    )

    try:
        with connection.transaction(force_rollback=True):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO locations (
                        name,
                        requested_latitude,
                        requested_longitude
                    )
                    VALUES ('San Francisco', 37.7749, -122.4194)
                    RETURNING id;
                    """
                )
                duplicate_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES
                        (
                            '2099-02-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            1
                        ),
                        (
                            '2099-02-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            19.0,
                            %s
                        );
                    """,
                    (duplicate_id,),
                )

                migration_sql = MIGRATION_PATH.read_text(
                    encoding="utf-8"
                )

                with pytest.raises(
                    psycopg.errors.RaiseException
                ):
                    cursor.execute(migration_sql)

    finally:
        connection.close()


def test_location_migration_rejects_conflicts_between_duplicates():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="weather_test",
        user="weather_user",
        password="weather_password",
    )

    try:
        with connection.transaction(force_rollback=True):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO locations (
                        name,
                        requested_latitude,
                        requested_longitude
                    )
                    VALUES
                        ('San Francisco', 37.7749, -122.4194),
                        ('SAN FRANCISCO', 37.7749, -122.4194)
                    RETURNING id;
                    """
                )
                duplicate_ids = [
                    row[0] for row in cursor.fetchall()
                ]

                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES
                        (
                            '2099-03-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            %s
                        ),
                        (
                            '2099-03-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            19.0,
                            %s
                        );
                    """,
                    tuple(duplicate_ids),
                )

                migration_sql = MIGRATION_PATH.read_text(
                    encoding="utf-8"
                )

                with pytest.raises(
                    psycopg.errors.RaiseException
                ):
                    cursor.execute(migration_sql)

    finally:
        connection.close()


def test_location_migration_merges_three_identical_observations():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="weather_test",
        user="weather_user",
        password="weather_password",
    )

    try:
        with connection.transaction(force_rollback=True):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO locations (
                        name,
                        requested_latitude,
                        requested_longitude
                    )
                    VALUES
                        ('San Francisco', 37.7749, -122.4194),
                        ('SAN FRANCISCO', 37.7749, -122.4194)
                    RETURNING id;
                    """
                )
                duplicate_ids = [
                    row[0] for row in cursor.fetchall()
                ]

                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES
                        (
                            '2099-04-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            1
                        ),
                        (
                            '2099-04-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            %s
                        ),
                        (
                            '2099-04-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            %s
                        );
                    """,
                    tuple(duplicate_ids),
                )

                migration_sql = MIGRATION_PATH.read_text(
                    encoding="utf-8"
                )
                cursor.execute(migration_sql)

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM weather_observations
                    WHERE location_id = 1
                      AND observed_at = '2099-04-01 00:00:00+00';
                    """
                )
                assert cursor.fetchone()[0] == 1

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM locations
                    WHERE LOWER(REPLACE(name, ' ', '_'))
                        = 'san_francisco';
                    """
                )
                assert cursor.fetchone()[0] == 1

    finally:
        connection.close()


def test_location_migration_merges_identical_duplicates_without_canonical_observation():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="weather_test",
        user="weather_user",
        password="weather_password",
    )

    try:
        with connection.transaction(force_rollback=True):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO locations (
                        name,
                        requested_latitude,
                        requested_longitude
                    )
                    VALUES
                        ('San Francisco', 37.7749, -122.4194),
                        ('SAN FRANCISCO', 37.7749, -122.4194)
                    RETURNING id;
                    """
                )
                duplicate_ids = [
                    row[0] for row in cursor.fetchall()
                ]

                cursor.execute(
                    """
                    INSERT INTO weather_observations (
                        observed_at,
                        latitude,
                        longitude,
                        temperature_c,
                        location_id
                    )
                    VALUES
                        (
                            '2099-05-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            %s
                        ),
                        (
                            '2099-05-01 00:00:00+00',
                            37.7749,
                            -122.4194,
                            15.0,
                            %s
                        );
                    """,
                    tuple(duplicate_ids),
                )

                migration_sql = MIGRATION_PATH.read_text(
                    encoding="utf-8"
                )
                cursor.execute(migration_sql)

                cursor.execute(
                    """
                    SELECT temperature_c
                    FROM weather_observations
                    WHERE location_id = 1
                      AND observed_at = '2099-05-01 00:00:00+00';
                    """
                )

                assert cursor.fetchall() == [(15.0,)]

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM locations
                    WHERE LOWER(REPLACE(name, ' ', '_'))
                        = 'san_francisco';
                    """
                )
                assert cursor.fetchone()[0] == 1

    finally:
        connection.close()


def test_location_migration_normalizes_whitespace_and_hyphens():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="weather_test",
        user="weather_user",
        password="weather_password",
    )

    try:
        with connection.transaction(force_rollback=True):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO locations (
                        name,
                        requested_latitude,
                        requested_longitude
                    )
                    VALUES
                        ('  San   Francisco  ', 37.7749, -122.4194),
                        ('San-Francisco', 37.7749, -122.4194),
                        (E'San\\tFrancisco', 37.7749, -122.4194);
                    """
                )

                migration_sql = MIGRATION_PATH.read_text(
                    encoding="utf-8"
                )
                cursor.execute(migration_sql)

                cursor.execute(
                    """
                    SELECT name
                    FROM locations
                    WHERE LOWER(name) LIKE '%francisco%'
                    ORDER BY name;
                    """
                )

                assert cursor.fetchall() == [
                    ("san_francisco",)
                ]

    finally:
        connection.close()
