### meter el funcionamiento de la ia y el servidor aca

import json
import ollama

def consultar_minicpm_v(imagen_path: str, prompt: str) -> dict:
    """
    Centraliza la infraestructura de la IA de forma local.
    Procesa la imagen usando Qwen2 local a través de Ollama,
    retornando siempre un diccionario estandarizado.
    """
    try:
        # Llamada directa al servicio local de Ollama usando el modelo que descargaste
        response = ollama.chat(
            model="minicpm-v",
            format="json",  # Forzamos a nivel motor que la salida sea JSON válido
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [imagen_path]  # Ollama se encarga de leer la ruta local directamente
                }
            ],
            options={
                "temperature": 0.1,       # Reduce la creatividad para evitar que invente caracteres
                "num_predict": 1024,       # Limita la cantidad de tokens para que no se extienda infinitamente
                "stop": ["叠"]     # Forzamos el freno si intenta repetir ese caracter
            }
        )
        
        respuesta_raw = response["message"]["content"]
        
    except Exception as e:
        return {
            "error": "Error al conectar con el servicio local de Ollama. ¿Está ejecutándose?",
            "details": str(e)
        }
    
    # Formateo y estandarización del resultado a diccionario (Mantenemos tu limpiador intacto)
    try:
        respuesta_limpia = respuesta_raw.strip()
        if respuesta_limpia.startswith("```"):
            lines = respuesta_limpia.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                respuesta_limpia = "\n".join(lines[1:-1]).strip()
                
        return json.loads(respuesta_limpia)
    except json.JSONDecodeError:
        return {
            "error": "El modelo local no devolvió un formato JSON válido.",
            "raw_response": respuesta_raw
        }