from fastapi import APIRouter

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/")
async def read_root():
    return {"User Management is Running!"}
