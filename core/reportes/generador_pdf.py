import os
import sys
from pathlib import Path

# Configuración de DLLs para Windows (MSYS2 / GTK)
if sys.platform == "win32":
    msys_bin = r"C:\msys64\ucrt64\bin"
    if os.path.exists(msys_bin):
        os.environ["PATH"] = msys_bin + ";" + os.environ["PATH"]
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(msys_bin)
            except Exception:
                pass

from weasyprint import HTML
from core.reportes.generador_html import renderizar_reporte_html

# Definimos la raíz principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def generar_reporte_pdf(master_json: dict, output_pdf_path: str) -> str:
    """Convierte el HTML renderizado directamente a un archivo PDF en disco."""
    # Aseguramos que el directorio de salida exista
    directorio_salida = os.path.dirname(output_pdf_path)
    if directorio_salida and not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida, exist_ok=True)

    html_content = renderizar_reporte_html(master_json)
    
    # WeasyPrint resuelve tanto Base64 como URLs públicas de Supabase
    HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(output_pdf_path)
    
    return output_pdf_path