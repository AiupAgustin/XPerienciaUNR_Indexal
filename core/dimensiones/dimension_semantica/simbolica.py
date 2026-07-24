from core.categorias.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría (Enfocados en convenciones culturales y leyes semánticas)
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
    # Selección del prompt base según la categoría
    prompt_base = PROMPTS_SIMBOLICOS.get(categoria.lower(), PROMPTS_SIMBOLICOS["general"])
    
    # Inyección de instrucciones semánticas y de estructura abstracta regional
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN SEMÁNTICA SIMBÓLICA:
    Interpreta el significado de los elementos identificados dividiéndolo explícitamente según el alcance de la convención cultural en tres niveles obligatorios:
    1. Regional (Argentina): Códigos específicos de la cultura, costumbres, modismos visuales o entorno argentino.
    2. LATAM: Convenciones o realidades socio-culturales compartidas a nivel latinoamericano.
    3. Global: Significados universales, occidentales estandarizados o leyes de diseño internacionales.

    Construye cada respuesta de manera fluida, breve y conceptual en una sola línea (Ejemplo de estructura abstracta: 'El elemento A connota B bajo la convención C'). 
    NO inventes interpretaciones si la imagen no presenta símbolos claros; en su defecto, analiza la disposición cultural general de los objetos cotidianos visibles. No copies palabras del ejemplo de estructura.

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_simbolico": {{
            "contexto_argentina": "Interpretación a nivel local argentino en una sola línea de texto.",
            "contexto_latam": "Interpretación a nivel regional latinoamericano en una sola línea de texto.",
            "contexto_global": "Interpretación a nivel universal o global en una sola línea de texto."
        }}
    }}
    """
    
    # Consumo de la infraestructura centralizada
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    
    if "error" in resultado_vlm:
        return resultado_vlm
        
    
    return {
        "status": "success",
        "metrica": "Semiótica Simbólica (Peirce)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }