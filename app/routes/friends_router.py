from fastapi import APIRouter, Request
from app.services.middleware import require_auth, get_current_user
from app.handlers.friends_handler import get_all_friends_table, get_user_friends, get_friend_requests_sent, get_friend_requests_received, request_friend, accept_friend, remove_friend

router = APIRouter(prefix="/friends", tags=["friends"])

@router.get("/")
async def get_all_friends():
    """Retrieve all friendship relationships from the database."""
    return get_all_friends_table()

@router.get("/users/")
@require_auth
async def get_friends(request: Request):
    """Get all friends for a specific user."""
    user = get_current_user(request)
    return get_user_friends(user.id)

@router.get("/requests/sent/users/")
@require_auth
async def get_sent_requests(request: Request):
    """Get all friend requests sent by a specific user."""
    user = get_current_user(request)
    return get_friend_requests_sent(user.id)

@router.get("/requests/received/users/")
@require_auth
async def get_received_requests(request: Request):
    """Get all friend requests received by a specific user."""
    user = get_current_user(request)
    return get_friend_requests_received(user.id)

@router.post("/requests")
@require_auth
async def create_friend_request(friend_id: int, request: Request):
    """Send a friend request from one user to another."""
    user = get_current_user(request)
    return request_friend(user.id, friend_id)

@router.patch("/requests")
@require_auth
async def update_friend_request(friend_id: int, request: Request):
    """Accept a friend request."""
    user = get_current_user(request)
    return accept_friend(user.id, friend_id)

@router.delete("/requests")
@require_auth
async def delete_friend_relationship(friend_id: int, request: Request):
    """Remove a friend relationship between two users."""
    user = get_current_user(request)
    return remove_friend(user.id, friend_id)
