from app.services.middleware import require_auth, get_current_user
from app.handlers.questions_handler import get_all_questions
from fastapi import APIRouter

router = APIRouter(prefix="/questions", tags=[])

@router.get("/")
async def get_all_user_places():
    return get_all_questions()

