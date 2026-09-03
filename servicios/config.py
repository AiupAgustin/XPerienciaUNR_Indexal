### meter el funcionamiento de la ia y el servidor aca

import base64
import json
import time
import cv2
import numpy as np
import requests
import streamlit as st


# ==========================================================
# DEFINICIÓN GLOBAL DE CREDENCIALES
# ==========================================================
try:
    RUNPOD_API_KEY = st.secrets["RUNPOD_API_KEY"]
    RUNPOD_ENDPOINT_ID = st.secrets["RUNPOD_ENDPOINT_ID"]
except Exception:
    import toml

    secrets = toml.load(".streamlit/secrets.toml")
    RUNPOD_API_KEY = secrets["RUNPOD_API_KEY"]
    RUNPOD_ENDPOINT_ID = secrets["RUNPOD_ENDPOINT_ID"]

BASE_URL = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}"
HEADERS = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json",
}

# Funcion para que OpenCV pueda leer imágenes con rutas que contengan caracteres especiales en Windows
def imread_unicode(path: str, flags: int = cv2.IMREAD_COLOR) -> np.ndarray | None:
    """
    Lee una imagen utilizando un buffer de numpy para evitar fallos de lectura
    con rutas que contengan caracteres especiales (ñ, acentos, espacios) en Windows.
    """
    try:
        buffer = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(buffer, flags)
        return img
    except Exception as e:
        print(f"Error al cargar la imagen desde '{path}': {e}")
        return None

def imagen_a_base64(imagen_path: str) -> str:
    """Lee una imagen desde disco (incluso con caracteres especiales en Windows)

    y la convierte a un string Base64.
    """
    with open(imagen_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# ==========================================================
# INFERENCIA EN RUNPOD SERVERLESS
# ==========================================================
def consultar_minicpm_v(
    imagen_path: str, prompt: str, timeout_total: int = 240
) -> dict:
    """Envía la imagen y el prompt a RunPod Serverless para procesar con MiniCPM-V-2_6.

    Sondea el estado hasta que finalice y retorna un diccionario con el JSON
    limpio.
    """
    try:
        # 1. Convertir la imagen a base64
        image_b64 = imagen_a_base64(imagen_path)

        # 2. Despachar tarea asíncrona (/run)
        payload = {
            "input": {
                "prompt": prompt,
                "image_base64": image_b64,  # Clave exacta que espera handler.py
            }
        }

        resp = requests.post(
            f"{BASE_URL}/run", headers=HEADERS, json=payload, timeout=15
        )
        resp.raise_for_status()
        data = resp.json()

        job_id = data.get("id")
        status = data.get("status")

        if not job_id:
            return {
                "error": "RunPod no devolvió un ID de tarea válido.",
                "details": data,
            }

        # 3. Bucle de sondeo (polling) de la tarea
        inicio = time.time()
        while status in ["IN_QUEUE", "IN_PROGRESS"]:
            if time.time() - inicio > timeout_total:
                return {
                    "error": f"Tiempo de espera agotado ({timeout_total}s) esperando al worker de RunPod."
                }

            time.sleep(2.5)  # Intervalo de consulta liviano
            status_resp = requests.get(
                f"{BASE_URL}/status/{job_id}", headers=HEADERS, timeout=10
            )
            status_resp.raise_for_status()
            data = status_resp.json()
            status = data.get("status")

        # 4. Validar resultado
        if status == "COMPLETED":
            output_obj = data.get("output", {})

            # handler.py devuelve {"response": "..."}
            if isinstance(output_obj, dict) and "response" in output_obj:
                respuesta_raw = output_obj["response"]
            elif isinstance(output_obj, str):
                respuesta_raw = output_obj
            else:
                respuesta_raw = str(output_obj)
        else:
            return {
                "error": f"La tarea falló en RunPod con estado: {status}",
                "details": data.get("error", data),
            }

    except requests.exceptions.RequestException as e:
        return {
            "error": "Error de conexión HTTP con RunPod Serverless.",
            "details": str(e),
        }
    except Exception as e:
        return {
            "error": "Error inesperado durante la ejecución en RunPod.",
            "details": str(e),
        }

    # 5. Formateo y estandarización del resultado a diccionario JSON
    try:
        respuesta_limpia = respuesta_raw.strip()

        # Quita delimitadores de código markdown si el modelo los agrega
        if respuesta_limpia.startswith("```"):
            lines = respuesta_limpia.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                respuesta_limpia = "\n".join(lines[1:-1]).strip()

        # Si el modelo devolvió texto libre que incluye JSON entre medio
        inicio_json = respuesta_limpia.find("{")
        fin_json = respuesta_limpia.rfind("}")
        if inicio_json != -1 and fin_json != -1:
            respuesta_limpia = respuesta_limpia[inicio_json : fin_json + 1]

        return json.loads(respuesta_limpia)

    except json.JSONDecodeError:
        return {
            "error": "El modelo no devolvió un formato JSON válido.",
            "raw_response": respuesta_raw,
        }

