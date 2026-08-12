from pathlib import Path
from weasyprint import HTML
from core.reportes.generador_html import renderizar_reporte_html

# Definimos la raíz principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def generar_reporte_pdf(master_json: dict, output_pdf_path: str) -> str:
    """Convierte el HTML renderizado directamente a un archivo PDF en disco."""
    html_content = renderizar_reporte_html(master_json)
    
    # Se pasa la ruta absoluta de BASE_DIR convertida a string o URI
    HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(output_pdf_path)
    
    return output_pdf_path