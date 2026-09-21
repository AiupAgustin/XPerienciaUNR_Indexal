
import base64
import copy
import io
import os
import streamlit as st
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

# Funcion auxiliar para tamaño de imagenes verticales (y en general) en los reportes
def escalar_preview_proporcional(b64_str: str, max_w: int = 560, max_h: int = 360) -> str:
    """
    Escala la imagen respetando estrictamente su aspect ratio dentro de una caja
    segura para A4 (560px ancho x 360px alto), evitando desbordes y saltos de página en xhtml2pdf.
    """
    if not b64_str or not isinstance(b64_str, str):
        return b64_str

    try:
        # Extraemos los datos crudos en base64 quitando el prefijo data URI si existe
        if "," in b64_str:
            _, datos_b64 = b64_str.split(",", 1)
        elif b64_str.startswith("http://") or b64_str.startswith("https://"):
            return b64_str  # Si es URL remota sin procesar, se retorna intacta
        else:
            datos_b64 = b64_str

        img_bytes = base64.b64decode(datos_b64)
        with Image.open(io.BytesIO(img_bytes)) as img:
            img = img.convert("RGB")
            
            # thumbnail() NO deforma: calcula la proporción exacta para que
            # quepa dentro de max_w x max_h sin estirar ni achatarse
            img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            
            b64_escalado = base64.b64encode(buffer.read()).decode("utf-8").replace("\n", "").replace("\r", "")
            return f"data:image/jpeg;base64,{b64_escalado}"
    except Exception as e:
        print(f"Aviso: no se pudo reescalar el preview ({e}), usando imagen original.")
        return b64_str
    
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
    
    # 1. MÁXIMA PRIORIDAD: si el reporte ya tiene su imagen Base64 embebida en metadata, SE RESPETA INTACTA
    if metadata.get("imagen_b64") and str(metadata["imagen_b64"]).startswith("data:image/"):
        pass

    # 2. Si viene una URL pública de Supabase
    elif metadata.get("imagen_url"):
        metadata["imagen_b64"] = metadata["imagen_url"]

    # 3. Si viene una ruta o Data URI en imagen_path
    elif metadata.get("imagen_path"):
        ruta_img = str(metadata["imagen_path"])
        if ruta_img.startswith("data:image/"):
            metadata["imagen_b64"] = ruta_img
        else:
            # Intentamos resolver en disco
            ruta_abs = ruta_img
            if not os.path.isabs(ruta_abs):
                raiz_proyecto = Path(__file__).resolve().parent.parent.parent
                ruta_posible = raiz_proyecto / ruta_img.replace("\\", os.sep).replace("/", os.sep)
                if ruta_posible.exists():
                    ruta_abs = str(ruta_posible)
            
            if os.path.exists(ruta_abs):
                metadata["imagen_b64"] = imagen_a_base64(ruta_abs)
            else:
                # Si no existe en disco, solo recurrimos a la sesión si este reporte NO tenía su propio Base64
                if not metadata.get("imagen_b64") and st.session_state.get("imagen_bytes"):
                    raw_bytes = st.session_state["imagen_bytes"]
                    ext = st.session_state.get("imagen_extension", ".png").replace(".", "").lower()
                    mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
                    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
                    metadata["imagen_b64"] = f"data:image/{mime};base64,{b64_str}"

    # 4. Fallback de última instancia para un reporte nuevo que se está generando en caliente
    elif st.session_state.get("imagen_bytes"):
        raw_bytes = st.session_state["imagen_bytes"]
        ext = st.session_state.get("imagen_extension", ".png").replace(".", "").lower()
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        metadata["imagen_b64"] = f"data:image/{mime};base64,{b64_str}"

    # Asegurar nombre de la pieza en metadata si no vino seteado
    if not metadata.get("nombre_pieza") and ruta_img:
        nombre_crudo = ruta_img.split("?")[0]
        nombre_archivo = os.path.basename(nombre_crudo)
        if "_" in nombre_archivo and nombre_archivo.split("_", 1)[0].isdigit():
            metadata["nombre_pieza"] = nombre_archivo.split("_", 1)[1]
        else:
            metadata["nombre_pieza"] = nombre_archivo
        
    bloques = datos_render.get("bloques", [])
    convertir_todas_las_imagenes_a_b64(bloques)

    # Reescalado proporcional en píxeles reales exclusivo para la presentación visual
    if metadata.get("imagen_b64"):
        metadata["imagen_b64"] = escalar_preview_proporcional(metadata["imagen_b64"], max_w=560, max_h=360)
    
    return template.render(
        metadata=metadata,
        bloques=bloques
    )