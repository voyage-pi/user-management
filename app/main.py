from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import preferences_router, questions_router, user_router, friends_router, trips_router, trip_info_router, places_router

app = FastAPI()

app.include_router(user_router.router)
app.include_router(friends_router.router)
app.include_router(trips_router.router)
app.include_router(trip_info_router.router)
app.include_router(places_router.router)
app.include_router(questions_router.router)
app.include_router(preferences_router.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "User Management is Running!"}
