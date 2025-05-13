from app.services.middleware import require_auth, get_current_user
from fastapi import APIRouter, Request

from app.handlers.places_handler import select_all_places, select_user_favorite_places, add_user_favorite_place, remove_user_favorite_place

router = APIRouter(prefix="/places", tags=["places"])

@router.get("/")
async def get_all_user_places():
    return select_all_places()

@router.get("/user/")
@require_auth
async def get_user_favorite_places(request:Request):
    user = get_current_user(request)
    return select_user_favorite_places(user.id)

@router.post("/user/favorite")
@require_auth
async def post_user_favorite_place(request:Request, place_id:int):
    user = get_current_user(request)
    return add_user_favorite_place(user.id, place_id)

@router.delete("/user/favorite")
@require_auth
async def delete_user_favorite_place(request:Request, place_id:int):
    user = get_current_user(request)
    return remove_user_favorite_place(user.id, place_id)