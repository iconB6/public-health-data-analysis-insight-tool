from src.interface.data_loader_interface import IDataLoader
from src.infrastructure.csv_loader import CSVLoader
# from src.infrastructure.json_loader import JSONLoader   # future extension
# from src.infrastructure.api_loader import APILoader     # future extension
# from src.infrastructure.db_loader import DBLoader       # future extension


class DataLoaderFactory:
    """
    Factory Pattern for creating loaders from different data sources.
    """

    @staticmethod
    def create_loader(source_type: str, source_path: str) -> IDataLoader:
        """
        Create appropriate loader based on the type.

        :param source_type: "csv" / "json" / "api" / "db"
        :param source_path: file path or URL or DB connection string
        :return: IDataLoader instance
        """

        source_type = source_type.lower()

        if source_type == "csv":
            return CSVLoader(source_path)

        # Future extensions:
        # if source_type == "json":
        #     return JSONLoader(source_path)
        #
        # if source_type == "api":
        #     return APILoader(source_path)
        #
        # if source_type == "db":
        #     return DBLoader(source_path)

        raise ValueError(f"Unsupported data source type: {source_type}")
