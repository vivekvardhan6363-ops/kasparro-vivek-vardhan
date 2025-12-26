from pydantic import BaseModel
from typing import List, Optional

class Record(BaseModel):
    id: int
    source: str
    coin_id: str
    name: str
    symbol: str
    market_cap: Optional[float]

class Metadata(BaseModel):
    request_id: str
    api_latency_ms: float
    page: int
    limit: int
    total_records: int

class DataResponse(BaseModel):
    metadata: Metadata
    data: List[Record]
