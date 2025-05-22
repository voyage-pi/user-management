from app.services.middleware import require_auth, get_current_user
from app.models.questions import Preferences
from typing import List
from fastapi import APIRouter,Request

router = APIRouter(prefix="/preferences", tags=[])

@router.post("/")
@require_auth
async def add_user_preferences(questions:Preferences,request:Request):
    user=get_current_user(request)
    print(user)
    print(questions)
    return ()

