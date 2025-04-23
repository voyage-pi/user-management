from fastapi import UploadFile, File

from app.services.supabase_client import supabase
from app.config.settings import SUPABASE_URL, SUPABASE_AVATAR_BUCKET, SUPABASE_BANNER_BUCKET
from fastapi import status
from app.models.user import UserLogin, UserRegister,User
from app.models.response import ResponseBody


def get_current_user(token:str| None):
    try:
        print(token)
        if token==None:
            raise Exception()
        # Verify token with Supabase
        auth_user = supabase.auth.get_user(token)
        user_email=auth_user.user.user_metadata['email']
        response= supabase.table("user").select("*").eq("email", user_email).execute()
        user_data=User(**(response.data[0]))
        return ResponseBody(user_data.model_dump(),"",status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return ResponseBody({},
            "Invalid authentication token",
            status.HTTP_401_UNAUTHORIZED
        )

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
