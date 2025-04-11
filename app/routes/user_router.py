from fastapi import APIRouter
from app.services.supabase_client import select_all_users
router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/")
async def get_all_users():
    return select_all_users()
