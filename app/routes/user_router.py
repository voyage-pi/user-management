from app.models.response import ResponseBody
from app.services.middleware import require_auth, get_current_user
from fastapi import APIRouter,Request, status, File, UploadFile
from app.models.user import UserLogin, UserRegister, UserUpdate
from app.handlers.user_handler import login_user, register_user, update_avatar, update_banner, select_all_users, select_user_info, update_user_info

router = APIRouter(prefix="/user", tags=["user"])

# voyage_at is the cookie with the access_token of the session of the user
@router.get("/")
async def get_all_users():
    """Get all users from the database."""
    return select_all_users()

@router.get("/current_user")
@require_auth
async def get_user_auth(request:Request):
    """Get information for a specific user by ID."""
    user =get_current_user(request)
    return ResponseBody(user.model_dump(),"",status.HTTP_200_OK)

@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get information for a specific user by ID."""
    return select_user_info(user_id)

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

@router.patch("/{user_id}/user-update")
async def update_user(user_id: int, user_update: UserUpdate):
    """Update user information like name, tag, bio, and show_trips."""
    return await update_user_info(user_id, user_update)