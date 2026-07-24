from core.categorias.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría (Enfocados en el mensaje lingüístico de Barthes)
PROMPTS_BARTHES = {
    "afiche": (
        "Analizá el texto presente en este afiche. Realizá un OCR del texto visible y analizá si cumple una función de "
        "Anclaje (fija el sentido publicitario/comunicacional reduciendo la polisemia de la imagen) "
        "o Relevo (añade información narrativa o secundaria que la imagen no muestra por sí sola)."
    ),
    "logo": (
        "Analizá el texto tipográfico presente en este logotipo/isologo. Transcribí el texto visible "
        "y determiná si actúa como Anclaje (identificando/nombrando la marca de forma unívoca) "
        "o Relevo (añadiendo un slogan o descriptivo comercial que amplía la narrativa del símbolo)."
    ),
    "ui": (
        "Analizá los elementos textuales (microcopy, etiquetas, botones) de esta interfaz de usuario (UI). "
        "Transcribí los textos clave e identificá si funcionan como Anclaje (instrucciones claras para fijar la acción del usuario) "
        "o Relevo (textos informativos que avanzan el flujo de la interacción digital)."
    ),
    "general": (
        "Analizá el mensaje lingüístico (texto) presente en la imagen desde la teoría semiótica de Roland Barthes. "
        "Extrae el texto mediante OCR y evalúa su relación retórica con la imagen (Anclaje o Relevo)."
    )
}

def analizar_retorica_barthes(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Retórica y Lingüística (Barthes): OCR de texto visible y análisis de función 
    semántica (Anclaje vs. Relevo) según la interacción texto-imagen.
    """
    # Selección del prompt base según la categoría
    prompt_base = PROMPTS_BARTHES.get(categoria.lower(), PROMPTS_BARTHES["general"])
    
    # Inyección de instrucciones de Barthes y formato JSON estricto
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN SEMÁNTICA DE JERARQUÍA Y BARTHES:
    1. 'texto_principal': Transcribe ÚNICAMENTE el titular, slogan o texto dominante de la pieza. Ignora textos legales, sellos de advertencia, gramos o leyendas de 'sin conservantes'. Si no hay texto, responde: "Sin texto visible".
    2. 'textos_secundarios': Transcribe brevemente textos secundarios o legales detectados (ej. "Sin conservantes", sellos, legales). Si no hay, responde: "Ninguno".
    3. 'funcion_linguistica': Evalúa la función del 'texto_principal' respecto a la imagen eligiendo únicamente entre: "Anclaje", "Relevo" o "No aplica (Sin texto)".
    4. 'analisis_retorico': Explica en una sola línea cómo el texto principal fija el sentido de la imagen (Anclaje) o completa la narrativa (Relevo).

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_barthes": {{
            "texto_principal": "Transcripción del titular o slogan principal",
            "textos_secundarios": "Textos accesorios, legales o informativos secundarios",
            "funcion_linguistica": "Anclaje / Relevo / No aplica (Sin texto)",
            "analisis_retorico": "Explicación en una sola línea sobre la relación del texto principal con la imagen."
        }}
    }}
    """
    
    # Consumo del conector centralizado
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    # Propagación de errores
    if "error" in resultado_vlm:
        return resultado_vlm
        
   
    return {
        "status": "success",
        "metrica": "Retórica y Lingüística (Roland Barthes)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }