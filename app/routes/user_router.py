from typing import Optional
from fastapi import APIRouter,Cookie,File,UploadFile

from app.models.user import UserLogin, UserRegister

from app.handlers.user_handler import get_current_user, login_user, register_user, update_avatar, update_banner

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

@router.patch("/{user_id}/avatar")
async def upload_avatar(user_id: int, avatar: UploadFile = File(...)):
    """Update the avatar for a specific user."""
    return await update_avatar(user_id, avatar)

@router.patch("/{user_id}/banner")
async def upload_banner(user_id: int, banner: UploadFile = File(...)):
    """Update the banner for a specific user."""
    return await update_banner(user_id, banner)
