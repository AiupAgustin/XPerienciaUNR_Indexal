
from core.categorias.config import consultar_minicpm_v
# Reutilizamos la función que ya tenemos en la dimensión sintáctica
from core.dimensiones.dimension_sintactica.cromo_semiotica import obtener_paleta_cromatica


def calcular_luminancia_relativa(rgb: tuple) -> float:
    """Calcula la luminancia relativa según la fórmula sRGB de la W3C."""
    r, g, b = [v / 255.0 for v in rgb]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calcular_ratio_contraste_wcag(rgb1: tuple, rgb2: tuple) -> float:
    """Calcula el ratio de contraste exacto WCAG: (L1 + 0.05) / (L2 + 0.05)."""
    l1 = calcular_luminancia_relativa(rgb1)
    l2 = calcular_luminancia_relativa(rgb2)
    mas_clara = max(l1, l2)
    mas_oscura = min(l1, l2)
    return round((mas_clara + 0.05) / (mas_oscura + 0.05), 2)


# Prompts para VLM (Enfocado en lo Semántico / Cualitativo)
PROMPTS_INCLUSION = {
    "afiche": (
        "Realizá un análisis de Inclusión Técnica y Accesibilidad sobre este afiche publicitario/comunicacional. "
        "Generá un alt-text enriquecido para lectores de pantalla y evaluá la jerarquía visual para lectura accesible."
    ),
    "logo": (
        "Realizá un análisis de Inclusión Técnica y Accesibilidad sobre este logotipo/marca gráfica. "
        "Generá un alt-text descriptivo y conciso para lectores de pantalla y evaluá la escalabilidad accesible de sus formas."
    ),
    "ui": (
        "Realizá un análisis de Inclusión Técnica y Accesibilidad sobre esta interfaz de usuario (UI). "
        "Generá el alt-text enriquecido e inspeccioná la disposición visual para la navegación por teclado (foco visual y áreas de clic)."
    ),
    "general": (
        "Realizá un análisis de Inclusión Técnica y Accesibilidad sobre esta pieza gráfica. "
        "Generá un alt-text enriquecido y analizá la legibilidad y jerarquía visual para navegación accesible."
    )
}

def analizar_inclusion_tecnica(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Inclusión Técnica - Accesibilidad (Pragmática):
    combina VLM para semántica (alt-text y orden focal) + Python determinista para WCAG real.
    """
    # Selección del prompt base
    prompt_base = PROMPTS_INCLUSION.get(categoria.lower(), PROMPTS_INCLUSION["general"])
    
    # Prompt enfocado en semántica (evita que el VLM alucine ratios numéricos)
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN DE INCLUSIÓN TÉCNICA Y ACCESIBILIDAD:
    1. alt_text_enriquecido: Redacta una descripción alternativa accesible, precisa y semánticamente rica apta para lectores de pantalla.
    2. evaluacion_cualitativa_contraste: Describe si el contraste de color general permite una lectura clara a simple vista.
    3. navegacion_teclado: Evalúa el flujo visual o la secuencia lógica de foco que seguiría la navegación por teclado.

    Estructura esperada:
    {{
        "inclusion_tecnica": {{
            "alt_text_enriquecido": "...",
            "evaluacion_cualitativa_contraste": "...",
            "navegacion_teclado": "..."
        }}
    }}
    """
    
    # Consulta al VLM
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    if "error" in resultado_vlm:
        return resultado_vlm

    # Cálculo determinista reutilizando la función de cromo_semiotica
    paleta = obtener_paleta_cromatica(imagen_path, cantidad_colores=2)
    datos_wcag_exactos = {}

    if isinstance(paleta, list) and len(paleta) >= 2:
        c1, c2 = paleta[0], paleta[1]
        ratio = calcular_ratio_contraste_wcag(c1["rgb"], c2["rgb"])
        datos_wcag_exactos = {
            "color_dominante_1": c1["hex"],
            "color_dominante_2": c2["hex"],
            "ratio_contraste_calculado": ratio,
            "cumple_wcag_aa_normal": ratio >= 4.5,
            "cumple_wcag_aa_grande": ratio >= 3.0
        }

    # Salida unificada
    return {
        "status": "success",
        "metrica": "Inclusión Técnica / Accesibilidad (Pragmática)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm,
        "wcag_matematico": datos_wcag_exactos
    }