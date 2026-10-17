

from servicios.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría (Enfocados puramente en lo denotativo)
PROMPTS_ICONICOS = {
    "afiche": (
        "Analizá este afiche publicitario/comunicacional desde una perspectiva semiótica de Charles Peirce. "
        "Hacé una lista puramente denotativa y objetiva de los iconos y figuras del mundo real que aparecen "
        "(ej. siluetas humanas, objetos, productos, formas geométricas de fondo). "
        "No interpretes su significado oculto todavía, solo identificá QUÉ elementos explícitos componen la escena."
    ),
    "logo": (
        "Analizá este logotipo/marca gráfica desde la perspectiva icónica de Charles Peirce. "
        "Identificá si la marca se basa en un icono del mundo real (ej. una silueta de un animal, una tipografía modificada, "
        "un objeto abstracto o una forma geométrica pura). Describe formalmente la estructura de los elementos visuales base."
    ),
    "ui": (
        "Analizá esta interfaz de usuario (UI). Identificá los elementos icónicos y componentes visuales presentes "
        "(ej. iconos de navegación, cajas de texto, botones, avatares o contenedores). "
        "Clasificá estructuralmente qué figuras del mundo real o convenciones de interfaz componen la pantalla de forma objetiva."
    ),
    "general": (
        "Analizá esta pieza gráfica e identificá de manera puramente denotativa y objetiva todos los elementos, "
        "figuras, sujetos u objetos del mundo real que la componen. Describe qué se ve a simple vista sin interpretar significados."
    )
}

def analizar_semiotica_iconica(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Icónica (Peirce): Reconocimiento denotativo de figuras del mundo real.
    Agnóstica al proveedor gracias a la abstracción de config.py.
    """
    # Selección del prompt base según la categoría
    prompt_base = PROMPTS_ICONICOS.get(categoria.lower(), PROMPTS_ICONICOS["general"])
    
    # Inyección de instrucciones para descripción denotativa libre de sesgos y anti-pareidolia
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN VISUAL DENOTATIVA Y FIDELIDAD OBSERVACIONAL (ANTI-PAREIDOLIA):
    Describe de forma directa, en una sola oración breve y con palabras simples, qué objetos y formas componen esta imagen de forma estrictamente visible y verificable.
    
    REGLAS DE RESTRICCIÓN:
    1. CERO PAREIDOLIA Y FIDELIDAD OBSERVACIONAL:
       - No asignes identidades, rostros ni objetos basados en manchas, sombras, texturas de pelaje o pliegues ambiguos.
       - Solo reporta objetos, prendas o accesorios si son físicamente discernibles de manera clara, completa e independiente del fondo o del sujeto (no confundir patrones corporales, manchas de pigmentación o sombras con objetos añadidos).
       - Si una figura es deforme, ambigua o surrealista, descríbela por su morfología neutra ('figura abstracta', 'forma biomórfica') sin forzar asociaciones.
    2. CERTEZA DENOTATIVA:
       - Limítate estrictamente a lo indiscutible. Ante la mínima duda o ambigüedad sobre si un detalle es un objeto o una textura natural, limítate a describir el sujeto principal y su entorno.
    3. REGLA ESTRUCTURAL:
       - NO utilices números, no cuentes elementos y no agregues interpretaciones simbólicas ni metáforas.

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_denotativo": "Descripción objetiva de los objetos indudables y formas observables en una sola línea de texto."
    }}
    """
    
    # Consumo de la infraestructura centralizada
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    
    if "error" in resultado_vlm:
        return resultado_vlm

    resultado_formateado = {
        "Análisis Denotativo": resultado_vlm.get("analisis_denotativo", "")
    }

    return {
        "status": "success",
        "metrica": "Semiótica Icónica (Peirce)",
        "categoria_evaluada": categoria,
        "resultado": resultado_formateado
    }