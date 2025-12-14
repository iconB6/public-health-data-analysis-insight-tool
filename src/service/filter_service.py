from typing import List, Dict, Any, Optional
import datetime
from src.utils.logger import get_logger
from src.interface.repository_interface import IRepository


class FilterService:

    TEXT_OPS = {"eq", "ne"}
    NUMERIC_OPS = {"eq", "ne", "gt", "gte", "lt", "lte"}

    def __init__(self, repository: IRepository):
        self.logger = get_logger(self.__class__.__name__)
        self._repo = repository
        self._cache: List[Dict[str, Any]] = []

    def filter(
        self,
        *,
        date_from: Optional[datetime.date] = None,
        date_to: Optional[datetime.date] = None,
        conditions: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:

        if date_from and not isinstance(date_from, datetime.date):
            self.logger.error("Invalid date_from type: %s", type(date_from))
            raise TypeError("date_from must be datetime.date")

        if date_to and not isinstance(date_to, datetime.date):
            self.logger.error("Invalid date_to type: %s", type(date_to))
            raise TypeError("date_to must be datetime.date")
        
        self.logger.debug(
            "Calling repository.query with conditions=%s",
            conditions
        )
        schema = self._repo.get_schema("records")

        if conditions:
            for col, ops in conditions.items():
                if col not in schema:
                    raise ValueError(f"Unknown column: {col}")

                col_type = schema[col]
                allowed_ops = (
                    self.TEXT_OPS if col_type == "TEXT" else self.NUMERIC_OPS
                )

                for op in ops:
                    if op not in allowed_ops:
                        raise ValueError(
                            f"Operator '{op}' not allowed for column {col}"
                        )

        result = self._repo.query(
            date_from=date_from,
            date_to=date_to,
            conditions=conditions,
        )

        self._cache = list(result)
        self.logger.info("FilterService returned %d rows", len(result))
        return result

    def get_cached_results(self) -> List[Dict[str, Any]]:
        return list(self._cache)