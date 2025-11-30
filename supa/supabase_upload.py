from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_to_bucket(file: bytes, filename: str):
    bucket = "imagenes"   # <-- pon aquí tu bucket real

    supabase.storage.from_(bucket).upload(filename, file)
    
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
