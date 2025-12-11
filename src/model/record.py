from dataclasses import dataclass
from typing import Dict

@dataclass
class Record:
    record_id: int | None   
    data_source: str        # csv/json/api/database
    dimensions: Dict[str, str]
    metrics: Dict[str, float]
