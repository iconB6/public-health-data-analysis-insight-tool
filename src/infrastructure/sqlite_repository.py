import sqlite3
from typing import Dict, Any, List
import re
from src.interface.data_repository_interface import IDataRepository
from datetime import datetime


class SQLiteRepository(IDataRepository):

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def connect(self):
         if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        if self.conn is not None:
            try:
                self.conn.close()
            finally:
                self.conn = None

    def execute(self, query: str, params: tuple = ()):
        cur = self.conn.execute(query, params) if params else self.conn.execute(query)
        return cur

    def executemany(self, query: str, params_list: List[tuple]):
        cur = self.conn.executemany(query, params_list)
        return cur

    # -------------------------
    # Transactions
    # -------------------------
    def begin(self):
        if self.conn is not None:
            self.conn.execute("BEGIN")

    def commit(self):
        if self.conn is not None:
            self.conn.commit()

    def rollback(self):
        if self.conn is not None:
            self.conn.rollback()

    # -------------------------
    # Context Manager
    # -------------------------
    def __enter__(self):
        # Return repository itself so callers can use its methods
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            try:
                self.rollback()
            except Exception:
                pass
        else:
            try:
                self.commit()
            except Exception:
                pass
    
    # ---- Type inference ----
    def infer_type(self, value: Any) -> str:
        """
        Infer SQLite column type from Python value.
        """
        if value is None:
            return "TEXT"  # default fallback

        # Try INT
        try:
            int(value)
            return "INTEGER"
        except:
            pass

        # Try FLOAT
        try:
            float(value)
            return "REAL"
        except:
            pass

        # Try DATE (YYYY-MM-DD)
        if isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return "TEXT"   # SQLite has no pure DATE type, store as TEXT

        # Default
        return "TEXT"

    def create_tables(self, rows: List[Dict[str, Any]]):
        if not rows:
            raise ValueError("Cannot infer structure from empty rows.")

        sample = rows[0]

        columns_sql = ["record_id INTEGER PRIMARY KEY AUTOINCREMENT"]

        for key, value in sample.items():
            col_type = self.infer_type(value)
            safe_key = key.replace(" ", "_").replace("-", "_")
            # quote identifiers to avoid conflicts with SQL keywords (e.g. group)
            columns_sql.append(f'"{safe_key}" {col_type}')

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS records (
            {", ".join(columns_sql)}
        );
        """

        self.conn.execute(create_sql)
        self.conn.commit()

    def save_records(self, rows: List[Dict[str, Any]]) -> int:
        if not rows:
            return

        keys = [k.replace(" ", "_").replace("-", "_") for k in rows[0].keys()]
        placeholders = ",".join(["?"] * len(keys))

        # quote column identifiers
        quoted_cols = ",".join([f'"{k}"' for k in keys])

        sql = f"INSERT INTO records ({quoted_cols}) VALUES ({placeholders})"

        values = [
            [row[k] for k in rows[0].keys()]
            for row in rows
        ]

        self.conn.executemany(sql, values)
        self.conn.commit()

        # return number of rows inserted
        return len(rows)

    def get_all_records(self):
        cur = self.conn.execute("SELECT * FROM records")
        return [dict(row) for row in cur.fetchall()]
    
    def get_columns(self) -> List[str]:
        """
        Return all columns of records table.
        """
        cur = self.conn.execute("PRAGMA table_info(records)")
        return [row["name"] for row in cur.fetchall()]
