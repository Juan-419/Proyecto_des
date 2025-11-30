import os
import uuid 
from typing import Optional
from fastapi import UploadFile
from supabase import create_client, Client
from dotenv import load_dotenv


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 

SUPABASE_BUCKET = "reportes-taller" 


_supabase_client:Optional[Client] = None

def get_supabase_client() -> Client:
    """Función para obtener o inicializar el cliente de Supabase."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
           
            raise ValueError(
                "Error de configuración: Faltan las variables de entorno de Supabase (SUPABASE_URL, SUPABASE_KEY)."
            )

        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    return _supabase_client

async def upload_to_bucket(file: UploadFile) -> str:
    """Sube un archivo a Supabase Storage y devuelve la URL pública."""
    client = get_supabase_client()

    try:
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        
        file_content = await file.read()
        
        
        file_path = f"clientes/{unique_filename}" 
        
        client.storage.from_(SUPABASE_BUCKET).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type
            }
        )
        public_url = client.storage.from_(
            SUPABASE_BUCKET
        ).get_public_url(file_path)
        
        return public_url
    except Exception as e:
        print(f"Error CRÍTICO al subir a Supabase: {e}")
        raise e