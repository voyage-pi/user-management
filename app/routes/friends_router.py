from fastapi import APIRouter

from app.handlers.friends_handler import get_all_friends_table, get_user_friends, get_friend_requests_sent, get_friend_requests_received, request_friend, accept_friend, remove_friend

router = APIRouter(prefix="/friends", tags=["friends"])

@router.get("/")
async def get_all_friends():
    """Retrieve all friendship relationships from the database."""
    return get_all_friends_table()

@router.get("/{user_id}")
async def get_friends(user_id: int):
    """Get all friends for a specific user."""
    return get_user_friends(user_id)

@router.get("/requests/sent/{user_id}")
async def get_friend_requests_sent(user_id: int):
    """Get all friend requests sent by a specific user."""
    return get_friend_requests_sent(user_id)

@router.get("/requests/received/{user_id}")
async def get_friend_requests_received(user_id: int):
    """Get all friend requests received by a specific user."""
    return get_friend_requests_received(user_id)

@router.post("/requests/send")
async def send_friend_request(user_id: int, friend_id: int):
    """Send a friend request from one user to another."""
    return request_friend(user_id, friend_id)

@router.post("/requests/accept")
async def accept_friend_request(user_id: int, friend_id: int):
    """Accept a pending friend request."""
    return accept_friend(user_id, friend_id)

@router.post("/requests/remove")
async def remove_friend(user_id: int, friend_id: int):
    """Remove a friend relationship between two users."""
    return remove_friend(user_id, friend_id)





