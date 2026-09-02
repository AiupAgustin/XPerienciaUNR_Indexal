import streamlit as st
from supabase import create_client, Client
import time
import mimetypes

@st.cache_resource
def get_supabase_client() -> Client:
    """Instancia única del cliente de Supabase en memoria."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def subir_imagen_galeria(nombre_archivo: str, contenido_bytes: bytes) -> str:
    """
    Sube la imagen al bucket 'galeria_imagenes' con un timestamp para evitar colisiones
    y devuelve la URL pública directa.
    """
    supabase = get_supabase_client()
    bucket = "galeria_imagenes"
    
    # Sanitizar nombre y evitar colisiones
    extension = nombre_archivo.split(".")[-1] if "." in nombre_archivo else "png"
    mime_type, _ = mimetypes.guess_type(nombre_archivo)
    content_type = mime_type or "image/png"
    
    path_destino = f"{int(time.time())}_{nombre_archivo}"
    
    # Subida al bucket
    supabase.storage.from_(bucket).upload(
        path=path_destino,
        file=contenido_bytes,
        file_options={"content-type": content_type, "upsert": "true"}
    )
    
    # Obtener URL pública
    url_publica = supabase.storage.from_(bucket).get_public_url(path_destino)
    return url_publica

def guardar_analisis_en_galeria(titulo: str, categoria: str, imagen_url: str, master_json: dict) -> dict:
    """Inserta una tarjeta de análisis completa en la tabla galeria."""
    supabase = get_supabase_client()
    payload = {
        "titulo": titulo,
        "categoria": categoria,
        "imagen_url": imagen_url,
        "master_json": master_json
    }
    res = supabase.table("galeria").insert(payload).execute()
    return res.data[0] if res.data else {}

def obtener_items_galeria() -> list:
    """Devuelve todos los análisis guardados ordenados del más reciente al más antiguo."""
    supabase = get_supabase_client()
    res = supabase.table("galeria").select("*").order("created_at", desc=True).execute()
    return res.data or []