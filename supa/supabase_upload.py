import os
import uuid
from supabase import create_client
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_to_bucket(file: UploadFile):
    bucket = "Taller-mult"  # bucket real de Supabase

    
    content = await file.read()

    
    extension = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4()}{extension}"

    
    file_path = f"clientes/{unique_name}"

    
    result = supabase.storage.from_(bucket).upload(
        file_path,
        content
    )

    print("UPLOAD RESULT:", result)

    
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"
