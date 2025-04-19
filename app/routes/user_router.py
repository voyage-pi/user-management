from fastapi import APIRouter

from app.models.user import UserLogin, UserRegister

from app.handlers.user_handler import select_all_users, login_user, register_user, get_user_info

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/")
async def get_all_users():
    """Retrieve all users from the database."""
    return select_all_users()

@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get information for a specific user by ID."""
    return get_user_info(user_id)

@router.post("/login")
async def login(user: UserLogin):
    """Authenticate a user and create a session."""
    return login_user(user)

@router.post("/register")
async def register(user: UserRegister):
    """Register a new user account."""
    return register_user(user)