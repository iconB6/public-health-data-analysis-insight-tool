import sqlite3
import pytest
from pathlib import Path

from application.import_pipeline import import_data
from src.infrastructure.sqlite_repository import SQLiteRepository


# ========== FIXTURES ==========

@pytest.fixture
def csv_file(tmp_path: Path):
    file_path = tmp_path / "input.csv"
    file_path.write_text(
        "country,year,value\n"
        "USA,2020,100\n"
        "UK,2021,200\n"
    )
    return file_path


@pytest.fixture
def db_path(tmp_path: Path):
    return tmp_path / "output.db"


# ========== INTEGRATION TEST ==========

def test_full_import_pipeline_csv_to_sqlite(csv_file, db_path):
    repo = SQLiteRepository(str(db_path))

    inserted = import_data(
        source_type="csv",
        source_path=str(csv_file),
        repository=repo,
    )

    # ---------- assertions ----------
    assert inserted == 2

    # verify data persisted
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM records;")
    count = cur.fetchone()[0]

    assert count == 2

    # verify schema inference
    cur.execute("PRAGMA table_info(records);")
    schema = {row[1]: row[2].upper() for row in cur.fetchall()}

    assert schema["COUNTRY"] == "TEXT"
    assert schema["YEAR"] == "TEXT"      # semantic override
    assert schema["VALUE"] == "INTEGER"

    conn.close()

