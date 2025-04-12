from fastapi import APIRouter

from app.models.user import User

from app.services.supabase_client import select_all_users, login_user, register_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/")
async def get_all_users():
    return select_all_users()

@router.post("/login")
async def login(user: User):
    return login_user(user)

@router.post("/register")
async def register(user: User):
    return register_user(user)
