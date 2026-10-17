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
       - Verificá si existen símbolos, banderas, marcas, tipografías o iconografía local argentina explícitamente observables.
       - Si NO existen elementos locales explícitos, responde ESTRICTAMENTE: "Sin elementos de la iconografía o cultura local argentina."
       - Queda PROHIBIDO asumir o inventar influencias sin evidencia visual directa.

    2. Contexto Regional (LATAM):
       - Verificá si existen rasgos culturales, iconográficos, lingüísticos o convenciones visuales propias y exclusivas de Latinoamérica.
       - Si la imagen representa un objeto genérico, neutro, global o sin marcadores latinoamericanos directos (por ejemplo vehículos genéricos, molinos eólicos globales, paisajes no identificados), responde ESTRICTAMENTE: "Sin anclaje visual o cultural específico de la región latinoamericana."
       - Queda TERMINANTEMENTE PROHIBIDO forzar asociaciones abstractas (como generalizar tecnologías, objetos cotidianos o industrias globales a Latinoamérica).

   3. Contexto Global (Simbólico / Connotativo):
       - Queda PROHIBIDO limitarse a describir los objetos presentes o la escena (eso corresponde al nivel icónico/denotativo).
       - Interpretá EXCLUSIVAMENTE los significados abstractos, valores universales, conceptos culturales o mitos sociales que el signo evoca a nivel global (ej. libertad, aventura, domesticación, afecto, compañía, modernidad).

    REGLA GENERAL:
    Construye cada respuesta de manera fluida, breve y conceptual en una sola línea.
    Basá tus inferencias únicamente en lo visible en la imagen. No inventes ni asignes ubicaciones geográficas que no estén respaldadas por elementos gráficos o textuales presentes en la obra.

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_simbolico": {{
            "contexto_argentina": "Análisis si hay elementos argentinos observables. Si no, escribir exactamente: Sin elementos de la iconografía o cultura local argentina.",
            "contexto_latam": "Análisis si hay elementos latinoamericanos observables. Si no, escribir exactamente: Sin anclaje visual o cultural específico de la región latinoamericana.",
            "contexto_global": "Valores abstractos, connotaciones culturales universales o conceptos simbólicos globales que evoca la pieza. PROHIBIDO describir físicamente la escena."
        }}
    }}
    """
    
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    if "error" in resultado_vlm:
        return resultado_vlm

    datos_simbolicos = resultado_vlm.get("analisis_simbolico", {})

    resultado_formateado = {
        "Análisis Simbólico": {
            "Contexto Argentina": datos_simbolicos.get("contexto_argentina", ""),
            "Contexto Latinoamérica": datos_simbolicos.get("contexto_latam", ""),
            "Contexto Global": datos_simbolicos.get("contexto_global", "")
        }
    }

    return {
        "status": "success",
        "metrica": "Semiótica Simbólica (Peirce)",
        "categoria_evaluada": categoria,
        "resultado": resultado_formateado
    }