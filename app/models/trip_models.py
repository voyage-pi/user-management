from pydantic import BaseModel
from typing import Optional

class TripSaveBody(BaseModel):
    trip_id: str
    is_group: bool
    preference_id: Optional[int] = None
