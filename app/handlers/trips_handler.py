from app.services.supabase_client import supabase

def select_all_trips():
    response = supabase.table("user_trips").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}
    
def create_trip(user_id: int, trip_id: int):
    response = supabase.table("user_trips").insert({"user_id": user_id, "trip_id": trip_id, "status": "owner"}).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Trip creation failed!"}
    
def select_user_trips(user_id: int):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}