from typing import Optional, Dict, Any


class AnalyseService:

    def __init__(
        self,
        *,
        filter_service,
        summary_service,
        trend_service,
        visualizer,
    ):
        self.filter_service = filter_service
        self.summary_service = summary_service
        self.trend_service = trend_service
        self.visualizer = visualizer

        # preview cache (only keep latest)
        self._filtered_rows: Optional[list] = None
        self._summary_preview: Optional[dict] = None
        self._trend_data_preview: Optional[dict] = None
        self._trend_figure_preview: Optional[Any] = None

    # ---------- Filter + Summary ----------

    def run_filter(self, *, date_from=None, date_to=None, conditions=None):
        """
        Run filter, then immediately compute and preview summary.
        """
        rows = self.filter_service.filter(
            date_from=date_from,
            date_to=date_to,
            conditions=conditions,
        )

        self._filtered_rows = rows

        summary = self.summary_service.summarize(rows)

        # overwrite previous preview
        self._summary_preview = summary

        # preview immediately
        self.visualizer.print_table(summary)

        return rows

    # ---------- Trend ----------
    def run_trend(
    self,
    *,
    date_field: str,
    metric_field: str,
    agg: str = "count",
    date_from=None,
    date_to=None,
    conditions=None
):
        """
        Generate trend data and preview trend figure.
        Can run on full table or filtered subset.
        """

        trend_data = self.trend_service.trend_over_time(
            date_field=date_field,
            metric_field=metric_field,
            agg=agg,
            date_from=date_from,
            date_to=date_to,
            conditions=conditions,
        )

        figure = self.visualizer.plot_trend(trend_data)
        self.visualizer.show(figure)

        # only keep latest preview
        self._trend_data_preview = trend_data
        self._trend_figure_preview = figure

        return trend_data
    
    # ---------- Export ----------

    def export_summary(self, path: str):
        """
        Export the latest summary preview.
        """
        if self._summary_preview is None:
            raise RuntimeError("No summary preview to export.")

        self.visualizer.export_table(self._summary_preview, path)

    def export_trend(self, path: str):
        """
        Export the latest trend preview figure.
        """
        if self._trend_figure_preview is None:
            raise RuntimeError("No trend preview to export.")

        self.visualizer.export_figure(self._trend_figure_preview, path)
