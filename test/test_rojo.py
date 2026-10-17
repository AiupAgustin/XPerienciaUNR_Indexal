import base64
import json
from pathlib import Path
import sys
import cv2
import numpy as np

# Le dice a Python que busque módulos en la raíz del proyecto (un nivel arriba de /test)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ajustá el nombre exacto si tu archivo es 'rojo_lineas_tension' o 'rojo_linea_tension'
from graficos.rojo_linea_tension import analizar_lineas_tension

# 1. Rutas de prueba
# IMAGEN AUTO
RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\imagenes_lorena\synthwave.jpeg"

# IMAGEN SAXO
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\brcfotografiedigital-jazz-bar-8737486_1920.jpg"

# IMAGEN MODISTA
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\Sin título (2).jpg"

print("--- Ejecutando análisis de Tensión Vectorial (Kandinsky) ---")
res = analizar_lineas_tension(RUTA_IMAGEN)

# 2. Verificamos el estado
if res.get("status") == "error":
    print("Error en el análisis:", res.get("mensaje"))
else:
    resultado = res["resultado"]
    metricas = resultado["metricas_analiticas"]
    zonas = resultado["descripcion_textual_zonas"]

    print("\n=== MÉTRICAS OBTENIDAS ===")
    print(json.dumps(metricas, indent=2, ensure_ascii=False))

    print("\n=== DIAGNÓSTICO SEMIÓTICO ===")
    print(json.dumps(zonas, indent=2, ensure_ascii=False))

    # 3. Decodificamos el Base64 a imagen física para inspección visual
    uri_b64 = resultado["path_imagen_overlay"]
    if uri_b64 and "," in uri_b64:
        header, encoded = uri_b64.split(",", 1)
        img_bytes = base64.b64decode(encoded)

        nparr = np.frombuffer(img_bytes, np.uint8)
        # IMREAD_UNCHANGED conserva el canal alfa (transparencia)
        img_resultado = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        cv2.imwrite("test_resultado_rojo.png", img_resultado)
        print("\n¡Listo! Imagen generada guardada como 'test_resultado_rojo.png'.")
    else:
        print("\nAtención: No se generó la cadena Base64 del overlay.")