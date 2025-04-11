from supabase import create_client, Client
from app.config.settings import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def select_all_users():
    response = supabase.table("User").select("*").execute()
    return response.data