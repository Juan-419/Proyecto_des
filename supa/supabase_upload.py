import os
from supabase import create_client
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    return supabase

async def upload_to_bucket(file: UploadFile):
    bucket = "Taller-mult" 

    content = await file.read()

    filename = file.filename.replace(" ", "_")

    storage_path = f"clientes/{filename}"  


    try:
        supabase.storage.from_(bucket).upload(
            storage_path,
            content,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        print("ERROR SUBIENDO ARCHIVO →", e)
        raise e

    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{storage_path}"
