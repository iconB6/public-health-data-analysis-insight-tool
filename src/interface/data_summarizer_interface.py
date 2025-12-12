from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDataSummarizer(ABC):

    @abstractmethod
    def summary_stats(self, records: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def trend_over_time(self, records: List[Dict[str, Any]], date_key: str, metric: str):
        pass

    @abstractmethod
    def group_by(self, records: List[Dict[str, Any]], group_key: str, metric: str):
        pass
