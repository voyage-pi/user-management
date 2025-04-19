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
    
def make_invite(user_id: int, trip_id: int):
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

def accept_invitation(user_id: int, trip_id: int):
    response = supabase.table("user_trips").update({"status": "participant"}).eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Acceptance failed!"}
    
def reject_invitation(user_id: int, trip_id: int):
    response = supabase.table("user_trips").delete().eq("user_id", user_id).eq("trip_id", trip_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Rejection failed!"}
    
def remove_participant(user_id: int, trip_id: int):
    response = supabase.table("user_trips").delete().eq("user_id", user_id).eq("trip_id", trip_id).eq("status", "participant").execute()
    if response.data:
        return response.data
    else:
        return {"message": "Removal failed!"}
    
def remove_owner(trip_id: int):
    response1 = supabase.table("user_trips").delete().eq("trip_id", trip_id).eq("status", "owner").execute()
    print(response1.data)
    response2 = supabase.table("user_trips").select("*").eq("trip_id", trip_id).order("joined_trip_at", desc=True).execute()
    print(response2.data)
    if response1.data and response2.data:
        new_owner = response2.data[0]["user_id"]
        response3 = supabase.table("user_trips").update({"status": "owner"}).eq("user_id", new_owner).eq("trip_id", trip_id).execute()
        print(response3.data)
        if response3.data:
            return response3.data
        else:
            return {"message": "Owner update failed!"}
    else:
        return {"message": "Owner removal failed!"}
