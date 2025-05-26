from fastapi import Request, HTTPException, status
from typing import Callable
from functools import wraps
from app.services.supabase_client import supabase
from app.models.user import User
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.error("Request object not found in function arguments")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request object not found in function arguments"
            )
        
        # Get token from cookie
        token = request.cookies.get("voyage_at")
        
        # Also check for token in Authorization header (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            logger.info("Using token from Authorization header")
        
        if not token:
            logger.error("Authentication token missing")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token missing"
            )
        
        # Log token length for debugging (don't log the actual token)
        logger.info(f"Auth token length: {len(token)}")
        
        try:
            # Verify token with Supabase
            logger.info("Verifying token with Supabase")
            auth_user = supabase.auth.get_user(token)
            user_email = auth_user.user.user_metadata['email']
            logger.info(f"Token verified for email: {user_email}")
            
            # Get user data from your table
            logger.info(f"Getting user data from database for email: {user_email}")
            response = supabase.table("user").select("id,tag, email, name, avatar_url, bio, banner_url, created_at, show_trips").eq("email", user_email).execute()
            
            if not response.data or len(response.data) == 0:
                logger.error(f"User not found for email: {user_email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
                
            # Create user object and attach to request state
            user_data = User(**(response.data[0]))
            request.state.user = user_data
            logger.info(f"User authenticated: {user_data.id}")
            
            # Continue with the original function
            return await func(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}"
            )
    
    return wrapper

def get_current_user(request: Request) -> User:
    if hasattr(request.state, 'user'):
        return request.state.user
    logger.error("User not authenticated in get_current_user")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not authenticated"
    )
