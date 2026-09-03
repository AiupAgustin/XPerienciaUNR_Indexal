import runpod
import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import base64
import io

print("Cargando modelo MiniCPM-V-2_6...")

device = "cuda" if torch.cuda.is_available() else "cpu"

model_name = "openbmb/MiniCPM-V-2_6"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    attn_implementation="sdpa"
)
model.eval()

print("Modelo cargado con éxito en GPU.")


def decode_image_from_base64(b64_string: str) -> Image.Image:
    """Convierte una cadena en Base64 a un objeto PIL Image."""
    if "," in b64_string:
        b64_string = b64_string.split(",")[1]
    image_bytes = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def handler(job):
    job_input = job.get("input", {})

    prompt = job_input.get("prompt", "¿Qué ves en esta imagen?")
    image_b64 = job_input.get("image_base64")

    if not image_b64:
        return {"error": "Falta el campo 'image_base64' en el payload de entrada."}

    try:
        image = decode_image_from_base64(image_b64)
        
        msgs = [{'role': 'user', 'content': [image, prompt]}]
        
        with torch.no_grad():
            res = model.chat(
                image=None,
                msgs=msgs,
                tokenizer=tokenizer,
                sampling=True,
                temperature=0.2,
                max_new_tokens=1024
            )

        return {"response": res}

    except Exception as e:
        return {"error": str(e)}


runpod.serverless.start({"handler": handler})