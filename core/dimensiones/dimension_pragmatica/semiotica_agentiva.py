
from servicios.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría (Clima, Emoción y Acción provocada)
PROMPTS_AGENTIVOS = {
    "afiche": (
        "Analizá este afiche publicitario/comunicacional desde la perspectiva de la Semiótica Agentiva. "
        "Determiná qué clima, emoción o acción busca provocar el artefacto en el espectador "
        "(ej. confianza, urgencia, rebeldía, concientización o llamado a la acción directo)."
    ),
    "logo": (
        "Analizá este logotipo/marca gráfica desde la perspectiva de la Semiótica Agentiva. "
        "Determiná qué clima, emoción o actitud busca provocar el artefacto en el consumidor "
        "(ej. confianza institucional, sentido de pertenencia, sofisticación, rebeldía o disrupción)."
    ),
    "ui": (
        "Analizá esta interfaz de usuario (UI) desde la perspectiva de la Semiótica Agentiva. "
        "Determiná qué clima, emoción o interacción busca provocar el artefacto en el usuario "
        "(ej. confianza en la transacción, urgencia de compra, fluidez, calma o seguridad visual)."
    ),
    "general": (
        "Analizá esta pieza gráfica desde la perspectiva de la Semiótica Agentiva. "
        "Determiná qué clima, emoción o acción busca provocar el artefacto en el receptor "
        "(ej. confianza, urgencia, rebeldía, empatía, curiosidad)."
    )
}

def analizar_semiotica_agentiva(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Semiótica Agentiva (Pragmática): Evalúa qué clima, emoción o acción
    busca provocar el artefacto gráfico (confianza, urgencia, rebeldía, etc.).
    """
    # Selección del prompt base según la categoría
    prompt_base = PROMPTS_AGENTIVOS.get(categoria.lower(), PROMPTS_AGENTIVOS["general"])
    
    # Inyección de instrucciones pragmáticas y de estructura JSON estricta
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN SEMÁNTICA AGENTIVA:
    Analiza la intención pragmática del artefacto visual respondiendo directamente a tres ejes clave:
    1. clima: El ambiente o atmósfera general que genera la pieza (ej. sofisticado, caótico, corporativo, festivo).
    2. emocion: La emoción principal que busca despertar en el receptor (ej. confianza, urgencia, rebeldía, serenidad).
    3. accion_provocada: La conducta, decisión o reacción concreta que el artefacto intenta desencadenar en el usuario según la categoría '{categoria}'.

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_agentivo": {{
            "clima": "Descripción del clima o atmósfera que busca generar el artefacto.",
            "emocion": "Emoción principal que busca despertar (ej. confianza, urgencia, rebeldía).",
            "accion_provocada": "Acción, conducta o reacción que intenta inducir en el espectador."
        }}
    }}
    """
    
    # Consumo de la infraestructura centralizada
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    # Manejo de error retornado por el conector
    if "error" in resultado_vlm:
        return resultado_vlm
        
    
    return {
        "status": "success",
        "metrica": "Semiótica Agentiva (Pragmática)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }