import base64
import json
import cv2
import numpy as np
import sys
from pathlib import Path

# Le dice a Python que busque módulos en la raíz del proyecto (un nivel arriba de /test)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ajustá el import según la carpeta donde ubicaste amarillo_gradiente_cromatico.py
from graficos.amarillo_gradiente_cromatico import analizar_gradiente_cromatico

# 1. Definí la ruta a la imagen de prueba real
# FOTO AUTO
RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\imagenes_lorena\synthwave.jpeg"

# FOTO SAXO
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\brcfotografiedigital-jazz-bar-8737486_1920.jpg"

# FOTO MODISTA
#RUTA_IMAGEN = r"C:\Users\Agus\Desktop\Xperiencia UNR\Archivos y documentos del proceso\Imagenes de prueba\imagenes test Indexal\Sin título (2).jpg"

print("--- Ejecutando análisis de Gradiente Cromático / Focos de Color (Indexal Amarillo #FEF9C3) ---")
res = analizar_gradiente_cromatico(RUTA_IMAGEN)

# 2. Verificamos el estado
if res.get("status") == "error":
    print("Error en el análisis:", res.get("mensaje"))
else:
    resultado = res["resultado"]
    metricas = resultado["metricas_analiticas"]
    diagnostico = resultado["descripcion_textual"]

    print("\n=== MÉTRICAS OBTENIDAS ===")
    print(json.dumps(metricas, indent=2, ensure_ascii=False))

    print("\n=== DIAGNÓSTICO CROMÁTICO Y TEMPERATURA ===")
    print(json.dumps(diagnostico, indent=2, ensure_ascii=False))

    # 3. Decodificamos el Base64 a imagen física para inspección visual
    uri_b64 = resultado["path_imagen_overlay"]
    if uri_b64 and "," in uri_b64:
        header, encoded = uri_b64.split(",", 1)
        img_bytes = base64.b64decode(encoded)

        nparr = np.frombuffer(img_bytes, np.uint8)
        img_resultado = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        # Guardamos una copia local para abrirla y ver las bandas y escalones cromáticos
        cv2.imwrite("test_resultado_amarillo.png", img_resultado)
        print("\n¡Listo! Imagen generada guardada como 'test_resultado_amarillo.png'.")
    else:
        print("\nAtención: No se generó la cadena Base64 del overlay.")