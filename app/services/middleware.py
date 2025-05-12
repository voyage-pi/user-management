from fastapi import Request, HTTPException, status
from typing import Callable
from functools import wraps
from app.services.supabase_client import supabase
from app.models.user import User

# Custom decorator for protected routes
def require_auth(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if request is None:
            for arg in kwargs.values():
                if isinstance(arg, Request):
                    request = arg
                    break
        
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request object not found in function arguments"
            )
        
        # Get token from cookie
        token = request.cookies.get("voyage_at")
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token missing"
            )
        
        try:
            # Verify token with Supabase
            auth_user = supabase.auth.get_user(token)
            user_email = auth_user.user.user_metadata['email']
            
            # Get user data from your table
            response = supabase.table("user").select("id,tag, email, name, avatar_url, bio, banner_url, created_at, show_trips").eq("email", user_email).execute()
            
            if not response.data or len(response.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
                
            # Create user object and attach to request state
            user_data = User(**(response.data[0]))
            request.state.user = user_data
            
            # Continue with the original function
            return await func(*args, **kwargs)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}"
            )
    
    return wrapper

def get_current_user(request: Request) -> User:
    if hasattr(request.state, 'user'):
        return request.state.user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not authenticated"
    )
