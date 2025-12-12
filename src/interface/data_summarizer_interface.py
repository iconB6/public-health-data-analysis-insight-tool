from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class IDataSummarizer(ABC):
    """
    Abstract base class for summarizing tabular data.
    """

    @abstractmethod
    def summary_stats(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Compute summary statistics for all numeric columns.
        Returns a pandas DataFrame.
        """
        pass

    @abstractmethod
    def trend_over_time(
        self,
        records: List[Dict[str, Any]],
        date_field: str,
        metric_field: str
    ):
        """
        Compute and visualize trend of a numeric field over time.
        Should return a DataFrame of date + metric, and *may* show a plot.
        """
        pass

    @abstractmethod
    def group_by(
        self,
        records: List[Dict[str, Any]],
        group_field: str,
        metric_field: str
    ) -> pd.DataFrame:
        """
        Group records by a categorical field and compute statistical summaries
        (count, mean, min, max). Returns a DataFrame.
        """
        pass
