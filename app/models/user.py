from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password:str

class User(BaseModel):
    tag:str|None
    name:str
    email:str
    avatar_url:str | None
    banner_url:str | None
    id:int

