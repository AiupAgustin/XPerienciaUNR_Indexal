import os
from pathlib import Path
from xhtml2pdf import pisa
from core.reportes.generador_html import renderizar_reporte_html

# Raíz principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def generar_reporte_pdf(master_json: dict, output_pdf_path: str) -> str:
    """Convierte el HTML renderizado directamente a un archivo PDF en disco usando xhtml2pdf."""
    directorio_salida = os.path.dirname(output_pdf_path)
    if directorio_salida and not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida, exist_ok=True)

    html_content = renderizar_reporte_html(master_json)

    with open(output_pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
            src=html_content, dest=pdf_file, path=str(BASE_DIR)
        )

    if pisa_status.err:
        raise RuntimeError(
            f"Error al generar el PDF con xhtml2pdf: código {pisa_status.err}"
        )

    return output_pdf_path