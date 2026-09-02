
import base64
import copy
import os
import streamlit as st
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))


def imagen_a_base64(ruta_imagen: str) -> str:
    """Lee una imagen del disco y la convierte a data URI en base64, o devuelve la URL/Base64 intacta."""
    if not ruta_imagen or not isinstance(ruta_imagen, str):
        return ""

    # Si ya es una URL web (Supabase) o ya viene codificada en Base64, se devuelve tal cual
    if ruta_imagen.startswith("http://") or ruta_imagen.startswith("https://") or ruta_imagen.startswith("data:image/"):
        return ruta_imagen
    
    # Manejamos rutas relativas y absolutas
    ruta_limpia = ruta_imagen.replace("\\", os.sep).replace("/", os.sep)
    if not os.path.isabs(ruta_limpia):
        # Si es relativa, buscamos desde la raíz del proyecto
        raiz_proyecto = Path(__file__).resolve().parent.parent.parent
        ruta_posible = raiz_proyecto / ruta_limpia
        if ruta_posible.exists():
            ruta_limpia = str(ruta_posible)

    if not os.path.exists(ruta_limpia):
        return ruta_imagen  # Retorna el original si no existe
    
    ext = os.path.splitext(ruta_limpia)[1].lower().replace(".", "")
    if ext not in ["png", "jpg", "jpeg", "webp"]:
        return ruta_imagen
        
    mime_type = "jpeg" if ext in ["jpg", "jpeg"] else ext
    
    try:
        with open(ruta_limpia, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/{mime_type};base64,{encoded}"
    except Exception as e:
        print(f"Error convirtiendo imagen {ruta_imagen} a base64: {e}")
        return ruta_imagen


def convertir_todas_las_imagenes_a_b64(obj):
    """Recorre recursivamente el diccionario y reemplaza cualquier ruta de imagen por su Base64."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and any(v.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"]):
                obj[k] = imagen_a_base64(v)
            elif isinstance(v, (dict, list)):
                convertir_todas_las_imagenes_a_b64(v)
    elif isinstance(obj, list):
        for item in obj:
            convertir_todas_las_imagenes_a_b64(item)


def renderizar_reporte_html(master_json: dict) -> str:
    """Toma el Master JSON, convierte todas las imágenes y heatmaps a Base64 y compila Jinja2."""
    template = env.get_template("reporte_template.html")
    
    # Copia profunda para no mutar el JSON en sesión
    datos_render = copy.deepcopy(master_json)
    
    metadata = datos_render.get("metadata", {})
    
    # 1. Si tenemos los bytes directos en la sesión activa, generamos el Base64 en memoria instantáneamente
    if st.session_state.get("imagen_bytes"):
        raw_bytes = st.session_state["imagen_bytes"]
        ext = st.session_state.get("imagen_extension", ".png").replace(".", "").lower()
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        metadata["imagen_b64"] = f"data:image/{mime};base64,{b64_str}"
        
    # 2. Si no hay bytes en sesión pero tenemos la URL pública de Supabase, la usamos directamente
    elif metadata.get("imagen_url"):
        metadata["imagen_b64"] = metadata["imagen_url"]
        
    # 3. Fallback habitual
    else:
        ruta_img = metadata.get("imagen_path", "")
        if ruta_img:
            metadata["imagen_b64"] = imagen_a_base64(ruta_img)
        
        # Extraer y limpiar el nombre de la pieza analizada (elimina el timestamp inicial y URLs)
        nombre_crudo = ruta_img.split("?")[0]
        nombre_archivo = os.path.basename(nombre_crudo)
        if "_" in nombre_archivo and nombre_archivo.split("_", 1)[0].isdigit():
            metadata["nombre_pieza"] = nombre_archivo.split("_", 1)[1]
        else:
            metadata["nombre_pieza"] = nombre_archivo
        
    bloques = datos_render.get("bloques", [])
    convertir_todas_las_imagenes_a_b64(bloques)
    
    return template.render(
        metadata=metadata,
        bloques=bloques
    )