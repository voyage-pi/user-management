from app.services.supabase_client import supabase, supabase_admin

def select_all_places():
    response = supabase.table("user_places").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No places found!"}
    
def select_user_favorite_places(user_id:int):
    response = supabase.table("user_places").select("*").eq("user_id", user_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "No favorite places found!"}
    
def add_user_favorite_place(user_id:int, place_id:int):
    response = supabase.table("user_places").insert({"user_id": user_id, "place_id": place_id}).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Failed to add favorite place!"}

def remove_user_favorite_place(user_id:int, place_id:int):
    response = supabase.table("user_places").delete().eq("user_id", user_id).eq("place_id", place_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Failed to remove favorite place!"}