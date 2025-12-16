from typing import Dict, Any
import csv
import matplotlib.pyplot as plt
from tabulate import tabulate
from pathlib import Path
import os



class Visualizer:
    """
    Presentation layer.
    Responsible only for displaying and exporting results.
    No business logic.
    """

    # ---------- Summary ----------

    def print_table(self, summary: Dict[str, Any]):
        """
        Print summary preview table to console.
        """
        rows = []

        # ---------- meta ----------
        meta = summary.get("meta", {})
        if "total_records" in meta:
            rows.append(["Total records", meta["total_records"]])

        # ---------- numeric ----------
        numeric = summary.get("numeric", {})
        for field, stats in numeric.items():
            rows.append([f"{field}.min", stats.get("min")])
            rows.append([f"{field}.max", stats.get("max")])
            rows.append([f"{field}.mean", stats.get("mean")])

        # ---------- categorical (preview only) ----------
        categorical = summary.get("categorical", {})
        for field, items in categorical.items():
            rows.append([f"{field}.distinct", len(items)])

        print(tabulate(rows, headers=["Metric", "Value"], tablefmt="simple"))

    def export_table(self, summary: Dict[str, Any], path: str):
        """
        Export summary as CSV.
        """
        # ensure .csv suffix
        path = Path(path)
        if path.suffix == "":
            path = path.with_suffix(".csv")

        # ensure directory exists
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["section", "field", "metric", "value"])

            # ---------- meta ----------
            meta = summary.get("meta", {})
            for k, v in meta.items():
                writer.writerow(["meta", "", k, v])

            # ---------- numeric ----------
            numeric = summary.get("numeric", {})
            for field, stats in numeric.items():
                for metric, value in stats.items():
                    writer.writerow(["numeric", field, metric, value])

            # ---------- categorical ----------
            categorical = summary.get("categorical", {})
            for field, items in categorical.items():
                for item in items:
                    writer.writerow([
                        "categorical",
                        field,
                        item["value"],
                        item["count"],
                    ])

    # ---------- Trend ----------

    def plot_trend(self, trend_data: Dict[str, Any]):
        """
        Generate a matplotlib Figure for trend preview.
        Returns the figure (does NOT show it).
        """
        dates = trend_data["date"]
        values = trend_data["value"]
        metric = trend_data.get("metric_field", "value")

        fig, ax = plt.subplots()
        ax.plot(dates, values, marker="o")
        ax.set_xlabel("Date")
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} over time")

        fig.autofmt_xdate()
        return fig

    def show(self, figure):
        """
        Show figure preview (CLI / desktop).
        """
        figure.show()

    def export_figure(self, figure, path: str):
        """
        Export figure to file (png / pdf / etc).
        """
        if not path.lower().endswith(".png"):
            path += ".png"

        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        figure.savefig(path, bbox_inches="tight")
