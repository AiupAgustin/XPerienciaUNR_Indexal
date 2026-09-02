import streamlit as st
from supabase import create_client, Client
import time
import mimetypes
import os

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

def registrar_analisis_galeria(
    imagen_path,
    tipo_analisis,
    modulos_seleccionados,
    descripcion="Análisis visual asistido por IA",
    master_json=None,
    nombre_personalizado=None,
):
    try:
        # 1. Mapeo de Categoría
        mapa_nombres = {
            "semiotico": "Semiótico",
            "ui_ux": "UI / UX",
            "packaging": "Packaging",
            "tipografia": "Tipografía",
            "logotipo": "Logotipo",
            "afiche": "Afiches",
            "afiches": "Afiches",
        }
        categoria_display = mapa_nombres.get(
            str(tipo_analisis).lower(), "Semiótico"
        )

        # 2. Mapeo idéntico al de Reportes para las Letras (A-F)
        MAPA_LETRAS = {
            "composicion_visual": ("A", "Composición visual"),
            "paleta_cromatica": ("B", "Paleta cromática"),
            "iluminacion": ("C", "Iluminación"),
            "semiotica_imagen": ("D", "Semiótica de la imagen"),
            "retorica_visual": ("E", "Retórica visual"),
            "contexto_denotacion": ("F", "Contexto y denotación"),
        }

        modulos_base_sel = [m for m in modulos_seleccionados if m in MAPA_LETRAS]
        total_modulos_posibles = len(MAPA_LETRAS)

        tiene_wcag = "transversal_wcag" in modulos_seleccionados
        tiene_hist = "transversal_historicas" in modulos_seleccionados

        if len(modulos_base_sel) == total_modulos_posibles:
            modulo_txt = "Análisis completo · 6 módulos"
        elif len(modulos_base_sel) == 1:
            letra, _ = MAPA_LETRAS[modulos_base_sel[0]]
            modulo_txt = f"MÓDULO {letra}"
        elif len(modulos_base_sel) > 1:
            letras_activas = sorted([MAPA_LETRAS[m][0] for m in modulos_base_sel])
            modulo_txt = f"MÓDULOS {', '.join(letras_activas)}"
        elif tiene_wcag and tiene_hist:
            modulo_txt = "Módulos transversales · WCAG e Historia"
        elif tiene_wcag:
            modulo_txt = "Módulo Accesibilidad · WCAG 2.1"
        elif tiene_hist:
            modulo_txt = "Módulo Referencias históricas"
        else:
            modulo_txt = "Diagnóstico visual"

        # 3. Determinar el nombre real de la pieza (evitando el prefijo temporal tmp)
        nombre_base_real = (
            nombre_personalizado 
            or st.session_state.get("nombre_imagen") 
            or os.path.basename(imagen_path)
        )

        with open(imagen_path, "rb") as f:
            contenido_bytes = f.read()

        # Generar nombre único para el Storage preservando el nombre legible
        nombre_storage = f"{int(time.time())}_{nombre_base_real}"
        imagen_url = subir_imagen_galeria(nombre_storage, contenido_bytes)

        # Inyectar también la URL y el nombre en el master_json por si el reporte lo necesita
        if master_json and "metadata" in master_json:
            master_json["metadata"]["imagen_url"] = imagen_url
            master_json["metadata"]["nombre_pieza"] = nombre_base_real

        # 4. Estructurar el JSON completo de la tarjeta
        tarjeta_data = {
            "categoria": categoria_display,
            "filtro_key": str(tipo_analisis).lower() if tipo_analisis else "semiotico",
            "descripcion": descripcion,
            "modulo": modulo_txt,
            "master_json": master_json or {}
        }

        # 5. Persistir en la tabla galeria de PostgreSQL usando el nombre real
        guardar_analisis_en_galeria(
            titulo=nombre_base_real,
            categoria=categoria_display,
            imagen_url=imagen_url,
            master_json=tarjeta_data
        )

        return True
    except Exception as e:
        print(f"Error al registrar en Supabase: {e}")
        return False