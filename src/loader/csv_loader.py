import pandas as pd
import os
from src.loader.base_loader import BaseLoader

class CSVLoader(BaseLoader):
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.filepath)
        except Exception as e:
            raise ValueError(f"Failed to read CSV: {e}")
        finally:
            if not os.path.exists(self.filepath):
                raise FileNotFoundError(f"CSV file not found: {self.filepath}")