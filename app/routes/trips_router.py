from fastapi import APIRouter

from app.handlers.trips_handler import select_all_trips, create_trip, select_user_trips, select_user_invitations, select_user_invites, make_invite, accept_invitation, reject_invitation, remove_participant, remove_owner
from app.services.middleware import get_current_user, require_auth
from fastapi import APIRouter,Request

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/")
async def get_all_trips():
    """Get all trips from the database."""
    return select_all_trips()

@router.post("/save")
@require_auth
async def post_trip(trip_id:str,request:Request):
    """Create a new trip in the database."""
    user = get_current_user(request)
    return create_trip(user.id,trip_id)

@router.get("/users/{user_id}")
async def get_user_trips(user_id: int):
    """Get all trips for a specific user."""
    return select_user_trips(user_id)

@router.get("/invitations/users/{user_id}")
async def get_user_invitations(user_id: int):
    """Get all invitations for a specific user."""
    return select_user_invitations(user_id)

@router.get("/invites/users/{user_id}")
async def get_user_invites(user_id: int):
    """Get all invites for a specific user."""
    return select_user_invites(user_id)

@router.post("/invitations")
async def create_invitation(user_id: int, trip_id: str):
    """Invite a user to a trip."""
    return make_invite(user_id, trip_id)

@router.patch("/invitations")
async def accept_trip_invitation(user_id: int, trip_id: str):
    """Accept an invitation to a trip."""
    return accept_invitation(user_id, trip_id)

@router.delete("/invitations")
async def reject_trip_invitation(user_id: int, trip_id: str):
    """Reject an invitation to a trip."""
    return reject_invitation(user_id, trip_id)

@router.delete("/{trip_id}/participants/{user_id}")
async def remove_trip_participant(trip_id: str, user_id: int):
    """Remove a participant from a trip."""
    return remove_participant(user_id, trip_id)

@router.delete("/{trip_id}/owner")
async def remove_trip_owner(trip_id: str):
    """Remove the owner from a trip and promote the longest-participating member to owner."""
    return remove_owner(trip_id)


