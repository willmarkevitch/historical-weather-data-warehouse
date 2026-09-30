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
