from app.services.supabase_client import supabase
from fastapi import status
from app.models.user import UserLogin, UserRegister,User
from app.models.response import ResponseBody
from datetime import datetime
import time

def get_current_user(token:str| None):
    try:
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
        return ResponseBody({},e.message,status.HTTP_500_INTERNAL_SERVER_ERROR)
