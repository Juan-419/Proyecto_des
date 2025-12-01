import os
from supabase import create_client
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    return supabase

async def upload_to_bucket(file: UploadFile):
    bucket = "imagenes"  # tu bucket real

    # Leer contenido del archivo
    content = await file.read()
    filename = file.filename  # toma el nombre original

    # Subir al bucket
    supabase.storage.from_(bucket).upload(filename, content)

    # URL pública resultante
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
