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
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español.
    No incluyas preámbulos, notas ni bloques markdown auxiliares fuera del JSON.

    METODOLOGÍA DE ANÁLISIS EN DOS FASES:

    FASE 1 — INVENTARIO DE EVIDENCIA VISUAL:
    Examina minuciosamente la imagen e identifica cualquier significante gráfico o cultural concreto:
    - Banderas, escarapelas, soles, escudos, emblemas nacionales o colores patrios.
    - Objetos y rituales cotidianos (recipientes de infusión tradicionales, vestimenta típica, herramientas).
    - Hitos geográficos, cordilleras, flora, fauna autóctona o arquitectura representativa.

    FASE 2 — DECODIFICACIÓN SIMBÓLICA (COHERENCIA OBLIGATORIA):
    1. Contexto Local (Argentina):
       - Si en la FASE 1 detectaste símbolos o prácticas vinculadas a Argentina (por ejemplo colores celeste/blanco, sol figurativo, infusión de mate, etc.), explica con precisión qué representan en su cultura.
       - Solo si la FASE 1 carece por completo de signos vinculables, indica: "Sin elementos de la iconografía o cultura local argentina."

    2. Contexto Regional (Latinoamérica):
       - Si la imagen contiene símbolos compartidos, paisajes andinos/tropicales, fauna regional o banderas de países latinoamericanos, detalla el anclaje identitario regional.
       - Si es una pieza completamente abstracta o de otra región sin anclaje, indica: "Sin anclaje visual o cultural específico de la región latinoamericana."

    3. Contexto Global (Simbólico / Connotativo):
       - Explica los valores universales, ideas abstractas o conceptos humanos que evoca la pieza (ej. integración, libertad, diversidad, hospitalidad, tradición).
       - REGLA DE CONSISTENCIA: Si en el contexto global mencionas que la obra representa a América Latina o a naciones específicas, esto DEBE estar respaldado y desarrollado en los campos locales/regionales previos, sin contradecirse.

    ESTRUCTURA EXACTA DEL JSON:
    {{
        "evidencia_visual": "Breve lista de elementos o símbolos visuales concretos detectados",
        "analisis_simbolico": {{
            "contexto_argentina": "Interpretación cultural si hay elementos argentinos; si no, 'Sin elementos de la iconografía o cultura local argentina.'",
            "contexto_latam": "Interpretación regional si hay elementos latinoamericanos; si no, 'Sin anclaje visual o cultural específico de la región latinoamericana.'",
            "contexto_global": "Valores abstractos, connotaciones universales o mitos sociales globales que evoca la pieza."
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