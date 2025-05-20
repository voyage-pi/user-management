from app.services.supabase_client import supabase
from datetime import datetime

def select_all_trips():
    response = supabase.table("user_trips").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}
    
def create_trip(user_id: int, trip_id: str, trip_is_group: bool):
    # Validate trip_type
    if trip_is_group not in [True, False]:
        return {"message": "Invalid trip type! Must be 'individual' or 'group'"}
        
    response = supabase.table("user_trips").insert({
        "user_id": user_id, 
        "trip_id": trip_id, 
        "status": "group" if trip_is_group else "individual",
        "joined_trip_at": datetime.now().isoformat()
    }).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Trip creation failed!"}
    
def select_user_trips(user_id: int):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).neq("status", "pending").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}
    
def select_user_invitations(user_id: int):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("status", "pending").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No invitations found!"}

def select_user_invites(user_id: int):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("status", "group").execute()
    if response.data:
        invites = []
        for trip_id in response.data:
            response = supabase.table("user_trips").select("*").eq("trip_id", trip_id).eq("status", "pending").execute()
            if response.data:
                invites.append(response.data)
        if len(invites) > 0:
            return invites
        else:
            return {"message": "No invites found!"}
    else:
        return {"message": "No trips found!"}
    
def make_invite(user_id: int, trip_id: str):
    # check if user is already in the trip
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if response.data:
        return {"message": "User is already in the trip!"}
    # create invite
    response = supabase.table("user_trips").insert({
        "user_id": user_id, 
        "trip_id": trip_id, 
        "status": "pending"
    }).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Invite failed!"}

def accept_invitation(user_id: int, trip_id: str):
    response = supabase.table("user_trips").update({"status": "group"}).eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Acceptance failed!"}
    
def reject_invitation(user_id: int, trip_id: str):
    response = supabase.table("user_trips").delete().eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Rejection failed!"}
    
def trip_participants(trip_id: str):
    response = supabase.table("user_trips").select("*").eq("trip_id", trip_id).neq("status", "pending").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No participants found!"}
