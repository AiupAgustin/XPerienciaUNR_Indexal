from core.categorias.config import consultar_minicpm_v

PROMPTS_TIPOGRAFICA = {
    "afiche": "Analizá el contraste visual y la legibilidad entre el titular y el texto secundario de este afiche.",
    "logo": "Analizá la tipografía del logotipo e identificá si transmite tradición, modernidad, elegancia o tecnología.",
    "ui": "Analizá la jerarquía visual y la legibilidad en pantalla (altura de x) de esta interfaz.",
    "general": "Analizá los aspectos tipográficos, familias presentes y su maridaje semántico en la imagen."
}

def analizar_tipografia(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Tipográfica: Analiza familias tipográficas y jerarquía visual.
    """
    prompt_base = PROMPTS_TIPOGRAFICA.get(categoria.lower(), PROMPTS_TIPOGRAFICA["general"])
    
    prompt_final = f"""
    {prompt_base}

    INSTRUCCIONES CRÍTICAS:
    1. Responde ÚNICAMENTE en idioma Español.
    2. NO transcribas texto ni nombres de la imagen (NO hagas OCR).
    3. En 'clasificacion_formal', usa SOLO estos términos:
       - Familias: Sans-Serif, Serif, Script, Display, Monospaced.
       - Estilos: Geométrica, Humanista, Grotesca, Condensada, Modulada.

    Responde EXCLUSIVAMENTE con esta estructura JSON sin agregar campos extra:

    {{
        "analisis_tipografico": {{
            "clasificacion_formal": "Titular: <Familia> <Estilo> | Secundario: <Familia> <Estilo>",
            "connotacion_semantica": "Breve explicación de las sensaciones o valores que transmite la tipografía.",
            "altura_de_x_y_legibilidad": "Evaluación cualitativa de legibilidad y proporciones.",
            "maridaje_y_jerarquia": "Análisis del contraste, tamaño y relación entre fuentes."
        }}
    }}
    """
    
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    if "error" in resultado_vlm:
        return resultado_vlm
        
    return {
        "status": "success",
        "metrica": "Análisis Tipográfico",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }