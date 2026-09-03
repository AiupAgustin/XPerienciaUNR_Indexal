import base64
from io import BytesIO
import time
from PIL import Image
import requests
import toml

secrets = toml.load(".streamlit/secrets.toml")
api_key = secrets["RUNPOD_API_KEY"]
endpoint_id = secrets["RUNPOD_ENDPOINT_ID"]

base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Generar una imagen de prueba válida (448x448 en RGB)
img = Image.new("RGB", (448, 448), color=(73, 109, 137))
buffered = BytesIO()
img.save(buffered, format="JPEG")
valid_image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

payload = {
    "input": {
        "prompt": "¿Qué color predomina en esta imagen?",
        "image_base64": valid_image_b64,
    }
}

print("1. Despachando tarea asíncrona a RunPod (/run)...")
resp = requests.post(f"{base_url}/run", headers=headers, json=payload, timeout=15)
data = resp.json()

job_id = data.get("id")
status = data.get("status")
print(f"ID de tarea asignado: {job_id} | Estado inicial: {status}")

inicio = time.time()
while status in ["IN_QUEUE", "IN_PROGRESS"]:
    transcurrido = int(time.time() - inicio)
    print(f"[{transcurrido}s] Procesando en GPU (estado: {status})...")
    time.sleep(3)

    status_resp = requests.get(
        f"{base_url}/status/{job_id}", headers=headers, timeout=10
    )
    data = status_resp.json()
    status = data.get("status")

print("\n--- Tarea Finalizada ---")
print(f"Status final: {status}")
if status == "COMPLETED":
    print("Respuesta de MiniCPM-V:", data.get("output"))
else:
    print("Detalle de fallo/cancelación:", data)