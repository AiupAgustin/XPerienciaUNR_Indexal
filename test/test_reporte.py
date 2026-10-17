import os
import sys
from pathlib import Path

# Registramos la raíz del proyecto en sys.path para resolver imports internos
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Carga de DLLs para WeasyPrint en Windows
os.add_dll_directory(r"C:\msys64\ucrt64\bin")

# Módulos de reportes
from core.reportes.orquestador import compilar_datos_reporte
from core.reportes.generador_pdf import generar_reporte_pdf

# Mapas de checkboxes de las categorías
from core.categorias.cat0_analisis_semiotico import MAPA_CHECKBOXES_CAT0
from core.categorias.cat5_ui_ux import MAPA_CHECKBOXES_CAT5

# Unificación de mapas en el mapa global
MAPA_GLOBAL = {**MAPA_CHECKBOXES_CAT0, **MAPA_CHECKBOXES_CAT5}

if __name__ == "__main__":
    # Define la ruta a tu imagen de prueba
    imagen_path_obj = Path(r"C:\Users\Agus\Desktop\imagenes test Indexal\imagenes_lorena\synthwave.jpeg")

    if not imagen_path_obj.exists():
        print(f"❌ ERROR CRÍTICO: El archivo no existe en la ruta:\n{imagen_path_obj}")
        print("Por favor revisá el nombre de la imagen o la extensión (.jpg / .jpeg).")
        sys.exit(1)
    else:
        print(f"✅ Imagen encontrada correctamente: {imagen_path_obj.name}")

    imagen_test = str(imagen_path_obj)
    nombre_imagen = imagen_path_obj.stem
    
    # 1. Crear carpeta output/reportes si no existe
    reportes_dir = BASE_DIR / "output" / "reportes"
    reportes_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Definir la ruta de salida del PDF en la carpeta de reportes
    output_pdf = str(reportes_dir / f"reporte_{nombre_imagen}.pdf")

    # Selección de checkboxes para auditar (ej. Categoría 0)
    checkboxes_a_probar = list(MAPA_CHECKBOXES_CAT0.keys())

    print("=== INICIANDO AUDITORÍA Y GENERACIÓN DE REPORTE ===")
    
    # Compilación de analíticas (pasando categoria_id=0 para que tome el título dinámico)
    master_json = compilar_datos_reporte(imagen_test, MAPA_GLOBAL, checkboxes_a_probar, categoria_id=0)

    if "metadata" not in master_json:
        master_json["metadata"] = {}
            
    master_json["metadata"]["imagen_path"] = imagen_test
    master_json["metadata"]["imagen_path_uri"] = imagen_path_obj.resolve().as_uri()
    
    # Generación de PDF
    print("-> Generando archivo PDF con WeasyPrint...")
    generar_reporte_pdf(master_json, output_pdf)
    
    print(f"\n¡Éxito! Reporte PDF listo en:\n{output_pdf}")

