from app.services.middleware import require_auth, get_current_user
from app.handlers.preferences_handler import get_preferences_form, get_preferences_trip, insert_preferences
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

