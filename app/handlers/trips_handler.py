from app.services.supabase_client import supabase
from datetime import datetime

def select_all_trips():
    response = supabase.table("user_trips").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}
    
def create_trip(user_id: int, trip_id: str, trip_is_group: bool, is_save_operation: bool = False):
    # Validate trip_type
    if trip_is_group not in [True, False]:
        return {"message": "Invalid trip type! Must be 'individual' or 'group'"}
    
    # Check if user is already a participant in this trip
    existing_response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if existing_response.data and len(existing_response.data) > 0:
        print(f"User {user_id} is already a participant in trip {trip_id}")
        
        if is_save_operation:
            # For save operations, update the existing record
            print(f"Updating existing participant record for user {user_id} in trip {trip_id}")
            update_response = supabase.table("user_trips").update({
                "status": "group" if trip_is_group else "individual",
                "joined_trip_at": datetime.now().isoformat()
            }).eq("user_id", user_id).eq("trip_id", trip_id).execute()
            
            if update_response.data:
                return update_response.data[0]
            else:
                return {"message": "Failed to update participant record!"}
        else:
            # For creation operations, reject duplicates
            return {"message": "User is already a participant in this trip!"}
        
    # Create new participant record if user is not already a participant
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
    print("--------------------------------")
    response = supabase.table("user_trips").select("*").eq("trip_id", trip_id).neq("status", "pending").execute()
    if response.data:
        print(response.data)
        return response.data
    else:
        return {"message": "No participants found!"}
