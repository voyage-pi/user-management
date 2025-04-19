from app.services.supabase_client import supabase

from app.models.user import UserLogin, UserRegister

def select_all_users():
    response = supabase.table("user").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No users found!"}
    
def get_user_info(user_id: int):
    response = supabase.table("user").select("*").eq("id", user_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "User not found!"}

def login_user(user: UserLogin):
    response = supabase.table("user").select("*").eq("username", user.username).eq("password", user.password).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Login failed!"}

def register_user(user: UserRegister):
    response = supabase.table("user").insert(user.model_dump()).execute()
    if response.data:
        return response.data
    else:
        return {"message": "Registration failed!"}