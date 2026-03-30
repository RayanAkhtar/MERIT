import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client | None = None
if url and key:
    supabase = create_client(url, key)
else:
    print("Warning: Supabase URL and Key are not set in the environment variables.")
