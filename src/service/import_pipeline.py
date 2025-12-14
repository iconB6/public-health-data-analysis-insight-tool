from src.service.loader_service import DataLoaderService
from src.service.clean_service import DataCleanService
from src.service.storage_service import DataStorageService
from src.interface.repository_interface import IRepository


def import_data(
    source_type: str,
    source_path: str,
    repository: IRepository,
) -> int:
    """
    Load → Clean → Store
    Return inserted record count
    """

    # load
    loader = DataLoaderService()
    rows = loader.load_data(source_type, source_path)

    # clean
    cleaner = DataCleanService()
    cleaned = cleaner.clean(rows)

    # store
    storage = DataStorageService(repository)
    repository.connect()

    try:
        with storage.transaction():
            inserted = storage.save_full_record(cleaned)
    finally:
        repository.disconnect()

    return inserted
