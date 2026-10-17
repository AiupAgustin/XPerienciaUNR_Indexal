import base64
import json
from pathlib import Path
import sys
import cv2
import numpy as np

# Agrega la raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graficos.azul_peso_visual import analizar_peso_visual

# 1. Definición de la ruta a la imagen de prueba real

# imagen de auto
RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\imagenes_lorena\synthwave.jpeg"

# imagen saxofon
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\brcfotografiedigital-jazz-bar-8737486_1920.jpg"

# imagen de modista
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\Sin título (2).jpg"

# imagen blanco y negro
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\correcciones entrega 21-9\boulder-dam-1941.jpg!Large.jpg"

print("--- Ejecutando análisis de Peso Visual / Momentos e Inercia (Indexal Azul) ---")
res = analizar_peso_visual(RUTA_IMAGEN)

# 2. Verificación del estado
if res.get("status") == "error":
    print("Error en el análisis:", res.get("mensaje"))
else:
    resultado = res["resultado"]
    metricas = resultado["metricas_analiticas"]
    diagnostico = resultado["descripcion_textual"]

    print("\n=== MÉTRICAS OBTENIDAS ===")
    print(json.dumps(metricas, indent=2, ensure_ascii=False))

    print("\n=== DIAGNÓSTICO DE BALANCE Y PESO ===")
    print(json.dumps(diagnostico, indent=2, ensure_ascii=False))

    # 3. Decodificación del Base64 preservando transparencia
    uri_b64 = resultado["path_imagen_overlay"]
    if uri_b64 and "," in uri_b64:
        header, encoded = uri_b64.split(",", 1)
        img_bytes = base64.b64decode(encoded)

        nparr = np.frombuffer(img_bytes, np.uint8)
        img_resultado = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        cv2.imwrite("test_resultado_azul.png", img_resultado)
        print("\n¡Listo! Imagen generada guardada como 'test_resultado_azul.png'.")
    else:
        print("\nAtención: No se generó la cadena Base64 del overlay.")