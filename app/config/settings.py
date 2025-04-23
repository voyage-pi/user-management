import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_AVATAR_BUCKET = os.getenv("SUPABASE_AVATAR_BUCKET")
SUPABASE_BANNER_BUCKET = os.getenv("SUPABASE_BANNER_BUCKET")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing or not loaded correctly")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing or not loaded correctly")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_SERVICE_ROLE_KEY is missing or not loaded correctly")

if not SUPABASE_AVATAR_BUCKET:
    raise ValueError("SUPABASE_AVATAR_BUCKET is missing or not loaded correctly")

if not SUPABASE_BANNER_BUCKET:
    raise ValueError("SUPABASE_BANNER_BUCKET is missing or not loaded correctly")