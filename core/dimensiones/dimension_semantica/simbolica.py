from servicios.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría
PROMPTS_SIMBOLICOS = {
    "afiche": (
        "Analizá este afiche publicitario/comunicacional desde la perspectiva semiótica de Charles Peirce (Subcapa Simbólica). "
        "Identificá la carga cultural de los elementos visuales dominantes: las paletas de colores elegidas, los símbolos institucionales, "
        "los mitos sociales que evoca o las convenciones visuales utilizadas para persuadir o transmitir un mensaje directo al espectador."
    ),
    "logo": (
        "Analizá este logotipo/marca gráfica desde la perspectiva simbólica de Charles Peirce. "
        "Decodificá las convenciones culturales e institucionales de la marca. ¿Qué leyes visuales, conceptos abstractos, "
        "valores corporativos o significados sociales universales y regionales están codificados en sus formas y colores estructurados?"
    ),
    "ui": (
        "Analizá esta interfaz de usuario (UI) desde su dimensión simbólica. "
        "Identificá las convenciones culturales digitales y códigos de interacción establecidos (ej. el significado del color rojo para errores/urgencia, "
        "el verde para éxito/ecología, metáforas visuales de botones o jerarquías que el usuario ya entiende por convención social)."
    ),
    "general": (
        "Analizá esta pieza gráfica desde la perspectiva semiótica simbólica de Charles Peirce. "
        "Interpreta las convenciones culturales directas, leyes sociales, normas de vestimenta, disposición del entorno o códigos visuales "
        "y de color presentes, decodificando qué significan colectivamente para una sociedad."
    )
}

def analizar_semiotica_simbolica(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Simbólica (Peirce): Interpretación semántica basada en convenciones culturales y leyes sociales.
    Estructurada en tres niveles geográfico-culturales (ARG / LATAM / Global).
    """
    prompt_base = PROMPTS_SIMBOLICOS.get(categoria.lower(), PROMPTS_SIMBOLICOS["general"])
    
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN SEMÁNTICA SIMBÓLICA Y FIDELIDAD OBSERVACIONAL:
    Analizá la significación de la pieza considerando tres niveles de convención cultural:

    1. Contexto Local (Argentina):
       - Verificá si existen símbolos, banderas, marcas o códigos locales explícitamente presentes.
       - Si NO existen elementos o textos locales explícitos, responde ESTRICTAMENTE: "Sin elementos de la iconografía o cultura local argentina."
       - Queda PROHIBIDO inventar u opinar sobre influencias culturales de otros países en esta casilla.

    2. Contexto Regional (LATAM):
       - Identificá convenciones, tipologías o fenómenos visuales/culturales compartidos a escala latinoamericana.

    3. Contexto Global:
       - Evaluá significados universales, estándares internacionales de diseño o corrientes estilísticas de alcance global.

    REGLA GENERAL:
    Construye cada respuesta de manera fluida, breve y conceptual en una sola línea.
    Basá tus inferencias únicamente en lo visible en la imagen. No inventes ni asignes ubicaciones geográficas que no estén respaldadas por elementos gráficos o textuales presentes en la obra.

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_simbolico": {{
            "contexto_argentina": "Análisis explícito si hay símbolos argentinos visibles. Si no los hay, escribir exactamente: Sin elementos de la iconografía o cultura local argentina.",
            "contexto_latam": "Interpretación a nivel regional latinoamericano en una sola línea de texto.",
            "contexto_global": "Interpretación a nivel universal o global en una sola línea de texto."
        }}
    }}
    """
    
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    if "error" in resultado_vlm:
        return resultado_vlm
        
    return {
        "status": "success",
        "metrica": "Semiótica Simbólica (Peirce)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }