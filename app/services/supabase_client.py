from supabase import create_client, Client
from app.config.settings import SUPABASE_URL, SUPABASE_KEY

from app.models.user import User

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def select_all_users():
    response = supabase.table("User").select("*").execute()
    return response.data

def login_user(user: User):
    response = supabase.table("User").select("*").eq("username", user.username).eq("password", user.password).execute()
    if response.data:
        return {"message": "Login successful", "user": response.data[0]}
    else:
        return {"message": "Login failed"}

def register_user(user: User):
    response = supabase.table("User").insert(user.model_dump()).execute()
    if response.data:
        return {"message": "Registration successful", "user": response.data[0]}
    else:
        return {"message": "Registration failed"}