import sqlite3
from typing import Dict, Any
from src.interface.data_repository_interface import IDataRepository


class SQLiteRepository(IDataRepository):

    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_source TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS record_dimensions (
                record_id INTEGER,
                key TEXT,
                value TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS record_metrics (
                record_id INTEGER,
                metric_name TEXT,
                metric_value REAL
            )
        """)

        self.conn.commit()

    def save_record(self, record_data: Dict[str, Any]) -> int:
        cur = self.conn.cursor()

        cur.execute(
            "INSERT INTO records (data_source) VALUES (?)",
            (record_data["data_source"],),
        )
        self.conn.commit()

        return cur.lastrowid

    def save_dimensions(self, record_id: int, dimensions: Dict[str, str]) -> None:
        cur = self.conn.cursor()
        for k, v in dimensions.items():
            cur.execute(
                "INSERT INTO record_dimensions (record_id, key, value) VALUES (?, ?, ?)",
                (record_id, k, v),
            )
        self.conn.commit()

    def save_metrics(self, record_id: int, metrics: Dict[str, float]) -> None:
        cur = self.conn.cursor()
        for k, v in metrics.items():
            cur.execute(
                "INSERT INTO record_metrics (record_id, metric_name, metric_value) VALUES (?, ?, ?)",
                (record_id, k, v),
            )
        self.conn.commit()

    def get_record(self, record_id: int) -> Dict[str, Any]:
        cur = self.conn.cursor()

        cur.execute("SELECT * FROM records WHERE record_id = ?", (record_id,))
        record_row = cur.fetchone()

        if record_row is None:
            raise ValueError(f"Record not found: {record_id}")

        cur.execute(
            "SELECT key, value FROM record_dimensions WHERE record_id = ?",
            (record_id,)
        )
        dimensions = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute(
            "SELECT metric_name, metric_value FROM record_metrics WHERE record_id = ?",
            (record_id,)
        )
        metrics = {row[0]: row[1] for row in cur.fetchall()}

        return {
            "record_id": record_id,
            "data_source": record_row[1],
            "dimensions": dimensions,
            "metrics": metrics,
        }
    def get_all_records(self):

        cur = self.conn.cursor()

        # fetch all record IDs
        cur.execute("SELECT record_id, data_source FROM records")
        record_rows = cur.fetchall()

        results = []

        for record_id, data_source in record_rows:

            # dimensions
            cur.execute(
                "SELECT key, value FROM record_dimensions WHERE record_id = ?",
                (record_id,)
            )
            dimensions = {row[0]: row[1] for row in cur.fetchall()}

            # metrics
            cur.execute(
                "SELECT metric_name, metric_value FROM record_metrics WHERE record_id = ?",
                (record_id,)
            )
            metrics = {row[0]: row[1] for row in cur.fetchall()}

            results.append({
                "record_id": record_id,
                "data_source": data_source,
                "dimensions": dimensions,
                "metrics": metrics
            })

        return results
