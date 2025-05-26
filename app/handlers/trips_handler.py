from app.services.supabase_client import supabase
from datetime import datetime

def select_all_trips():
    response = supabase.table("user_trips").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No trips found!"}
    
def create_trip(user_id: int, trip_id: str, trip_is_group: bool, is_save_operation: bool = False, preference_id: int = None):
    # Validate trip_type
    if trip_is_group not in [True, False]:
        return {"message": "Invalid trip type! Must be 'individual' or 'group'"}
    
    print(f"DEBUG: create_trip called with user_id={user_id}, trip_id={trip_id}, trip_is_group={trip_is_group}, preference_id={preference_id}")
    
    # Check if user is already a participant in this trip
    existing_response = supabase.table("user_trips").select("*").eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if existing_response.data and len(existing_response.data) > 0:
        print(f"User {user_id} is already a participant in trip {trip_id}")
        
        if is_save_operation:
            # For save operations, update the existing record
            print(f"Updating existing participant record for user {user_id} in trip {trip_id}")
            update_data = {
                "status": "group" if trip_is_group else "individual",
                "joined_trip_at": datetime.now().isoformat()
            }
            if preference_id is not None:
                update_data["preference_id"] = preference_id
                print(f"DEBUG: Adding preference_id to update_data: {preference_id}")
                
            print(f"DEBUG: Update data: {update_data}")
            update_response = supabase.table("user_trips").update(update_data).eq("user_id", user_id).eq("trip_id", trip_id).execute()
            
            print(f"DEBUG: Update response: {update_response}")
            if update_response.data:
                return update_response.data[0]
            else:
                print(f"DEBUG: Update failed - error: {update_response}")
                return {"message": "Failed to update participant record!"}
        else:
            # For creation operations, reject duplicates
            return {"message": "User is already a participant in this trip!"}
        
    # Create new participant record if user is not already a participant
    insert_data = {
        "user_id": user_id, 
        "trip_id": trip_id, 
        "status": "group" if trip_is_group else "individual",
        "joined_trip_at": datetime.now().isoformat(),
    }
    if preference_id is not None:
        insert_data["preference_id"] = preference_id
        print(f"DEBUG: Adding preference_id to insert_data: {preference_id}")
        
    print(f"DEBUG: Insert data: {insert_data}")
    response = supabase.table("user_trips").insert(insert_data).execute()
    print(f"DEBUG: Insert response: {response}")
    
    if response.data:
        return response.data
    else:
        print(f"DEBUG: Insert failed - error: {response}")
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
        # Include preference_id in the response for the trip creator (first participant)
        participants_with_preferences = []
        for participant in response.data:
            participant_data = dict(participant)
            participants_with_preferences.append(participant_data)
        return participants_with_preferences
    else:
        return {"message": "No participants found!"}
