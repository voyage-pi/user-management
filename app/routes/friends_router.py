from fastapi import APIRouter, Query, Body, HTTPException
from typing import Union
import traceback
from fastapi import Request
from app.services.middleware import require_auth, get_current_user
from app.handlers.friends_handler import get_all_friends_table, get_user_friends, get_friend_requests_sent, get_friend_requests_received, request_friend, accept_friend, remove_friend, search_users

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
    try:
        return get_user_friends(user.id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests/sent/users/")
@require_auth
async def get_sent_requests(request: Request):
    """Get all friend requests sent by a specific user."""
    user = get_current_user(request)
    try:
        return get_friend_requests_sent(user.id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests/received/users/")
@require_auth
async def get_received_requests(request: Request):
    """Get all friend requests received by a specific user."""
    user = get_current_user(request)
    try:
        return get_friend_requests_received(user.id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_for_users(
    term: str = Query(..., description="Email, username, or user ID to search for"),
    current_user_id: int = Query(None, description="Current user ID to exclude from results")
):
    """
    Search for users by email, username, or user ID.
    This endpoint can be used to find users to send friend requests to.
    """
    try:
        return search_users(term, current_user_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/requests")
async def create_friend_request(
    request: Request,
    friend_id: Union[int, str] = Body(..., description="ID, email, or username of the user to send the request to")
):
    """
    Send a friend request from one user to another.
    The friend_id can be either a numeric ID, an email address, or a username.
    """
    user = get_current_user(request)
    try:
        if not user:
            raise HTTPException(status_code=400, detail="User ID is required")
        if not friend_id:
            raise HTTPException(status_code=400, detail="Friend ID, email, or username is required")
            
        result = request_friend(user.id, friend_id)
        
        # Check if there was an error in the result
        if "message" in result and "error" in result["message"].lower():
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/requests")
@require_auth
async def accept_friend_request(
    request: Request,
    friend_id: int = Body(..., description="ID of the user accepting the request")
):
    """Accept a pending friend request. 
    
    Parameters:
    - user_id: ID of the user who sent the request
    - friend_id: ID of the user accepting the request
    """
    try:
        user = get_current_user(request)
        print(f"Accepting friend request from {user.id} to {friend_id}")
        return accept_friend(user.id, friend_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/requests")
@require_auth
async def delete_friend_relationship(
    request: Request,
    friend_id: int = Body(..., description="ID of the user rejecting the request")
):
    """Remove a friend relationship between two users or reject a friend request.
    
    Parameters:
    - user_id: ID of the user who sent the request
    - friend_id: ID of the user rejecting the request
    """
    try:
        user = get_current_user(request)
        print(f"Removing friend relationship between {user.id} and {friend_id}")
        return remove_friend(user.id, friend_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))





