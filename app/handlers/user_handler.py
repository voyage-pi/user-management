from fastapi import UploadFile, File

from app.services.supabase_client import supabase
from app.config.settings import SUPABASE_URL, SUPABASE_AVATAR_BUCKET, SUPABASE_BANNER_BUCKET

from app.models.user import UserLogin, UserRegister

def select_all_users():
    response = supabase.table("user").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No users found!"}

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
    
def get_user_info(user_id: int):
    response = supabase.table("user").select("*").eq("id", user_id).execute()
    if response.data:
        return response.data
    else:
        return {"message": "User not found!"}
    
async def update_avatar(user_id: int, avatar: UploadFile = File(...)):
    response = supabase.table("user").select("username").eq("id", user_id).execute()
    if response.data:
        username = response.data[0]["username"]
        image_url = None
        if avatar and avatar.filename != "":
            image_filename = f"{username}-{avatar.filename}"
            file_content = await avatar.read()
            reponse = supabase.storage.from_(SUPABASE_AVATAR_BUCKET).upload(image_filename, file_content)
            if reponse.status_code == 200:
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_AVATAR_BUCKET}/{image_filename}"

    if image_url:
        supabase.table("user").update({"avatar": image_url}).eq("id", user_id).execute()
        return {"message": "Avatar updated successfully!"}
    else:
        return {"message": "Avatar update failed!"}
            
async def update_banner(user_id: int, banner: UploadFile = File(...)):
    response = supabase.table("user").select("username").eq("id", user_id).execute()
    if response.data:
        username = response.data[0]["username"]
        image_url = None
        if banner and banner.filename != "":
            image_filename = f"{username}-{banner.filename}"
            file_content = await banner.read()
            reponse = supabase.storage.from_(SUPABASE_BANNER_BUCKET).upload(image_filename, file_content)
            if reponse.status_code == 200:
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BANNER_BUCKET}/{image_filename}"
                
    if image_url:
        supabase.table("user").update({"banner": image_url}).eq("id", user_id).execute()
        return {"message": "Banner updated successfully!"}
    else:
        return {"message": "Banner update failed!"}
