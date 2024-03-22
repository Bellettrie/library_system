from django.db import connection


def get_lending_stats(start_date, end_date) -> dict[str, int]:
    # Get the number of lendings which started within a specific period, grouped by the category (SF, Dutch, etc.) within the library
    query = """
    SELECT
        works_category.name, count(*)
    FROM
        lendings_lending
    LEFT JOIN works_item
        ON lendings_lending.item_id = works_item.id
    LEFT JOIN works_location ON
        works_item.location_id = works_location.id
    LEFT JOIN works_category ON
        works_location.category_id = works_category.id
    WHERE lendings_lending.start_date>=%s AND lendings_lending.end_date<%s
    GROUP BY works_category.id
    ORDER BY works_category.name ASC;"""
    quadrants = dict()

    with connection.cursor() as c:
        c.execute(query, [start_date, end_date])
        for r in c:
            quadrants[r[0]] = r[1]

    return quadrants
