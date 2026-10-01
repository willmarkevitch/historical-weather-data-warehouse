from psycopg import Connection


def get_location_id(
    connection: Connection,
    name: str,
) -> int | None:
    query = """
        SELECT id
        FROM locations
        WHERE name = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (name,),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return row[0]

def create_location(
    connection: Connection,
    name: str,
    requested_latitude: float,
    requested_longitude: float,
) -> int:
    query = """
        INSERT INTO locations (
            name,
            requested_latitude,
            requested_longitude
        )
        VALUES (%s, %s, %s)
        RETURNING id;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                name,
                requested_latitude,
                requested_longitude,
            ),
        )
        row = cursor.fetchone()

    return row[0]
