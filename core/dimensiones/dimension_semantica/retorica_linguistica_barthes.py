from servicios.config import consultar_minicpm_v

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
        "REGLA ESTRICTA DE FIDELIDAD TIPOGRÁFICA:\n"
        "1. Verificá si existen letras, palabras o texto gráfico escrito explícitamente dibujado o impreso en la imagen.\n"
        "2. Si NO hay texto escrito explícito en la imagen, NO inventes, traduzcas, ni hagas descripciones de lo que ves en la foto como si fuera texto.\n"
        "3. Si identificás texto escrito real, extraelo mediante OCR y evalúa su relación retórica (Anclaje o Relevo)."
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

    INSTRUCCIÓN SEMÁNTICA DE VERIFICACIÓN TIPOGRÁFICA Y BARTHES:
    1. 'texto_principal': Transcribe ÚNICAMENTE el texto o caracteres tipográficos impresos en la imagen. Queda ESTRICTAMENTE PROHIBIDO describir elementos visuales u objetos de la escena en este campo. Si no hay letras o palabras escritas en la imagen, responde exactamente: "Sin texto visible".
    2. 'textos_secundarios': Transcribe textos accesorios o legales secundarios. Si no hay, responde: "Sin texto secundario".
    3. 'funcion_linguistica': EVALUACIÓN CONDICIONAL ESTRICTA:
       - Si 'texto_principal' es "Sin texto visible", este campo DEBE SER OBLIGATORIAMENTE: "Sin texto (Ausente)". Queda ESTRICTAMENTE PROHIBIDO responder "Anclaje" o "Relevo" si no hay texto.
       - Si SI hay texto transcrito, elige únicamente entre "Anclaje" o "Relevo".
    4. 'analisis_retorico': Si hay texto, explica en una sola línea cómo el texto fija o complementa el sentido. Si no hay texto, responde: "La pieza es de carácter puramente visual y prescinde de mensaje lingüístico escrito."

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_barthes": {{
            "texto_principal": "Transcripción del texto o 'Sin texto visible'",
            "textos_secundarios": "Transcripción de textos accesorios o 'Sin texto secundario'",
            "funcion_linguistica": "Anclaje / Relevo / Sin texto (Ausente)",
            "analisis_retorico": "Explicación en una sola línea sobre la relación del texto con la imagen o de la autonomía visual."
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