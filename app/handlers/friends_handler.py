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
    """
    Create a friend request from user_id to friend_id
    
    Args:
        user_id: ID of the user sending the request
        friend_id: ID of the user receiving the request
    
    Returns:
        Dict with success/failure message
    """
    print(f"Creating friend request: user_id={user_id}, friend_id={friend_id}")
    
    # Validate that we're not trying to send a request to ourselves
    if user_id == friend_id:
        return {"message": "Cannot send a friend request to yourself."}
    
    # First check if we already have a friendship or pending request in either direction
    check_query1 = supabase.table("user_friends").select("*").eq("user_id", user_id).eq("friend_id", friend_id).execute()
    check_query2 = supabase.table("user_friends").select("*").eq("user_id", friend_id).eq("friend_id", user_id).execute()
    
    existing_relations = []
    if check_query1.data:
        existing_relations.extend(check_query1.data)
    if check_query2.data:
        existing_relations.extend(check_query2.data)
    
    if existing_relations:
        print(f"Found existing relationship between {user_id} and {friend_id}: {existing_relations}")
        for relation in existing_relations:
            status = relation.get("status")
            if status == "ok":
                return {"message": "You are already friends!"}
            elif status == "pending":
                return {"message": "Friend request already sent!"}
    
    # Get user information to include in the record
    user_info = supabase.table("user").select("*").eq("id", user_id).execute()
    friend_info = supabase.table("user").select("*").eq("id", friend_id).execute()
    
    if not user_info.data or not friend_info.data:
        return {"message": "One or both users not found!"}
    
    user_data = user_info.data[0]
    friend_data = friend_info.data[0]
    
    print(f"Creating friend request from {user_id} ({user_data.get('name')}) to {friend_id} ({friend_data.get('name')})")
    
    # Create a single entry that represents the request from user_id to friend_id
    try:
        response = supabase.table("user_friends").insert({
            "user_id": user_id, 
            "friend_id": friend_id, 
            "status": "pending",
            # Include user information to simplify lookups
        }).execute()
        
        print(f"Friend request response: {response.data if response.data else 'Error'}")
        
        if response.data:
            return {"message": "Friend request sent!"}
        else:
            return {"message": "Friend request failed!"}
    except Exception as e:
        print(f"Error creating friend request: {e}")
        return {"message": f"Friend request failed: {str(e)}"}

def remove_friend(user_id: int, friend_id: int):
    # Delete both directions of the friendship
    response1 = supabase.table("user_friends").delete().eq("user_id", user_id).eq("friend_id", friend_id).execute()
    response2 = supabase.table("user_friends").delete().eq("user_id", friend_id).eq("friend_id", user_id).execute()
    
    if response1.data or response2.data:
        return {"message": "Friend removed!"}
    else:
        return {"message": "Friend removal failed!"}

def accept_friend(user_id: int, friend_id: int):
    """Accept a pending friend request.
    
    Parameters:
    - user_id: ID of the user who sent the request
    - friend_id: ID of the user accepting the request
    """
    print(f"Accepting friend request: user_id={user_id}, friend_id={friend_id}")
    
    # Validate that we're not trying to accept a request to ourselves
    if user_id == friend_id:
        return {"message": "Cannot accept a friend request from yourself."}
    
    # First find the friendship record to ensure it exists
    # Note: user_id is the sender, friend_id is the receiver in the pending request
    response_find = supabase.table("user_friends") \
        .select("*") \
        .eq("user_id", friend_id) \
        .eq("friend_id", user_id) \
        .eq("status", "pending") \
        .execute()
    
    print(f"Found pending request: {response_find.data}")
    
    if not response_find.data:
        return {"message": "Friend request not found!"}
    
    try:
        # Update the existing request to "ok"
        response1 = supabase.table("user_friends") \
            .update({"status": "ok"}) \
            .eq("user_id", friend_id) \
            .eq("friend_id", user_id) \
            .execute()
        
        # Create the reverse direction with "ok" status
        response2 = supabase.table("user_friends") \
            .insert({
                "user_id": user_id,
                "friend_id": friend_id,
                "status": "ok"
            }) \
            .execute()
        
        print(f"Update responses: {response1.data}, {response2.data}")
        
        if response1.data and response2.data:
            return {"message": "Friend accepted!"}
        else:
            return {"message": "Friend acceptance failed!"}
    except Exception as e:
        print(f"Error accepting friend request: {e}")
        return {"message": f"Friend acceptance failed: {str(e)}"}

def get_friend_requests_sent(user_id: int):
    """
    Get all friend requests sent by a specific user.
    
    Args:
        user_id: ID of the user to get sent requests for
    
    Returns:
        List of friend requests or a message if none found
    """
    print(f"Looking for friend requests sent by user {user_id}")
    
    response = supabase.table("user_friends") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("status", "pending") \
        .execute()
    
    # Debug output
    print(f"Found {len(response.data) if response.data else 0} sent requests for user {user_id}")
    if response.data:
        for request in response.data:
            print(f"  Sent request: {request}")
        return response.data
    else:
        return {"message": "No friend requests sent!"}

def get_friend_requests_received(user_id: int):
    """
    Get all friend requests received by a specific user.
    
    Args:
        user_id: ID of the user to get received requests for
    
    Returns:
        List of friend requests or a message if none found
    """
    # Get requests where the user is the recipient (friend_id)
    print(f"Looking for friend requests received by user {user_id}")
    
    response = supabase.table("user_friends") \
        .select("*") \
        .eq("friend_id", user_id) \
        .eq("status", "pending") \
        .execute()
    
    # Debug output
    print(f"Found {len(response.data) if response.data else 0} friend requests for user {user_id}")
    if response.data:
        for request in response.data:
            print(f"  Request: {request}")
        return response.data
    else:
        return {"message": "No friend requests received!"}

def search_users(search_term: str, current_user_id: int = None):
    """
    Search for users by name or tag only.
    Args:
        search_term: The name or tag to search for
        current_user_id: The ID of the current user (to exclude from results)
    Returns:
        List of matching users with their details
    """
    try:
        # Search in both name and tag fields
        name_response = supabase.table("user").select("id, tag, email, name, avatar_url").ilike("name", f"%{search_term}%").execute()
        tag_response = supabase.table("user").select("id, tag, email, name, avatar_url").ilike("tag", f"%{search_term}%").execute()
        # Combine results (removing duplicates)
        result_data = name_response.data + [user for user in tag_response.data if user['id'] not in [u['id'] for u in name_response.data]]
        # Filter out the current user if provided
        if current_user_id is not None:
            result_data = [user for user in result_data if user['id'] != current_user_id]
        return result_data
    except Exception as e:
        print(f"Error searching users: {e}")
        return {"error": str(e)}















