# src/repository/sqlite_repository.py
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import date
from src.interface.repository_interface import IRepository


class SQLiteRepository(IRepository):

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.TABLE = "records"

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    # ========== helper ==========
    def _quote(self, identifier: str) -> str:
        return f'"{identifier}"'

    # ========== transaction ==========
    
    def begin(self):
        self.conn.execute("BEGIN")

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    # ========== Schema ==========

    def table_exists(self, table: str) -> bool:
        cur = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        return cur.fetchone() is not None

    def get_schema(self, table: str) -> Dict[str, str]:
        cur = self.conn.execute(f'PRAGMA table_info("{table}")')
        return {row[1]: row[2].upper() for row in cur.fetchall()}

    def ensure_table(self, table: str, schema: Dict[str, str]):
        cols = ", ".join(
            f'"{col}" {dtype}'
            for col, dtype in schema.items()
        )
        sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({cols})'
        self.conn.execute(sql)

    # ========== Create ==========

    def insert_rows(
        self,
        table: str,
        rows: List[Dict[str, Any]],
        columns: List[str],
    ) -> int:
        if not rows:
            return 0

        col_sql = ", ".join(f'"{c}"' for c in columns)
        placeholders = ", ".join("?" for _ in columns)

        sql = f'''
        INSERT INTO "{table}" ({col_sql})
        VALUES ({placeholders})
        '''

        values = [
            tuple(row.get(c) for c in columns)
            for row in rows
        ]

        cur = self.conn.executemany(sql, values)
        return cur.rowcount

    # ========== Read ==========

    def fetch_all(self, table: str) -> List[Dict[str, Any]]:
        cur = self.conn.execute(f'SELECT * FROM "{table}"')
        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, row))
            for row in cur.fetchall()
        ]

    def fetch_where(
        self,
        table: str,
        where: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if not where:
            return self.fetch_all(table)

        conditions = " AND ".join(f'"{k}" = ?' for k in where)
        sql = f'SELECT * FROM "{table}" WHERE {conditions}'
        values = tuple(where.values())

        cur = self.conn.execute(sql, values)
        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, row))
            for row in cur.fetchall()
        ]

    # ========== Update ==========

    def update_where(
        self,
        table: str,
        values: Dict[str, Any],
        where: Dict[str, Any],
    ) -> int:
        if not values:
            return 0

        set_clause = ", ".join(f'"{k}" = ?' for k in values)
        where_clause = " AND ".join(f'"{k}" = ?' for k in where)

        sql = f'''
        UPDATE "{table}"
        SET {set_clause}
        WHERE {where_clause}
        '''

        params = tuple(values.values()) + tuple(where.values())
        cur = self.conn.execute(sql, params)
        return cur.rowcount

    # ========== Delete ==========

    def delete_where(
        self,
        table: str,
        where: Dict[str, Any],
    ) -> int:
        if not where:
            raise ValueError("Delete without WHERE is not allowed")

        where_clause = " AND ".join(f'"{k}" = ?' for k in where)
        sql = f'DELETE FROM "{table}" WHERE {where_clause}'
        params = tuple(where.values())

        cur = self.conn.execute(sql, params)
        return cur.rowcount
    
    # ======== query ===========
    def query(
        self,
        *,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        conditions: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:

        sql = f"SELECT * FROM {self.TABLE}"
        where_clauses = []
        params = []

        if date_from:
            where_clauses.append("DATE >= ?")
            params.append(str(date_from))

        if date_to:
            where_clauses.append("DATE <= ?")
            params.append(str(date_to))

        if conditions:
            for col, ops in conditions.items():
                col = self._quote(col)
                for op, val in ops.items():
                    if op == "eq":
                        where_clauses.append(f"{col} = ?")
                    elif op == "ne":
                        where_clauses.append(f"{col} != ?")
                    elif op == "gt":
                        where_clauses.append(f"{col} > ?")
                    elif op == "gte":
                        where_clauses.append(f"{col} >= ?")
                    elif op == "lt":
                        where_clauses.append(f"{col} < ?")
                    elif op == "lte":
                        where_clauses.append(f"{col} <= ?")
                    else:
                        raise ValueError(f"Unsupported operator: {op}")
                    params.append(val)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        cur = self.conn.cursor()
        cur.execute(sql, params)

        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    
    def query_for_trend(
    self,
    *,
    date_field: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    conditions: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:

        sql = f"SELECT * FROM {self.TABLE}"
        where_clauses = []
        params = []

        if date_from:
            where_clauses.append(f"{date_field} >= ?")
            params.append(str(date_from))

        if date_to:
            where_clauses.append(f"{date_field} <= ?")
            params.append(str(date_to))

        if conditions:
            for col, ops in conditions.items():
                col = self._quote(col)
                for op, val in ops.items():
                    if op == "eq":
                        where_clauses.append(f"{col} = ?")
                    elif op == "ne":
                        where_clauses.append(f"{col} != ?")
                    elif op == "gt":
                        where_clauses.append(f"{col} > ?")
                    elif op == "gte":
                        where_clauses.append(f"{col} >= ?")
                    elif op == "lt":
                        where_clauses.append(f"{col} < ?")
                    elif op == "lte":
                        where_clauses.append(f"{col} <= ?")
                    else:
                        raise ValueError(f"Unsupported operator: {op}")
                    params.append(val)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        cur = self.conn.cursor()
        cur.execute(sql, params)

        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
