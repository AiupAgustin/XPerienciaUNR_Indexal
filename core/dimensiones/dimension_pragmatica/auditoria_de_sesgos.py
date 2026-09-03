
from servicios.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría para Auditoría de Sesgos
PROMPTS_SESGOS = {
    "afiche": (
        "Realizá una auditoría crítica de sesgos sobre este afiche publicitario/comunicacional. "
        "Analizá la presencia de estereotipos de género, raza o clase social, "
        "evaluando si la representación visual reproduce sesgos culturales o eurocéntricos/anglosajones."
    ),
    "logo": (
        "Realizá una auditoría crítica de sesgos sobre este logotipo/marca gráfica. "
        "Analizá si los elementos simbólicos, figuras humanas, tipografías o iconografía reproducen "
        "sesgos implícitos de género, raza o estatus socioeconómico/clase derivados de paradigmas hegemónicos."
    ),
    "ui": (
        "Realizá una auditoría crítica de sesgos sobre esta interfaz de usuario (UI). "
        "Analizá si los avatares, ilustraciones, fotografías de usuarios o lenguaje visual "
        "presentan estereotipos de género, raza, inclusión socioeconómica o sesgos occidentales/anglosajones."
    ),
    "general": (
        "Realizá una auditoría crítica de sesgos sobre esta pieza gráfica. "
        "Analizá la presencia de estereotipos de género, raza o clase social, "
        "evaluando si el artefacto reproduce sesgos impuestos por modelos o datasets anglosajones y hegemónicos."
    )
}

def analizar_auditoria_sesgos(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Auditoría de Sesgos (Pragmática): Detecta estereotipos de género,
    raza o clase impuestos por datasets o paradigmas hegemónicos/anglosajones.
    """
    # Selección del prompt base según la categoría
    prompt_base = PROMPTS_SESGOS.get(categoria.lower(), PROMPTS_SESGOS["general"])
    
    # Inyección de instrucciones pragmáticas y de estructura JSON estricta
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN DE AUDITORÍA DE SESGOS:
    Evalúa minuciosamente el artefacto gráfico buscando la presencia de sesgos o estereotipos en tres dimensiones clave:
    1. genero: Estereotipos o roles preasignados por género en la representación visual (ej. roles tradicionales, invisibilización, sobrerepresentación).
    2. raza_etnicidad: Sesgos raciales, etnocentrismo o dominancia de estándares anglosajones/eurocéntricos en las figuras representadas.
    3. clase_socioeconomica: Estereotipos vinculados al estatus social, económico o de consumo (ej. elitismo, representación exclusiva de clases altas o estigmatización).

    La estructura del JSON debe ser exactamente:
    {{
        "auditoria_sesgos": {{
            "estereotipos_genero": "Análisis sobre presencia o ausencia de sesgos o roles de género.",
            "estereotipos_raza": "Análisis sobre diversidad racial, etnocentrismo o sesgos anglosajones/eurocéntricos.",
            "estereotipos_clase": "Análisis sobre representación socioeconómica y accesibilidad visual."
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
        "metrica": "Auditoría de Sesgos (Pragmática)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }