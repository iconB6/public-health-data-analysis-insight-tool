from typing import Optional, Dict, Any
from src.interface.repository_interface import IRepository
from src.utils.logger import get_logger
from src.service.filter_service import FilterService
from src.service.summary_service import SummaryService
from src.service.trend_service import TrendService

class AnalyseService:

    def __init__(self, repository: IRepository, visualizer):
        self.logger = get_logger(self.__class__.__name__)

        self.repository = repository
        self.repository.connect()
        self.visualizer = visualizer

        self.filter_service = FilterService(repository)
        self.summary_service = SummaryService(repository)
        self.trend_service = TrendService(repository)

        self._filtered_rows = None
        self._summary_preview = None
        self._trend_data_preview = None
        self._trend_figure_preview = None

    # ---------- Filter + Summary ----------

    def run_filter(self, *, date_from=None, date_to=None, conditions=None):
        """
        Run filter, then immediately compute and preview summary.
        """


        self.logger.info("Running filter")

        self.logger.debug(
            "Filter params: date_from=%s, date_to=%s, conditions=%s",
            date_from, date_to, conditions
        )


        rows = self.filter_service.filter(
            date_from=date_from,
            date_to=date_to,
            conditions=conditions,
        )

        self._filtered_rows = rows

        self.logger.info("Filter completed, %d rows returned", len(rows))
        self.logger.info("Generating summary preview")

        summary = self.summary_service.summarize(rows)

        # overwrite previous preview
        self.logger.debug("Overwriting previous summary preview")
        self._summary_preview = summary

        self.logger.debug(
            "Summary result keys: %s",
            list(summary.keys())
        )


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

        self.logger.info(
            "Running trend: date_field=%s, metric_field=%s, agg=%s",
            date_field, metric_field, agg
        )

        trend_data = self.trend_service.trend_over_time(
            date_field=date_field,
            metric_field=metric_field,
            agg=agg,
            date_from=date_from,
            date_to=date_to,
            conditions=conditions,
        )

        self.logger.info("Trend generated with %d points", len(trend_data["date"]))


        figure = self.visualizer.plot_trend(trend_data)
        self.visualizer.show(figure)

        # only keep latest preview
        self._trend_data_preview = trend_data
        self._trend_figure_preview = figure
        self.logger.debug("Overwriting previous trend preview")

        return trend_data
    
    # ---------- Export ----------

    def export_summary(self, path: str):
        """
        Export the latest summary preview.
        """
        if self._summary_preview is None:
            raise RuntimeError("No summary preview to export.")
        
        self.visualizer.export_table(self._summary_preview, path)
        self.logger.info("Exporting summary to %s", path)


    def export_trend(self, path: str):
        """
        Export the latest trend preview figure.
        """
        if self._trend_figure_preview is None:
            raise RuntimeError("No trend preview to export.")

        self.visualizer.export_figure(self._trend_figure_preview, path)
        self.logger.info("Exporting trend figure to %s", path)

    def close(self):
        self.repository.disconnect()

