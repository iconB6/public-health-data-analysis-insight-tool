from abc import ABC, abstractmethod
import pandas as pd

class BaseLoader(ABC):
    """
    Abstract base class for all data loaders.
    Defines the common workflow:
    1. load raw data
    2. validate data
    3. detect dimension + metric fields
    """

    @abstractmethod
    def load(self, source) -> pd.DataFrame:
        """
        Load raw data from the source (CSV / JSON / API / DB).
        Must return a pandas DataFrame.
        """
        pass

    def validate(self, df: pd.DataFrame):
        """
        Optional validation logic (date format / required columns / etc).
        Subclasses can override.
        Default: ensure DataFrame is not empty.
        """
        if df is None:
            raise ValueError("Loaded DataFrame is None")

        if df.empty:
            raise ValueError("Loaded DataFrame contains no rows")

        if df.shape[1] == 0:
            raise ValueError("Loaded DataFrame contains no columns")
        
    def detect_fields(self, df: pd.DataFrame):
        """
        Automatically detect dimension fields and metric fields:
          - metrics  : float columns (must contain numeric values)
          - dimensions: everything else (string, int, categorical)
        Requires at least:
          - 1 dimension field
          - 1 metric field
        """
        dimension_fields = []
        metric_fields = []

        for col in df.columns:
            series = df[col]

            # Metric detection: float columns or numeric-convertible columns
            if pd.api.types.is_float_dtype(series):
                # verify content is numeric
                try:
                    pd.to_numeric(series, errors="raise")
                except Exception:
                    raise ValueError(f"Invalid numeric value in metric column: {col}")

                metric_fields.append(col)
            elif pd.api.types.is_integer_dtype(series):
                dimension_fields.append(col)
            else:
                dimension_fields.append(col)

        if len(metric_fields) == 0:
            raise ValueError("No metric fields detected")

        if len(dimension_fields) == 0:
            raise ValueError("No dimension fields detected")

        return dimension_fields, metric_fields
    
    def run(self):
        """
        High-level execution pipeline:
        1. load()
        2. validate()
        3. detect_fields()
        Returns: (df, dimensions, metrics)
        """
        df = self.load()
        self.validate(df)
        dimensions, metrics = self.detect_fields(df)
        return df, dimensions, metrics
