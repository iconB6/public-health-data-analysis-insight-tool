import cmd
from visualization import (
    summarize_database,
    preview_head,
    filter_by_fields,
    filter_by_date,
    groupby_fields,
    plot_time_series,
)
from src.service.data_storage import DataStorageService


class DataShell(cmd.Cmd):
    intro = "Welcome to Data Insights Shell. Type help or ? to list commands."
    prompt = "DataShell> "

    def __init__(self):
        super().__init__()
        self.conn = None
        self.db_path = None

    # -------------------------------------
    # connect <db_path>
    # -------------------------------------
    def do_connect(self, db_path):
        """Connect to a SQLite database."""
        if not db_path:
            print("Usage: connect <db_path>")
            return

        print(f"[INFO] Connecting to: {db_path}")
        self.conn = DataStorageService(db_path)
        self.conn.connect()
        self.db_path = db_path

        print("[INFO] Summary:")
        summarize_database(self.conn)

        print("[INFO] First 10 rows:")
        preview_head(self.conn)

        print("[DONE] Connected.")

    # -------------------------------------
    # disconnect
    # -------------------------------------
    def do_disconnect(self, _):
        """Disconnect current database."""
        if self.conn:
            self.conn.disconnect()
            self.conn = None
            self.db_path = None
            print("[DONE] Disconnected.")
        else:
            print("[INFO] No active connection.")

    # -------------------------------------
    # summary
    # -------------------------------------
    def do_summary(self, _):
        """Show database summary."""
        if not self.conn:
            print("[ERROR] Not connected.")
            return
        summarize_database(self.conn)

    # -------------------------------------
    # preview
    # -------------------------------------
    def do_preview(self, _):
        """Show first 10 rows."""
        if not self.conn:
            print("[ERROR] Not connected.")
            return
        preview_head(self.conn)

    # -------------------------------------
    # filter <field>=<value> <field2>=<value2>
    # -------------------------------------
    def do_filter(self, args):
        """Filter fields. Example: filter age>30 city=London"""
        if not self.conn:
            print("[ERROR] Not connected.")
            return

        filters = {}
        parts = args.split()
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
            elif ">" in p:
                k, v = p.split(">", 1)
            filters[k] = v

        result = filter_by_fields(self.conn, "records", filters)

        summarize_database(result)
        preview_head(result)

    # -------------------------------------
    # filter_date <datefield> <start> <end>
    # -------------------------------------
    def do_filter_date(self, args):
        """Filter by date. Example: filter_date date 2020-01-01 2020-12-31"""
        if not self.conn:
            print("[ERROR] Not connected.")
            return

        parts = args.split()
        if len(parts) != 3:
            print("Usage: filter_date <date_field> <start> <end>")
            return

        date_field, start, end = parts
        result = filter_by_date(self.conn, "records", date_field, start, end)

        summarize_database(result)
        preview_head(result)

    # -------------------------------------
    # groupby <field1> <field2> agg=mean
    # -------------------------------------
    def do_groupby(self, args):
        """Group by fields. Example: groupby city agg=mean"""
        if not self.conn:
            print("[ERROR] Not connected.")
            return

        parts = args.split()
        group_fields = []
        agg_map = {}

        for p in parts:
            if "=" in p:
                k, v = p.split("=")
                agg_map[k] = v
            else:
                group_fields.append(p)

        result = groupby_fields(self.conn, "records", group_fields, agg_map)

        summarize_database(result)
        preview_head(result)

    # -------------------------------------
    # trend <metric>
    # -------------------------------------
    def do_trend(self, metric):
        """Plot time-series trend. Example: trend price"""
        if not self.conn:
            print("[ERROR] Not connected.")
            return

        if not metric:
            print("Usage: trend <metric_field>")
            return

        plot_time_series(self.conn, "records", "date", metric)

    # -------------------------------------
    # exit / quit
    # -------------------------------------
    def do_exit(self, _):
        """Exit shell."""
        print("Bye.")
        return True

    def do_quit(self, _):
        return self.do_exit(_)
