from fastapi import APIRouter, Request

from app.handlers.trips_handler import select_all_trips, create_trip, select_user_trips, select_user_invitations, select_user_invites, make_invite, accept_invitation, reject_invitation, trip_participants, is_trip_owner, remove_participant
from app.services.middleware import get_current_user, require_auth

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/")
async def get_all_trips():
    """Get all trips from the database."""
    return select_all_trips()

@router.post("/save")
@require_auth
async def post_trip(trip_id: str, request: Request):
    """Create a new trip in the database."""
    user = get_current_user(request)
    return create_trip(user.id, trip_id)

@router.get("/users/")
@require_auth
async def get_user_trips(request: Request):
    """Get all trips for a specific user."""
    user = get_current_user(request)
    return select_user_trips(user.id)

@router.get("/invitations/users/")
@require_auth
async def get_user_invitations(request: Request):
    """Get all invitations for a specific user."""
    user = get_current_user(request)
    return select_user_invitations(user.id)

@router.get("/invites/users/")
@require_auth
async def get_user_invites(request: Request):
    """Get all invites for a specific user."""
    user = get_current_user(request)
    return select_user_invites(user.id)

@router.post("/invitations")
@require_auth
async def create_invitation(trip_id: str, request: Request):
    """Invite a user to a trip."""
    user = get_current_user(request)
    return make_invite(user.id, trip_id)

@router.patch("/invitations")
@require_auth
async def accept_trip_invitation(trip_id: str, request: Request):
    """Accept an invitation to a trip."""
    user = get_current_user(request)
    return accept_invitation(user.id, trip_id)

@router.delete("/invitations")
@require_auth
async def reject_trip_invitation(trip_id: str, request: Request):
    """Reject an invitation to a trip."""
    user = get_current_user(request)
    return reject_invitation(user.id, trip_id)

@router.get("/{trip_id}/participants/")
@require_auth
async def get_trip_participants(trip_id: str, request: Request):
    """Get all participants of a trip."""
    user = get_current_user(request)
    return trip_participants(trip_id)

@router.delete("/{trip_id}/participants/")
@require_auth
async def remove_trip_participant(user_id: int, trip_id: str, request: Request):
    """Remove a participant from a trip. If the participant is the owner, ownership will be transferred to the longest-standing participant."""
    user = get_current_user(request)
    if is_trip_owner(user.id, trip_id):
        return remove_participant(user_id, trip_id)
    else:
        return {"message": "You are not the owner of this trip."}
