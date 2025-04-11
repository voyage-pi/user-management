from pydantic import BaseModel
from typing import List, Literal, Optional, Union

class Location(BaseModel):
    latitude: float
    longitude: float  

class PlaceID(BaseModel):
    place_id: str  

class ComputeRoutesRequest(BaseModel):
    origin: Union[Location, PlaceID]
    destination: Union[Location, PlaceID]
    intermediate: Optional[List[Union[Location, PlaceID]]] = []  # Optional, empty by default
    travelingMode: Literal["WALK", "DRIVE", "BICYCLE", "TRANSIT", "TWO_WHEELER"] = "DRIVE"  # Default to DRIVE