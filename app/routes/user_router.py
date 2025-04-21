from typing import Optional
from fastapi import APIRouter,Cookie,Cookie

from app.models.user import UserLogin, UserRegister

from app.handlers.user_handler import get_current_user, login_user, register_user 

router = APIRouter(prefix="/user", tags=["user"])


# voyage_at is the cookie with the access_token of the session of the user
@router.get("/current_user")
async def get_user(voyage_at:Optional[str]=Cookie(None)):
    """Get information for a specific user by ID."""
    return get_current_user(voyage_at)

@router.post("/login")
async def login(user: UserLogin):
    """Authenticate a user and create a session."""
    return login_user(user)

@router.post("/register")
async def register(user: UserRegister):
    """Register a new user account."""
    return register_user(user)
