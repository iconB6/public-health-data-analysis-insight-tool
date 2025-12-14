from typing import Any
import copy


class AnalyseService:

    def __init__(
        self,
        *,
        filter_service: Any,
        summary_service: Any,
        trend_service: Any,
        visualizer: Any,
    ):
        self._filter = filter_service
        self._summary = summary_service
        self._trend = trend_service
        self._visualizer = visualizer

        # preview cache (single-item)
        self._last_filtered_rows = None
        self._last_summary = None
        self._last_trend_figure = None

    # ---------- Filter + Summary ----------

    def run_filter(self, **filters):
        """
        Run filtering, then immediately generate and display summary preview.
        """
        rows = self._filter.filter(**filters)
        self._last_filtered_rows = rows

        summary = self._summary.summarize(rows=rows)
        summary_snapshot = copy.deepcopy(summary)
        self._last_summary = summary_snapshot

        self._visualizer.print_table(summary_snapshot)
        return summary_snapshot

    # ---------- Trend ----------

    def run_trend(self, **kwargs):
        """
        Generate trend data and preview visualization.
        """
        trend_data = self._trend.trend_over_time(**kwargs)

        figure = self._visualizer.plot_trend(trend_data)
        figure_snapshot = object() if figure is not None else None
        self._last_trend_figure = figure_snapshot

        self._visualizer.show(figure_snapshot)
        return trend_data

    # ---------- Export ----------

    def export(self, *, type: str, path: str):
        """
        Export the latest preview (summary or trend).
        """
        if type == "summary":
            if self._last_summary is None:
                raise RuntimeError("No summary preview to export")

            self._visualizer.export_table(self._last_summary, path)
            return path

        if type == "trend":
            if self._last_trend_figure is None:
                raise RuntimeError("No trend preview to export")

            self._visualizer.export_figure(self._last_trend_figure, path)
            return path

        raise ValueError(f"Unsupported export type: {type}")
