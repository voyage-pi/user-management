from app.services.middleware import require_auth, get_current_user
from app.handlers.preferences_handler import get_all_preferences_for_user, get_preference_by_id, get_preferences_form, insert_preferences
from app.models.questions import Preferences
from typing import List
from fastapi import APIRouter,Request

router = APIRouter(prefix="/preferences", tags=[])

@router.post("/")
@require_auth
async def add_user_preferences(pref:Preferences,request:Request):
    user=get_current_user(request)
    return insert_preferences(pref,user)

@router.get("/")
@require_auth
async def get_user_list_preferences(request:Request):
    user=get_current_user(request)
    return get_preferences_form(user)


@router.get("{id}")
@require_auth
async def get_pref_id(id:int,request:Request):
    user=get_current_user(request)
    return get_preference_by_id(id,user)

@router.get("/user")
@require_auth
async def get_all_pref_user(request:Request):
    user=get_current_user(request)
    return get_all_preferences_for_user(user)

