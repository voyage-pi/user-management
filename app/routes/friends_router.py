from fastapi import APIRouter

from app.handlers.friends_handler import get_all_friends_table, get_user_friends, get_friend_requests_sent, get_friend_requests_received, request_friend, accept_friend, remove_friend

router = APIRouter(prefix="/friends", tags=["friends"])

@router.get("/")
async def get_all_friends():
    """Retrieve all friendship relationships from the database."""
    return get_all_friends_table()

@router.get("/users/{user_id}")
async def get_friends(user_id: int):
    """Get all friends for a specific user."""
    return get_user_friends(user_id)

@router.get("/requests/sent/users/{user_id}")
async def get_sent_requests(user_id: int):
    """Get all friend requests sent by a specific user."""
    return get_friend_requests_sent(user_id)

@router.get("/requests/received/users/{user_id}")
async def get_received_requests(user_id: int):
    """Get all friend requests received by a specific user."""
    return get_friend_requests_received(user_id)

@router.post("/requests")
async def create_friend_request(user_id: int, friend_id: int):
    """Send a friend request from one user to another."""
    return request_friend(user_id, friend_id)

@router.patch("/requests")
async def accept_friend_request(user_id: int, friend_id: int):
    """Accept a pending friend request."""
    return accept_friend(user_id, friend_id)

@router.delete("/requests")
async def delete_friend_relationship(user_id: int, friend_id: int):
    """Remove a friend relationship between two users."""
    return remove_friend(user_id, friend_id)





