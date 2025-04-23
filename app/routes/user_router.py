from app.models.response import ResponseBody
from app.services.middleware import require_auth,get_current_user
from fastapi import APIRouter,Request,status
from app.models.user import UserLogin, UserRegister
from app.handlers.user_handler import login_user, register_user 

router = APIRouter(prefix="/user", tags=["user"])


# voyage_at is the cookie with the access_token of the session of the user
@router.get("/current_user")
@require_auth
async def get_user(request:Request):
    """Get information for a specific user by ID."""
    user =get_current_user(request)
    return ResponseBody(user.model_dump(),"",status.HTTP_200_OK)

@router.post("/login")
async def login(user: UserLogin):
    """Authenticate a user and create a session."""
    return login_user(user)

@router.post("/register")
async def register(user: UserRegister):
    """Register a new user account."""
    return register_user(user)
