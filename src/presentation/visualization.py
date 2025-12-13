import pandas as pd
from src.service.data_summarizer import DataSummarizer
from src.service.data_filter import DataFilter
from tabulate import tabulate

TOP_K = 5  # show top 5 categories per field
BLUE = "\033[34m"
RESET = "\033[0m"

def blue(text: str) -> str:
    return f"{BLUE}{text}{RESET}"


def summarize_database(conn):
    """Backend interface: generate summary information."""
    # obtain records
    try:
        if isinstance(conn, list):
            if len(conn) == 0:
                print("[Empty dataset]")
                return
            records = conn
        else:
            records = conn.get_all_records()
        if not records:
            print("[INFO] No records to summarize.")
            return None
        
        # instantiate summarizer
        summarizer = DataSummarizer()
        try:
            stats = summarizer.summary_stats(records)
        except Exception as e:
            print(f"[ERROR] Failed to generate summary: {e}")
            return None
        
        record_count = stats.get("record_count")
        numeric_summary = stats.get("numeric_summary")
        categorical_summary = stats.get("categorical_summary")

        # display summary
        print("\n=== Dataset Overview ===")
        print(f"Total record_id count: {record_count}")

        # ---------- numeric ----------
        if numeric_summary is not None and not numeric_summary.empty:
            print("\n=== Numeric Fields Summary ===")
            df = numeric_summary.round(2).reset_index()
            df.rename(columns={"index": "FIELD"}, inplace=True)
            df["FIELD"] = df["FIELD"].apply(lambda x: f"{BLUE}{x}{RESET}")
            print(
                tabulate(
                    df,
                    headers="keys",
                    tablefmt="grid",
                    showindex=False,
                    colalign=("center",) + ("right",) * (len(df.columns) - 1)
                )
            )
        else:
            print("\n[INFO] No numeric fields to summarize.")
        
        # ---------- categorical ----------
        if categorical_summary:
            rows = []

            for field, df in categorical_summary.items():
                if df.empty:
                    continue

                # assume df has columns: [value, count]
                items = [
                    f"{row.iloc[0]}:{row.iloc[1]}"
                    for _, row in df.head(TOP_K).iterrows()
                ]
                summary_str = " | ".join(items)

                if len(df) > TOP_K:
                    summary_str += " | ..."

                rows.append({
                    "FIELD": blue(field),
                    "TOP_CATEGORIES": summary_str
                })

            if rows:
                print("\n=== Categorical Fields Summary ===")
                print(
                    tabulate(
                        rows,
                        headers= "keys",
                        tablefmt="grid",
                        colalign=("center", "center")
                    )
                )
            else:
                print("\n[INFO] No categorical fields to summarize.")
        else:
            print("\n[INFO] No categorical fields to summarize.")
        print("\n=== End Summary ===\n")

        return stats
    
    except Exception as exc:
        print(f"[ERROR] summarize_database raised an exception: {exc}")
        return None

def preview_head(conn, n=10):
    """Backend interface: show the first n rows."""
    if isinstance(conn, list):
        if not conn:
            raise ValueError("Empty dataset: no records to preview.")

        df = pd.DataFrame(conn)
        print(df.head(n).to_string(index=False))
        return
    
    if conn is None:
        raise ValueError("No data source provided.")

    if not hasattr(conn, "get_all_records"):
        raise TypeError(
            f"Invalid data source type: {type(conn).__name__}"
        )

    records = conn.get_all_records()

    if not records:
        raise ValueError("Empty dataset: database contains no records.")

    df = pd.DataFrame(records)
    print(df.head(n).to_string(index=False))


def filter_by_fields(conn, filters: dict):
    """Backend interface: field-based filtering."""
    # obtain records
    if conn is None:
        raise ValueError("No data source provided.")

    if not hasattr(conn, "get_all_records"):
        raise TypeError(
            f"Invalid data source type: {type(conn).__name__}"
        )
    records = conn.get_all_records()

    if not records:
        raise Exception("No records to filter.")

    # instantiate filter service, pass repository if available for column info
    dfilt = DataFilter(repository=conn if hasattr(conn, "get_columns") else None)

    try:
        result = dfilt.filter_by_fields(records, **filters)
    except Exception as e:
        raise Exception(f"filter_by_fields failed: {e}")

    if not result:
        raise ValueError("No records matched the given filters.")

    return result

def filter_by_date(conn, date_field, start_date, end_date = None):
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
    preview_head(result)

    return result

def groupby_fields(conn, by_fields, agg_map):
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

def plot_time_series(conn, date_field, metric_field):
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
