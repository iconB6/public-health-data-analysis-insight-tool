import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any
from src.interface.repository_interface import IRepository

'''
responsible for schemainfer
'''
class SchemaInferer:

    CATEGORICAL_KEYWORDS = {
        "year", "quarter", "month", "week",
        "country", "region", "group", "category", "type", "code"
    }

    def infer_column_types(self, rows: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Infer SQLite column types using:
        1. Semantic rules (column name)
        2. Multi-row value inspection
        """
        if not rows:
            raise ValueError("Cannot infer schema from empty rows.")

        col_values = {}
        for row in rows:
            for k, v in row.items():
                if v is not None and v != "":
                    col_values.setdefault(k, []).append(v)

        inferred = {}

        for col, values in col_values.items():
            col_lower = col.lower()

            # ---------- ① semantic override ----------
            if any(keyword in col_lower for keyword in self.CATEGORICAL_KEYWORDS):
                inferred[col] = "TEXT"
                continue

            # ---------- ② numeric inference ----------
            is_int = True
            is_float = True

            for v in values:
                if isinstance(v, int):
                    continue
                if isinstance(v, float):
                    is_int = False
                    continue

                try:
                    iv = int(v)
                    fv = float(v)
                    if iv != fv:
                        is_int = False
                except:
                    is_int = False

                try:
                    float(v)
                except:
                    is_float = False

            if is_int:
                inferred[col] = "INTEGER"
            elif is_float:
                inferred[col] = "REAL"
            else:
                inferred[col] = "TEXT"

        return inferred

'''
responsible for datastore
'''
class DataStorageService:

    def __init__(
        self,
        repository: IRepository,
        table_name: str = "records"
    ):
        self.repo = repository
        self.table_name = table_name
        self.inferer = SchemaInferer()

    # ========== Connection ==========

    def connect(self):
        self.repo.connect()

    def disconnect(self):
        self.repo.disconnect()

    # ========== Transaction ==========

    @contextmanager
    def transaction(self):
        self.repo.begin()
        try:
            yield
            self.repo.commit()
        except Exception:
            self.repo.rollback()
            raise

    # ========== Core API ==========

    def save_full_record(self, rows: List[Dict[str, Any]]) -> int:
        if not rows:
            return 0

        for row in rows:
            if not isinstance(row, dict):
                raise TypeError("Each row must be a dict")

        valid_rows = [
            row for row in rows
            if any(v is not None and v != "" for v in row.values())
        ]

        if not valid_rows:
            return 0

        schema = self.inferer.infer_column_types(valid_rows)
        if not schema:
            return 0

        self.repo.ensure_table(self.table_name, schema)

        return self.repo.insert_rows(
            table=self.table_name,
            rows=valid_rows,
            columns=list(schema.keys()),
        )