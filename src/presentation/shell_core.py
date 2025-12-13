import cmd
from src.presentation.visualization import (
    summarize_database,
    preview_head,
    filter_by_fields,
    filter_by_date,
    groupby_fields,
    plot_time_series,
)
from src.service.data_storage import DataStorageService

def _coerce_value(s: str):
    """Try to convert numeric strings to int/float, otherwise return the original string."""
    # try int
    try:
        return int(s)
    except ValueError:
        pass
    # try float
    try:
        return float(s)
    except ValueError:
        pass
    # strip quotes if present
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        return s[1:-1]
    return s


class DataShell(cmd.Cmd):
    intro = "Welcome to Data Insights Shell. Type help or ? to list commands."
    prompt = "DataShell> "

    def __init__(self):
        super().__init__()
        self.conn = None
        self.db_path = None
        
    def onecmd(self, line):
        """Override onecmd so that exceptions don't kill the shell."""
        try:
            return super().onecmd(line)
        except Exception as e:
            print(f"[ERROR] Command failed: {e}")
            return False
            
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
        """Filter fields. Example: filter age=30 city=London"""
        if not self.conn:
            raise Exception("Not connected.")

        filters = {}
        parts = args.split()
        if not parts:
            raise ValueError("Usage: filter <field>=<value> [<field>=<value> ...]")

        for p in parts:
            if "=" not in p:
                raise ValueError(f"Invalid filter expression '{p}'. Use field=value only.")

            k, v = p.split("=", 1)
            k = k.strip()
            v = v.strip()

            if not k:
                raise ValueError(f"Invalid field name in expression '{p}'")

            filters[k] = _coerce_value(v)

        try:
            result = filter_by_fields(self.conn, filters)
            preview_head(result)
            summarize_database(result)
        except Exception as e:
            print(f"[INFO] {e}")

    # -------------------------------------
    # filter_date <datefield> <start> <end>
    # -------------------------------------
    def do_filter_date(self, args):
        """Filter by date.
        Examples:
        filter_date DATE 2020-01-01
        filter_date DATE 2020-01-01 2020-12-31
        """
        if not self.conn:
            print("[ERROR] Not connected.")
            return

        parts = args.split()

        if len(parts) not in (2, 3):
            print("Usage: filter_date <date_field> <start> [end]")
            return

        date_field = parts[0]
        start = parts[1]
        end = parts[2] if len(parts) == 3 else None

        result = filter_by_date(self.conn, date_field, start, end)
        summarize_database(result)

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

        result = groupby_fields(self.conn, group_fields, agg_map)

        summarize_database(result)
        preview_head(result)

    # -------------------------------------
    # trend <metric>
    # -------------------------------------
    def do_trend(self, args):
        """Plot time-series trend. Example: trend price"""
        if not self.conn:
            print("[ERROR] Not connected.")
            return
        
        parts = args.split()
        if len(parts) != 2:
            print("Usage: trend <date_field> <metric_field>")
            return

        date_field, metric = parts

        plot_time_series(self.conn, date_field, metric)

    # -------------------------------------
    # exit / quit
    # -------------------------------------
    def do_exit(self, _):
        """Exit shell."""
        print("Bye.")
        return True

    def do_quit(self, _):
        return self.do_exit(_)
