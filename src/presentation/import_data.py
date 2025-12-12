from src.infrastructure.sqlite_repository import SQLiteRepository
from src.service.data_storage import DataStorageService
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner

# ==============================
#   Backend Interface Placeholders (for future implementation)
# ==============================

def import_data_from_source(source_type, source_path, db_name):
    """Backend interface: import -> clean -> store into SQLite."""
    loader = DataLoadingService()
    cleaner = DataCleaner()

    # load
    rows = loader.load_data(source_type, source_path)
    if not rows:
        return 0

    # clean
    cleaned = cleaner.clean(rows)

    # decide DB path (use file name 'default_db' when not provided)
    db_path = db_name if db_name else "default_db.db"

    # store
    repo = SQLiteRepository(db_path)
    service = DataStorageService(repo)
    service.connect()
    try:
        with service.transaction():
            inserted = service.save_full_record(cleaned)
    finally:
        try:
            service.disconnect()
        except Exception:
            pass

    return inserted