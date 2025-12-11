import pandas as pd


class CSVLoader:
    def __init__(self, path=None):
        self.path = path

    def load(self):
        if not self.path:
            raise ValueError("No path specified for CSVLoader")
        df = pd.read_csv(self.path)
        return df

    def get_indicators(self, df):
        base = {"country", "year", "group", "date"}
        return [c for c in df.columns if c not in base]