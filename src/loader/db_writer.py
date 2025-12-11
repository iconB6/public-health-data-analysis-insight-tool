import sqlite3

class DBWriter:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path

    def init_schema(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_source TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS record_dimensions (
            record_id INTEGER,
            key TEXT,
            value TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS record_metrics (
            record_id INTEGER,
            metric_name TEXT,
            metric_value REAL
        );
        """)

        conn.commit()
        conn.close()

    def write(self, df, dimension_fields, metric_fields):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        for _, row in df.iterrows():
            # insert record
            cur.execute("INSERT INTO records (data_source) VALUES (?)", ("csv",))
            record_id = cur.lastrowid

            # write dimensions
            for dim in dimension_fields:
                cur.execute(
                    "INSERT INTO record_dimensions (record_id, key, value) VALUES (?, ?, ?)",
                    (record_id, dim, str(row[dim]))
                )

            # write metrics
            for metric in metric_fields:
                value = float(row[metric])
                cur.execute(
                    "INSERT INTO record_metrics (record_id, metric_name, metric_value) VALUES (?, ?, ?)",
                    (record_id, metric, value)
                )

        conn.commit()
        conn.close()
