from pydantic import BaseModel

class TripSaveBody(BaseModel):
    trip_id: str
    is_group: bool
