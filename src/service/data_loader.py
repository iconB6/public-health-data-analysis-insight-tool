from typing import List, Dict, Any
from src.infrastructure.data_loader_factory import DataLoaderFactory
from src.interface.data_loader_interface import IDataLoader


class DataLoadingService:
    """
    Business service layer responsible for loading data using the abstract factory.
    Does NOT clean or save data. Purely loads data.
    """

    def __init__(self):
        pass

    def load_data(self, source_type: str, source_path: str) -> List[Dict[str, Any]]:
        """
        Use factory to create the appropriate loader and return loaded rows.
        """
        loader: IDataLoader = DataLoaderFactory.create_loader(source_type, source_path)
        return loader.load()
