
import base64
import copy
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))


def imagen_a_base64(ruta_imagen: str) -> str:
    """Lee una imagen del disco y la convierte a data URI en base64."""
    if not ruta_imagen or not isinstance(ruta_imagen, str):
        return ""
    
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
    ruta_img = metadata.get("imagen_path", "")
    if ruta_img:
        metadata["imagen_b64"] = imagen_a_base64(ruta_img)
        
    bloques = datos_render.get("bloques", [])
    convertir_todas_las_imagenes_a_b64(bloques)
    
    return template.render(
        metadata=metadata,
        bloques=bloques
    )