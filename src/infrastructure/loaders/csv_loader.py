import csv
from typing import List, Dict, Any
from src.interface.data_loader_interface import IDataLoader

class CSVLoader(IDataLoader):
    """
    CSV implementation of data loader.
    """
    def __init__(self, source: str):
        """
        Store the CSV file path.
        """
        if not source:
            raise ValueError("CSV file path is required")
        if not source.lower().endswith(".csv"):
            raise ValueError("Not a CSV file")
        
        self.source = source

    def load(self) -> List[Dict[str, Any]]:
        """
        Load CSV file into a list of row dictionaries.
        """
        try:
            with open(self.source, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except FileNotFoundError:
            raise ValueError(f"CSV file not found: {self.source}")

        # Empty CSV (no header)
        if reader.fieldnames is None:
            raise ValueError("CSV contains no header")

        # header but no data
        if len(rows) == 0:
            raise ValueError("CSV contains only header, no records")
        
        result = []
        for row in rows:
            # normalize missing cells to empty string
            result.append({
                k: ("" if v is None else v)
                for k, v in row.items()
            })

        return result
        