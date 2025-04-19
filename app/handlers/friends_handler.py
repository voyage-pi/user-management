from app.services.supabase_client import supabase

def get_all_friends_table():
    response = supabase.table("user_friends").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No friends found!"}

def get_user_friends(user_id: int):
    response = supabase.table("user_friends").select("*").eq("user_id", user_id).eq("status", "ok").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No friends found!"}

def request_friend(user_id: int, friend_id: int):
    response1 = supabase.table("user_friends").insert({"user_id": user_id, "friend_id": friend_id, "status": "pending"}).execute()
    response2 = supabase.table("user_friends").insert({"user_id": friend_id, "friend_id": user_id, "status": "pending"}).execute()
    if response1.data and response2.data:
        return {"message": "Friend request sent!"}
    else:
        return {"message": "Friend request failed!"}

def remove_friend(user_id: int, friend_id: int):
    response1 = supabase.table("user_friends").delete().eq("user_id", user_id).eq("friend_id", friend_id).execute()
    response2 = supabase.table("user_friends").delete().eq("user_id", friend_id).eq("friend_id", user_id).execute()
    if response1.data and response2.data:
        return {"message": "Friend removed!"}
    else:
        return {"message": "Friend removal failed!"}

def accept_friend(user_id: int, friend_id: int):
    response1 = supabase.table("user_friends").update({"status": "ok"}).eq("user_id", user_id).eq("friend_id", friend_id).execute()
    response2 = supabase.table("user_friends").update({"status": "ok"}).eq("user_id", friend_id).eq("friend_id", user_id).execute()
    if response1.data and response2.data:
        return {"message": "Friend accepted!"}
    else:
        return {"message": "Friend acceptance failed!"}

def get_friend_requests_sent(user_id: int):
    response = supabase.table("user_friends").select("*").eq("user_id", user_id).eq("status", "pending").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No friend requests sent!"}

def get_friend_requests_received(user_id: int):
    response = supabase.table("user_friends").select("*").eq("friend_id", user_id).eq("status", "pending").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No friend requests received!"}















