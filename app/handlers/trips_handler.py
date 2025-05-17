from app.services.supabase_client import supabase
from datetime import datetime

def select_all_trips():
    response = supabase.table("user_trips").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}
    
def create_trip(user_id: int, trip_id: str):
    response = supabase.table("user_trips").insert({
        "user_id": user_id, 
        "trip_id": trip_id, 
        "status": "owner",
        "joined_trip_at": datetime.now().isoformat()
    }).execute()
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
    
def select_user_invitations(user_id: int):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("status", "pending").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No invitations found!"}

def select_user_invites(user_id: int):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("status", "owner").execute()
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
    response = supabase.table("user_trips").insert({"user_id": user_id, "trip_id": trip_id, "status": "pending"}).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Invite failed!"}

def accept_invitation(user_id: int, trip_id: str):
    response = supabase.table("user_trips").update({"status": "participant"}).eq("user_id", user_id).eq("trip_id", trip_id).execute()
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
    response = supabase.table("user_trips").select("*").eq("trip_id", trip_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "No participants found!"}
    
def is_trip_owner(user_id: int, trip_id: str):
    response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("trip_id", trip_id).eq("status", "owner").execute()
    if response.data:
        return True
    else:
        return False
    
def remove_participant(user_id: int, trip_id: str):
    """
    Remove a participant from a trip. If the participant is the owner,
    transfer ownership to the longest-standing participant.
    """
    # First check if the user is the owner
    is_owner = is_trip_owner(user_id, trip_id)
    
    # Remove the user from the trip
    response = supabase.table("user_trips").delete().eq("user_id", user_id).eq("trip_id", trip_id).execute()
    
    if not response.data:
        return {"message": "Failed to remove participant"}
    
    # If the removed user was the owner, transfer ownership to the longest-standing participant
    if is_owner:
        # Get all remaining participants ordered by join date (oldest first)
        remaining_participants = supabase.table("user_trips")\
            .select("*")\
            .eq("trip_id", trip_id)\
            .order("joined_trip_at", desc=False)\
            .execute()
        
        if remaining_participants.data and len(remaining_participants.data) > 0:
            # Get the longest-standing participant
            new_owner = remaining_participants.data[0]
            
            # Update their status to owner
            update_response = supabase.table("user_trips")\
                .update({"status": "owner"})\
                .eq("user_id", new_owner["user_id"])\
                .eq("trip_id", trip_id)\
                .execute()
            
            if update_response.data:
                return {
                    "message": "Participant removed and ownership transferred",
                    "new_owner": new_owner["user_id"]
                }
            else:
                return {"message": "Participant removed but ownership transfer failed"}
    
    return {"message": "Participant removed successfully"}
