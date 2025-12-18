from typing import Dict, List, Any, Optional
from datetime import date

try:
    import psycopg2
    from psycopg2 import sql
except Exception:  # pragma: no cover - import only required for integration runs
    psycopg2 = None
    sql = None

from src.interface.repository_interface import IRepository


class CloudRepository(IRepository):
    """
    - Requires `psycopg2` to be installed when used.
    - Intended for integration tests; unit tests should use fakes/mocks.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None
        self._table_default = "records"
    
    def connect(self):
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for CloudRepository")
        if self.conn is None:
            self.conn = psycopg2.connect(self.dsn)
            self.conn.autocommit = False

    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None

    # ========== transaction ==========
    def begin(self):
        if not self.conn:
            raise RuntimeError("Not connected")
        # Explicit BEGIN
        with self.conn.cursor() as cur:
            cur.execute("BEGIN")
    def commit(self):
        if not self.conn:
            raise RuntimeError("Not connected")
        self.conn.commit()

    def rollback(self):
        if not self.conn:
            raise RuntimeError("Not connected")
        self.conn.rollback()

    def ensure_table(self, table: str, schema: Dict[str, str]):
        if not self.conn:
            raise RuntimeError("Not connected")

        # remember the table as the default for subsequent query operations
        self._table_default = table

        # Quote identifiers to handle reserved words (e.g. GROUP) and special names
        cols = ", ".join(f'"{col}" {dtype}' for col, dtype in schema.items())

        create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({cols})'
        with self.conn.cursor() as cur:
            cur.execute(create_sql)

    def get_schema(self, table: str) -> Dict[str, str]:
        if not self.conn:
            raise RuntimeError("Not connected")

        q = (
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = %s"
        )
        with self.conn.cursor() as cur:
            cur.execute(q, (table,))
            rows = cur.fetchall()

        mapping = {}
        for col, dtype in rows:
            dtype = dtype.upper()
            if "CHAR" in dtype or "TEXT" in dtype:
                mapping[col] = "TEXT"
            elif "INT" in dtype:
                mapping[col] = "INTEGER"
            elif "REAL" in dtype or "DOUBLE" in dtype or "NUMERIC" in dtype or "DECIMAL" in dtype:
                mapping[col] = "REAL"
            elif "DATE" in dtype or "TIMESTAMP" in dtype:
                mapping[col] = "DATE"
            else:
                mapping[col] = dtype

        return mapping

    def insert_rows(self, table: str, rows: List[Dict[str, Any]], columns: List[str]) -> int:
        if not rows:
            return 0
        if not self.conn:
            raise RuntimeError("Not connected")

        # update default table to the one inserted into
        self._table_default = table

        cols_sql = ", ".join(f'"{c}"' for c in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders})'

        values = [tuple(row.get(c) for c in columns) for row in rows]
        with self.conn.cursor() as cur:
            cur.executemany(insert_sql, values)
            return cur.rowcount or len(rows)

    def _build_where(self, date_field: Optional[str], date_from: Optional[date], date_to: Optional[date], conditions: Optional[Dict[str, Dict[str, Any]]]):
        clauses = []
        params = []

        if date_field and date_from:
            clauses.append(f'"{date_field}" >= %s')
            params.append(str(date_from))
        if date_field and date_to:
            clauses.append(f'"{date_field}" <= %s')
            params.append(str(date_to))

        if conditions:
            for col, ops in conditions.items():
                for op, val in ops.items():
                    col_quoted = f'"{col}"'
                    if op == "eq":
                        clauses.append(f"{col_quoted} = %s")
                    elif op == "ne":
                        clauses.append(f"{col_quoted} != %s")
                    elif op == "gt":
                        clauses.append(f"{col_quoted} > %s")
                    elif op == "gte":
                        clauses.append(f"{col_quoted} >= %s")
                    elif op == "lt":
                        clauses.append(f"{col_quoted} < %s")
                    elif op == "lte":
                        clauses.append(f"{col_quoted} <= %s")
                    else:
                        raise ValueError(f"Unsupported operator: {op}")
                    params.append(val)

        return clauses, params

    def query(self, *, date_from: Optional[date] = None, date_to: Optional[date] = None, conditions: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        # default uses DATE column named 'date' or 'DATE'
        date_field = None
        # try to detect a date-like column
        try:
            schema = self.get_schema(self._table_default)
            for k, t in schema.items():
                if t == "DATE":
                    date_field = k
                    break
        except Exception:
            date_field = None

        clauses, params = self._build_where(date_field, date_from, date_to, conditions)
        sql_q = f'SELECT * FROM "{self._table_default}"'
        if clauses:
            sql_q += " WHERE " + " AND ".join(clauses)

        with self.conn.cursor() as cur:
            cur.execute(sql_q, tuple(params))
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def query_for_trend(self, *, date_field: str, date_from: Optional[date] = None, date_to: Optional[date] = None, conditions: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        if not self.conn:
            raise RuntimeError("Not connected")

        clauses, params = self._build_where(date_field, date_from, date_to, conditions)

        sql_q = f'SELECT * FROM "{self._table_default}"'
        if clauses:
            sql_q += " WHERE " + " AND ".join(clauses)

        with self.conn.cursor() as cur:
            cur.execute(sql_q, tuple(params))
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def delete_where(self, table: str, where: Dict[str, Any]) -> int:
        if not where:
            raise ValueError("Delete without WHERE is not allowed")
        if not self.conn:
            raise RuntimeError("Not connected")

        where_clause = " AND ".join(f'"{k}" = %s' for k in where)
        params = tuple(where.values())
        sql_q = f'DELETE FROM "{table}" WHERE {where_clause}'
        with self.conn.cursor() as cur:
            cur.execute(sql_q, params)
            return cur.rowcount
