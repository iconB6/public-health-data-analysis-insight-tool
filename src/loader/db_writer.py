import sqlite3


class DBWriter:
    def __init__(self, db_path):
        self.db_path = db_path

    def save(self, df, table_name="data"):
        conn = sqlite3.connect(self.db_path)
        try:
            # Use pandas if available for convenience
            try:
                df.to_sql(table_name, conn, if_exists="replace", index=False)
            except Exception:
                # fallback: create table and insert rows
                raise
        finally:
            conn.close()