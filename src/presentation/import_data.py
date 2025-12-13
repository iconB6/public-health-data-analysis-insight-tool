from src.infrastructure.sqlite_repository import SQLiteRepository
from src.service.data_storage import DataStorageService
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner
import os
import shutil


def ensure_unique_db_path(db_path: str) -> str:
    """
    If db_path exists, create a copy with suffix:
        example.db → example_copy.db → example_copy_2.db → ...
    Returns a guaranteed unique file path.
    """
    if not os.path.exists(db_path):
        return db_path  # no conflict, safe to use

    base, ext = os.path.splitext(db_path)

    # try suffixes
    counter = 1
    new_path = f"{base}_copy{ext}"
    while os.path.exists(new_path):
        new_path = f"{base}_copy_{counter}{ext}"
        counter += 1

    print(f"[INFO] Database '{db_path}' exists. Using '{new_path}' instead.")
    return new_path

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
    if not db_path.endswith(".db"):
        db_path += ".db"
        
    db_path = ensure_unique_db_path(db_path)

    # store
    service = DataStorageService(db_path)
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