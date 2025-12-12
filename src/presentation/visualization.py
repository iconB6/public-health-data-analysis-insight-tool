import pandas as pd
from src.service.data_summarizer import DataSummarizer
from src.service.data_filter import DataFilter

def summarize_database(conn):
    """Backend interface: generate summary information."""
    try:
        records = conn.get_all_records()
        if not records:
            print("[INFO] No records to summarize.")
            return None

        summarizer = DataSummarizer()
        try:
            summary_df = summarizer.summary_stats(records)
        except Exception as e:
            print(f"[ERROR] Failed to generate summary: {e}")
            return None

        # Pretty-print table using pandas formatting options
        with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", 120):
            # Round to two decimals, index as variable name
            formatted = summary_df.round(2).to_string()

        print("\n=== Summary Statistics ===")
        print(formatted)
        print("=== End Summary ===\n")

        return summary_df
    
    except Exception as exc:
        print(f"[ERROR] summarize_database raised an exception: {exc}")
        return None

def preview_head(conn, table_name, n=10):
    """Backend interface: show the first n rows."""
    # Case 1: in-memory list of dicts
    if isinstance(conn, list):
        if len(conn) == 0:
            print("[Empty dataset]")
            return

        df = pd.DataFrame(conn)
        print(df.head(n).to_string(index=False))
        return
    
    # Case 2: SQLite connection
    records = conn.get_all_records()

    if len(records) == 0:
        print("[Empty database: no records in 'records' table]")
        return

    df = pd.DataFrame(records)
    print(df.head(n).to_string(index=False))
    return


def filter_by_fields(conn, table_name, filters: dict):
    """Backend interface: field-based filtering."""
    # obtain records
    records = conn.get_all_records()

    if not records:
        print("[INFO] No records to filter.")
        return []

    # instantiate filter service, pass repository if available for column info
    dfilt = DataFilter(repository=conn if hasattr(conn, "get_columns") else None)

    try:
        result = dfilt.filter_by_fields(records, **filters)
    except Exception as e:
        print(f"[ERROR] filter_by_fields failed: {e}")
        return []

    print(f"[INFO] Filtered rows: {len(result)}")
    preview_head(result, table_name)

    return result

def filter_by_date(conn, table_name, date_field, start_date, end_date):
    """Backend interface: date-range filtering."""
    # obtain records
    records = conn.get_all_records()

    if not records:
        print("[INFO] No records to filter by date.")
        return []

    dfilt = DataFilter(repository=conn if hasattr(conn, "get_columns") else None)

    try:
        result = dfilt.filter_by_date_range(records, date_field=date_field, start_date=start_date, end_date=end_date)
    except Exception as e:
        print(f"[ERROR] filter_by_date failed: {e}")
        return []

    print(f"[INFO] Date-filtered rows: {len(result)}")
    preview_head(result, table_name)

    return result

def groupby_fields(conn, table_name, by_fields, agg_map):
    """Backend interface: groupby aggregation."""
    records = conn.get_all_records()

    if not records:
        print("[INFO] No records to group.")
        return None

    # choose group_field and metric_field
    group_field = by_fields[0] if by_fields else None
    metric_field = None
    if agg_map:
        # take the first metric provided
        metric_field = list(agg_map.keys())[0]

    summarizer = DataSummarizer()

    if not group_field or not metric_field:
        print("[ERROR] group_field or metric_field not specified or inferable.")
        return None

    try:
        grouped = summarizer.group_by(records, group_field, metric_field)
    except Exception as e:
        print(f"[ERROR] groupby failed: {e}")
        return None

    # pretty print
    with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", 120):
        formatted = grouped.round(2).to_string()

    print(f"\n=== Group By ({group_field}) on {metric_field} ===")
    print(formatted)
    print("=== End Group By ===\n")

    return grouped

def plot_time_series(conn, table_name, date_field, metric_field):
    """Backend interface: time-series trend plot using Matplotlib."""
    records = conn.get_all_records()

    if not records:
        print("[INFO] No records to plot.")
        return None

    summarizer = DataSummarizer()
    try:
        trend = summarizer.trend_over_time(records, date_field=date_field, metric_field=metric_field)
    except Exception as e:
        print(f"[ERROR] trend_over_time failed: {e}")
        return None

    df = trend.get("dataframe")
    if df is None or df.empty:
        print("[INFO] No data available for plotting.")
        return None

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df.iloc[:, 0], df.iloc[:, 1], marker="o", linestyle="-")
    ax.set_xlabel(date_field)
    ax.set_ylabel(metric_field)
    ax.set_title(f"Trend: {metric_field} over {date_field}")
    fig.autofmt_xdate()

    out_path = f"trend_{metric_field}.png"
    try:
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        print(f"[INFO] Saved trend plot to {out_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save plot: {e}")
        return None

    return out_path
