from pydantic import BaseModel
from typing import List

class RouteResult(BaseModel):
    polylineEncoded: str
    duration: int   #in seconds
    distance: int   #in meters

class ComputeRoutesResponse(BaseModel):
    routes: List[RouteResult]
