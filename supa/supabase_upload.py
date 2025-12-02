import os
import unicodedata
from supabase import create_client
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalize_filename(filename: str) -> str:
    """
    Elimina acentos, espacios y caracteres no permitidos.
    """
    filename = filename.replace(" ", "_")

    filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")

    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    filename = "".join(c for c in filename if c in allowed)

    return filename

async def upload_to_bucket(file: UploadFile):
    bucket = "Taller-mult"

    content = await file.read()

    filename = normalize_filename(file.filename)

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
