from typing import Dict, Any
import csv
import matplotlib.pyplot as plt
from tabulate import tabulate


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

        for key, value in summary.items():
            if isinstance(value, dict):
                for sub_k, sub_v in value.items():
                    rows.append([f"{key}.{sub_k}", sub_v])
            else:
                rows.append([key, value])

        print(tabulate(rows, headers=["Metric", "Value"], tablefmt="grid"))

    def export_table(self, summary: Dict[str, Any], path: str):
        """
        Export summary as CSV.
        """
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])

            for key, value in summary.items():
                if isinstance(value, dict):
                    for sub_k, sub_v in value.items():
                        writer.writerow([f"{key}.{sub_k}", sub_v])
                else:
                    writer.writerow([key, value])

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
        figure.savefig(path, bbox_inches="tight")
