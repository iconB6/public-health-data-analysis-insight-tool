import os
import random
import string
import datetime
import pytest


DB_URL = os.getenv("CLOUD_DB_URL")


pytestmark = pytest.mark.skipif(
    not DB_URL,
    reason="CLOUD_DB_URL not set; integration tests for cloud DB are skipped",
)


def _random_table_name():
    return "test_cloud_repo_" + "".join(random.choices(string.ascii_lowercase, k=8))


def test_cloud_repository_crud_and_trend():
    # TDD: expect a CloudRepository implementing IRepository API
    from src.infrastructure.cloud_repository import CloudRepository

    table = _random_table_name()
    schema = {"country": "TEXT", "value": "INTEGER", "date": "DATE"}

    rows = [
        {"country": "A", "value": 10, "date": datetime.date(2024, 1, 1)},
        {"country": "A", "value": 20, "date": datetime.date(2024, 1, 1)},
        {"country": "B", "value": 5,  "date": datetime.date(2024, 1, 2)},
    ]

    repo = CloudRepository(DB_URL)
    repo.connect()

    try:
        # ensure table exists
        repo.ensure_table(table, schema)

        # insert
        inserted = repo.insert_rows(table=table, rows=rows, columns=["country", "value", "date"])
        assert inserted == len(rows)

        # basic query
        all_rows = repo.query()
        assert isinstance(all_rows, list)

        # trend query
        trend = repo.query_for_trend(date_field="date")
        assert isinstance(trend, list)

    finally:
        # cleanup if implementation provides deletion
        try:
            repo.delete_where(table, {})
        except Exception:
            # implementations may require explicit where; best effort cleanup
            pass
        repo.disconnect()
