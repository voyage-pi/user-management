from fastapi import UploadFile, File
import mimetypes

from app.services.supabase_client import supabase, supabase_admin
from app.config.settings import SUPABASE_URL, SUPABASE_AVATAR_BUCKET, SUPABASE_BANNER_BUCKET
from fastapi import status
from app.models.user import UserLogin, UserRegister,User
from app.models.response import ResponseBody

def select_all_users():
    response = supabase.table("user").select("*").execute()
    if response.data:
        return response.data
    else:
        return {"message": "No users found!"}

def select_user_info(user_id: int):
    response = supabase.table("user").select("*").eq("id", user_id).execute()
    if response.data:
        return response.data[0]
    else:
        return {"message": "User not found!"}

def login_user(user: UserLogin):
    try:
        response= supabase.table("user").select("*").eq("email", user.email).execute()
        if len(response.data)!=1:
            return ResponseBody({},"User doens't exist!",status.HTTP_404_NOT_FOUND)
        auth=supabase.auth.sign_in_with_password(
            {
                "email":user.email,
                "password":user.password
            }
        )
        user_db=response.data[0]
        session=auth.session
        user=User(**user_db)
        response=ResponseBody(user.model_dump(),"Authenticaed successfuly!",status.HTTP_200_OK)
        response.set_cookie_header({
                "key":"voyage_at",
                "value":session.access_token,
                "httponly":True
            }
        )
        return response 
    except Exception as e:
        print(e)
        return ResponseBody({},e.message,status.HTTP_422_UNPROCESSABLE_ENTITY)

def register_user(user: UserRegister):
    insertUser=user.model_dump()
    insertUser["tag"]=user.name.lower()
    password=insertUser.pop("password")
    if len(password) <6:
        return ResponseBody({},"Password has to be greater then 6 characters!",status.HTTP_500_INTERNAL_SERVER_ERROR)
    # insert the record to the our user's table then make the signUp which inserts a record into the auth.user table native of schema auth from supabase
    try:
        supabase.table("user").insert(insertUser).execute()
        # if there is no error then the inserted parameters should be on the auth.users table
        supabase.auth.sign_up(
            {
                "email":user.email,
                "password":user.password,
            }
        )
        return ResponseBody({},"User registered sucessfully!", status.HTTP_200_OK) 
    except Exception as e :
        print(e)
        return ResponseBody({},"User already exists",status.HTTP_409_CONFLICT)


async def update_avatar(user_id: int, avatar: UploadFile = File(...)):
    try:
        response = supabase.table("user").select("tag").eq("id", user_id).execute()
        if response.data:
            username = response.data[0]["tag"]
            image_url = None
            if avatar and avatar.filename != "":
                image_filename = f"{username}-{avatar.filename}"
                file_content = await avatar.read()
                content_type = avatar.content_type
                if not content_type:
                    content_type = mimetypes.guess_type(avatar.filename)[0] or "application/octet-stream"
                
                try:
                    print("Attempting to upload to bucket:", SUPABASE_AVATAR_BUCKET)
                    upload_result = supabase_admin.storage.from_(SUPABASE_AVATAR_BUCKET).upload(
                        image_filename, 
                        file_content,
                        file_options={
                            "contentType": content_type,
                            "upsert": "true"
                        }
                    )
                    print("Upload response:", upload_result)    
                    # UploadResponse object returns a path on success
                    if upload_result and hasattr(upload_result, 'path'):
                        image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_AVATAR_BUCKET}/{image_filename}"
                except Exception as upload_error:
                    print(f"Avatar upload error detail: {str(upload_error)}")

        if image_url:
            supabase.table("user").update({"avatar_url": image_url}).eq("id", user_id).execute()
            return {"message": "Avatar updated successfully!"}
        else:
            return {"message": "Avatar update failed!"}
    except Exception as e:
        print("Avatar upload error:", str(e))
        return {"message": f"Avatar update failed with error: {str(e)}"}
            
async def update_banner(user_id: int, banner: UploadFile = File(...)):
    try:
        response = supabase.table("user").select("tag").eq("id", user_id).execute()
        if response.data:
            username = response.data[0]["tag"]
            image_url = None
            if banner and banner.filename != "":
                print("Banner was uploaded", banner.filename)
                image_filename = f"{username}-{banner.filename}"
                file_content = await banner.read()
                content_type = banner.content_type
                if not content_type:
                    content_type = mimetypes.guess_type(banner.filename)[0] or "application/octet-stream"
                print(f"Detected content type: {content_type}")
                
                try:
                    print("Attempting to upload to bucket:", SUPABASE_BANNER_BUCKET)
                    upload_result = supabase_admin.storage.from_(SUPABASE_BANNER_BUCKET).upload(
                        image_filename, 
                        file_content,
                        file_options={
                            "contentType": content_type,
                            "upsert": "true"
                        }
                    )
                    print("Upload response:", upload_result)
                    
                    # UploadResponse object returns a path on success
                    if upload_result and hasattr(upload_result, 'path'):
                        print("Image was uploaded in supabase", image_filename)
                        image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BANNER_BUCKET}/{image_filename}"
                except Exception as upload_error:
                    print(f"Banner upload error detail: {str(upload_error)}")
                    
        if image_url:
            print("Image URL was generated", image_url)
            supabase.table("user").update({"banner_url": image_url}).eq("id", user_id).execute()
            return {"message": "Banner updated successfully!"}
        else:
            return {"message": "Banner update failed!"}
    except Exception as e:
        print("Banner upload error:", str(e))
        return {"message": f"Banner update failed with error: {str(e)}"}
