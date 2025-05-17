from fastapi import APIRouter, Request
from app.services.middleware import require_auth, get_current_user
from app.handlers.trip_info_handler import get_user_trip_stats, get_user_trips, get_shared_trips, get_last_shared_trip

router = APIRouter(prefix="/trip-info", tags=["trip-info"])

@router.get("/stats/{user_id}")
@require_auth
async def select_user_trip_stats(user_id: str, request: Request):
    """
    Get trip statistics for a user including:
    - Number of trips
    - Number of countries visited
    - Number of cities visited
    - Number of days traveled
    """
    user = get_current_user(request)
    return await get_user_trip_stats(user_id)

@router.get("/trips/{user_id}")
@require_auth
async def select_user_trips(user_id: str, request: Request):
    """
    Get all trip IDs for a user
    """
    user = get_current_user(request)
    return await get_user_trips(user_id)

@router.get("/shared-trips/{user_id}")
@require_auth
async def select_shared_trips(user_id: str, request: Request):
    """
    Get all trips made with other users
    """
    user = get_current_user(request)
    return await get_shared_trips(user_id)

@router.get("/last-shared-trip/{user_id}/{other_user_id}")
@require_auth
async def select_last_shared_trip(user_id: str, other_user_id: str, request: Request):
    """
    Get details of the last trip between two users
    """
    user = get_current_user(request)
    return await get_last_shared_trip(user_id, other_user_id) 