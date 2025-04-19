from fastapi import APIRouter

from app.handlers.trips_handler import select_all_trips, create_trip, select_user_trips

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/")
async def get_all_trips():
    """Get all trips from the database."""
    return select_all_trips()

@router.post("/")
async def post_trip(user_id:int, trip_id:int):
    """Create a new trip in the database."""
    return create_trip(user_id, trip_id)

@router.get("/{user_id}")
async def get_user_trips(user_id: int):
    """Get all trips for a specific user."""
    return select_user_trips(user_id)



