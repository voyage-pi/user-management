from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password:str

class UserUpdate(BaseModel):
    name: str | None = None
    tag: str | None = None
    bio: str | None = None
    show_trips: bool | None = None

class User(BaseModel):
    tag: str
    name: str
    email: str
    avatar_url: str | None
    banner_url: str | None
    bio: str | None
    show_trips: bool
    id: int