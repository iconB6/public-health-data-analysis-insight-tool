import click
import pandas as pd

# ==============================
#   Backend Interface Placeholders (for future implementation)
# ==============================

def import_data_from_source(source_type, source_path, db_name):
    """Backend interface: import -> clean -> store into SQLite."""
    pass

def connect_to_database(db_path):
    """Backend interface: connect to SQLite or future cloud DB."""
    pass

def disconnect_database():
    """Backend interface: disconnect current database connection."""
    pass

def summarize_database(conn):
    """Backend interface: generate summary information."""
    pass

def preview_head(conn, table_name, n=10):
    """Backend interface: show the first n rows."""
    pass

def filter_by_fields(conn, table_name, filters: dict):
    """Backend interface: field-based filtering."""
    pass

def filter_by_date(conn, table_name, date_field, start_date, end_date):
    """Backend interface: date-range filtering."""
    pass

def groupby_fields(conn, table_name, by_fields, agg_map):
    """Backend interface: groupby aggregation."""
    pass

def plot_time_series(conn, table_name, date_field, metric_field):
    """Backend interface: time-series trend plot using Matplotlib."""
    pass


# Store current DB connection
CURRENT_CONN = {"conn": None, "db_path": None}


# ==========================================
#                CLI Commands
# ==========================================

@click.group()
def cli():
    """Main CLI group for Data Insights Tool."""
    pass


# ------------------------------------------
# 1. Import data
# ------------------------------------------
@cli.command()
@click.option("--source-type", type=click.Choice(["csv", "json", "api", "db"]), required=True)
@click.option("--source-path", required=True, help="File path or connection string")
@click.option("--db-name", required=False, help="Database name (auto-generated if omitted)")
def import_data(source_type, source_path, db_name):
    """
    Import data from a source, clean it, and store into SQLite.
    """
    click.echo(f"[INFO] Importing data from {source_type}: {source_path}")
    import_data_from_source(source_type, source_path, db_name)
    click.echo("[DONE] Data import completed.")


# ------------------------------------------
# 2. Connect to a database
# ------------------------------------------
@cli.command()
@click.option("--db-path", required=True, help="SQLite database file path")
def connect(db_path):
    """
    Connect to a database and automatically show summary and first 10 rows.
    """
    click.echo(f"[INFO] Connecting to: {db_path}")
    conn = connect_to_database(db_path)
    CURRENT_CONN["conn"] = conn
    CURRENT_CONN["db_path"] = db_path

    click.echo("[INFO] Summary:")
    summarize_database(conn)

    click.echo("[INFO] First 10 rows:")
    preview_head(conn, table_name=None)

    click.echo("[DONE] Database connected.")


# ------------------------------------------
# 3. Field filtering
# ------------------------------------------
@cli.command()
@click.option("--table", required=True, help="Table name")
@click.option("--filters", multiple=True, help="Field filters, e.g. --filters age>30 --filters city=London")
def filter_fields(table, filters):
    """
    Filter table by specific fields.
    """
    if not CURRENT_CONN["conn"]:
        click.echo("[ERROR] No database connected.")
        return

    filter_dict = {}
    for item in filters:
        k, v = item.split("=", 1) if "=" in item else item.split(">", 1)
        filter_dict[k] = v

    result = filter_by_fields(CURRENT_CONN["conn"], table, filter_dict)

    click.echo("[INFO] Summary:")
    summarize_database(result)

    click.echo("[INFO] First 10 rows:")
    preview_head(result, table)

    click.echo("[DONE] Field filtering completed.")


# ------------------------------------------
# 4. Date-range filtering
# ------------------------------------------
@cli.command()
@click.option("--table", required=True)
@click.option("--date-field", required=True)
@click.option("--start-date", required=True)
@click.option("--end-date", required=True)
def filter_date(table, date_field, start_date, end_date):
    """
    Filter table by date range.
    """
    if not CURRENT_CONN["conn"]:
        click.echo("[ERROR] No database connected.")
        return

    result = filter_by_date(
        CURRENT_CONN["conn"], table, date_field, start_date, end_date
    )

    click.echo("[INFO] Summary:")
    summarize_database(result)

    click.echo("[INFO] First 10 rows:")
    preview_head(result, table)

    click.echo("[DONE] Date filtering completed.")


# ------------------------------------------
# 5. GroupBy functionality
# ------------------------------------------
@cli.command()
@click.option("--table", required=True)
@click.option("--groupby", required=True, multiple=True, help="Group-by fields")
@click.option("--agg", required=True, multiple=True, help="Aggregation rules, e.g. --agg age=mean")
def groupby(table, groupby, agg):
    """
    Perform group-by aggregation.
    """
    if not CURRENT_CONN["conn"]:
        click.echo("[ERROR] No database connected.")
        return

    agg_map = {}
    for a in agg:
        key, func = a.split("=")
        agg_map[key] = func

    result = groupby_fields(CURRENT_CONN["conn"], table, groupby, agg_map)

    click.echo("[INFO] Summary:")
    summarize_database(result)

    click.echo("[INFO] First 10 rows:")
    preview_head(result, table)

    click.echo("[DONE] Group-by completed.")


# ------------------------------------------
# 6. Time-series trend plot
# ------------------------------------------
@cli.command()
@click.option("--table", required=True)
@click.option("--date-field", required=True)
@click.option("--metric-field", required=True)
def trend(table, date_field, metric_field):
    """
    Plot a metric's trend over time.
    """
    if not CURRENT_CONN["conn"]:
        click.echo("[ERROR] No database connected.")
        return

    click.echo(f"[INFO] Plotting time-series for {metric_field}...")
    plot_time_series(CURRENT_CONN["conn"], table, date_field, metric_field)

    click.echo("[DONE] Plot generated.")


# ------------------------------------------
# 7. Disconnect database
# ------------------------------------------
@cli.command()
def disconnect():
    """
    Disconnect from the current database.
    """
    if CURRENT_CONN["conn"]:
        disconnect_database()
        CURRENT_CONN["conn"] = None
        CURRENT_CONN["db_path"] = None
        click.echo("[DONE] Database disconnected.")
    else:
        click.echo("[INFO] No active connection.")


# ==========================================
# Entry point
# ==========================================
if __name__ == "__main__":
    cli()
