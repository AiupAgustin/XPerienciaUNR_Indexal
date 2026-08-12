from pathlib import Path
import cv2
from core.categorias.config import (consultar_minicpm_v, imread_unicode)
from core.dimensiones.dimension_pragmatica.atencion_predictiva import analizar_atencion_predictiva
from core.dimensiones.dimension_sintactica.reticular_grillas import generar_grilla_muller_brockmann
from core.dimensiones.dimension_sintactica.cromo_semiotica import obtener_paleta_cromatica
from core.dimensiones.dimension_sintactica.eidetica_y_tensiones_kandinsky import calcular_tension_kandinsky
from core.dimensiones.dimension_semantica.indicial_materialidad import analizar_semiotica_indicial
from core.dimensiones.dimension_semantica.tipografica import analizar_tipografia
from core.dimensiones.dimension_semantica.simbolica import analizar_semiotica_simbolica
from core.dimensiones.dimension_pragmatica.inclusion_tecnica import analizar_inclusion_tecnica



# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 1 (Jerarquía Visual)
def ejec_jerarquia_visual_ui(imagen_path: str, categoria_pieza: str = "ui") -> dict:
    """
    Audita la saliencia óptica por frecuencias espaciales (OpenCV) y contrasta
    el punto de entrada/zonas calientes contra el propósito o CTA principal de la UI.
    """
    # 1. Ejecución del algoritmo de Saliencia de OpenCV
    res_atencion = analizar_atencion_predictiva(imagen_path)
    if res_atencion.get("status") != "success":
        return res_atencion

    datos_saliencia = res_atencion.get("resultado", {})
    zonas = datos_saliencia.get("descripcion_textual_zonas", {})
    punto_entrada = zonas.get("punto_entrada_visual", "No identificado")
    zonas_calientes = zonas.get("zonas_calientes", "No identificadas")
    patron_lectura = zonas.get("recorrido_visual_estimado", "No identificado")

    # 2. Invocación al VLM para auditoría de CTA y alineación con la saliencia
    prompt_jerarquia = f"""
    Analizá la jerarquía visual y la efectividad de los elementos de interacción de esta interfaz de usuario (UI).

    CONTEXTO TÉCNICO DE SALIENCIA ÓPTICA (OpenCV):
    - Punto de entrada primario: {punto_entrada}
    - Concentración de atención (Zonas calientes): {zonas_calientes}
    - Patrón de lectura estimado: {patron_lectura}

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni bloques markdown.

    INSTRUCCIONES EVALUATIVAS:
    1. 'proposito_pantalla_cta': Identificá el botón de acción principal (CTA), formulario o elemento central de interacción de la pantalla.
    2. 'coincide_con_saliencia': Indicar True si el punto de entrada o la zona caliente coinciden/guían al usuario hacia el CTA o propósito real. Indicar False si la atención se desvía a elementos secundarios.
    3. 'alerta_jerarquia': Si no coincide (False), emití una alerta detallada indicando qué elemento está robando atención visual. Si coincide (True), indicá: "Jerarquía alineada correctamente".

    Estructura JSON estricta:
    {{
        "evaluacion_jerarquia_ui": {{
            "proposito_pantalla_cta": "Descripción del CTA/propósito principal detectado",
            "coincide_con_saliencia": true,
            "alerta_jerarquia": "Alerta de desalineación o confirmación de jerarquía"
        }}
    }}
    """
    
    res_vlm = consultar_minicpm_v(imagen_path, prompt_jerarquia)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb1_jerarquia_visual_ui",
        "bloque": "1. Jerarquía Visual",
        "marco_teorico": [
            "Mapas de calor predictivos de atención visual",
            "Saliency Maps por contraste de frecuencias espaciales (OpenCV Spectral Residual)",
            "Auditoría de alineación entre punto de entrada óptico y Call To Action (CTA)"
        ],
        "desglose_jerarquia": {
            "saliencia_predictiva_opencv": datos_saliencia,
            "auditoria_cta_y_alerta": res_vlm.get("resultado", res_vlm)
        }
    }

# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 2 (Grilla y Layout)
def ejec_grilla_y_layout_ui(imagen_path: str, categoria_pieza: str = "ui") -> dict:
    """
    Evalúa las dimensiones de la pantalla para definir dinámicamente si aplica 
    una grilla de 8 columnas (Mobile) o 12 columnas (Desktop/Web) mediante Müller-Brockmann.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    output_dir = BASE_DIR / "output" / "grillas"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    nombre_base = Path(imagen_path).stem
    destino_grilla = str(output_dir / f"grilla_mb_{nombre_base}.jpg")

    # 1. Evaluación dinámica de breakpoint (Mobile vs Desktop)
    img_temp = imread_unicode(imagen_path)
    if img_temp is not None:
        h, w, _ = img_temp.shape
        ratio_aspecto = h / w if w > 0 else 1.0
        
        # Breakpoint: 8 columnas si w < 768px O si es marcadamente vertical (h/w >= 1.25)
        if w < 768 or ratio_aspecto >= 1.25:
            cols_calculadas = 8
        else:
            cols_calculadas = 12
    else:
        cols_calculadas = 12

    # 2. Generación de la grilla modular de Müller-Brockmann
    res_grilla = generar_grilla_muller_brockmann(
        imagen_path=imagen_path,
        destino_path=destino_grilla,
        columnas=cols_calculadas,
        filas=4,
        calle=15
    )
    
    if "error" in res_grilla:
        return res_grilla

    dim_modulos = res_grilla.get("dimensiones_modulos", {})

    # 3. Auditoría analítica con MiniCPM-V
    prompt_layout = f"""
    Analizá la estructura de grilla y layout de esta interfaz de usuario (UI) bajo el sistema de grillas de Josef Müller-Brockmann.

    MÉTRICAS MATEMÁTICAS CALCULADAS POR OPENCV:
    - Ancho de módulo individual: {dim_modulos.get('ancho_modulo')} px
    - Alto de módulo individual: {dim_modulos.get('alto_modulo')} px
    - Configuración analizada: {cols_calculadas} columnas con calles de 15px.

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas markdown.

    INSTRUCCIONES EVALUATIVAS:
    1. 'sistema_grilla_detectado': Identificá el estándar de grilla digital utilizado en la pantalla (ej. "Grilla de 12 columnas (Web)", "Grilla de 8 columnas (Mobile)", "Baseline Grid de 8px / 4px" o "Layout asimétrico").
    2. 'cumple_estandar_ui': Responde True si los contenedores, botones y bloques de texto respetan los márgenes y ejes, o False si hay descalces de alineación.
    3. 'errores_alineacion_cuantificados': Describí detalladamente los errores de alineación o desvíos cuantificados en píxeles en elementos de UI respecto a la grilla o componentes adyacentes.

    Estructura JSON estricta:
    {{
        "evaluacion_grilla_ui": {{
            "sistema_grilla_detectado": "Grilla de 12 columnas / 8 columnas / Baseline Grid",
            "cumple_estandar_ui": true,
            "errores_alineacion_cuantificados": "Descripción detallada de descalces y desvíos cuantificados en píxeles"
        }}
    }}
    """

    res_vlm = consultar_minicpm_v(imagen_path, prompt_layout)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb2_grilla_y_layout_ui",
        "bloque": "2. Grilla y Layout",
        "marco_teorico": [
            "Josef Müller-Brockmann (Sistemas de grillas modulares en diseño gráfico y digital)",
            "Estándares de layout UI/UX (Grillas de 12/8 columnas y Baseline Grid)",
            "Cuantificación de desvíos de alineación en píxeles"
        ],
        "desglose_layout": {
            "reticula_muller_brockmann_opencv": res_grilla,
            "auditoria_sistema_columnas": res_vlm.get("resultado", res_vlm)
        }
    }

# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 3 (Sistema de Diseño - Tokens)
def ejec_sistema_diseno_tokens_ui(imagen_path: str, categoria_pieza: str = "ui") -> dict:
    """
    Ejecuta la subcapa de materialidad indicial y pasa su salida como contexto a MiniCPM-V
    para auditar la consistencia de Design Tokens (border-radius, paddings y espaciados).
    """
    # 1. Ejecución de la subcapa Indicial/Materialidad para UI
    res_indicial = analizar_semiotica_indicial(imagen_path, categoria="ui")
    if isinstance(res_indicial, dict) and "error" in res_indicial:
        return res_indicial

    # Extracción defensiva adaptada a la estructura real de indicial_materialidad.py
    res_vlm_indicial = res_indicial.get("resultado", {})
    if isinstance(res_vlm_indicial, dict) and "analisis_indicial" in res_vlm_indicial:
        datos_materialidad = res_vlm_indicial.get("analisis_indicial", {})
    else:
        datos_materialidad = res_vlm_indicial.get("resultado", {}).get("analisis_indicial", {}) if isinstance(res_vlm_indicial, dict) else {}

    # 2. Auditoría VLM de Consistencia de Design Tokens guiada por el contexto previo
    prompt_tokens = f"""
    Analizá la consistencia del Sistema de Diseño (Design Tokens) en esta interfaz de usuario (UI).

    CONTEXTO TÉCNICO DE MATERIALIDAD (Subcapa Indicial):
    - Técnica de origen: {datos_materialidad.get('tecnica_origen', 'Diseño digital UI')}
    - Soporte y textura: {datos_materialidad.get('soporte_y_textura', 'Pantalla digital')}
    - Pistas de producción: {datos_materialidad.get('pistas_produccion', 'Entorno nativo digital')}

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas markdown.

    INSTRUCCIONES EVALUATIVAS:
    1. 'evaluacion_border_radius': Evaluá la consistencia en el radio de curvatura de las esquinas (border-radius) entre botones, tarjetas (cards), campos de texto y contenedores.
    2. 'regularidad_espaciados': Evaluá la regularidad de los márgenes y espaciados internos/externos (paddings y gaps) entre cards y botones.
    3. 'consistencia_design_tokens': Responde True si los componentes respetan un sistema de tokens uniforme, o False si hay mezcla incoherente de estilos.
    4. 'inconsistencias_estructurales': Describe detalladamente las inconsistencias visuales encontradas entre componentes (ej. mezcla de esquinas rectas y redondeadas, desvíos de espaciado o tamaños dispares).

    Estructura JSON estricta:
    {{
        "evaluacion_tokens_ui": {{
            "evaluacion_border_radius": "Análisis de radios de curvatura en esquinas de botones y cards",
            "regularidad_espaciados": "Evaluación del ritmo de padding y espacios entre elementos",
            "consistencia_design_tokens": true,
            "inconsistencias_estructurales": "Descripción de fallas de coherencia o inconsistencias detectadas"
        }}
    }}
    """

    res_vlm = consultar_minicpm_v(imagen_path, prompt_tokens)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb3_sistema_diseno_tokens_ui",
        "bloque": "3. Sistema de Diseño (Tokens)",
        "marco_teorico": [
            "Descriptores morfológicos de componentes UI y materialidad digital",
            "Sistemas de Design Tokens (Border-radius, Spacing/Padding system)",
            "Coherencia y consistencia estructural entre tarjetas (cards) y botones"
        ],
        "desglose_tokens": {
            "morfologia_material_indicial": datos_materialidad,
            "auditoria_design_tokens": res_vlm.get("resultado", res_vlm)
        }
    }

# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 4 (Legibilidad de Texto)
def ejec_legibilidad_texto_ui(imagen_path: str, categoria_pieza: str = "ui") -> dict:
    """
    Ejecuta la subcapa tipográfica y audita la microtipografía en pantalla con MiniCPM-V:
    caracteres por línea (rango óptimo 45-75), tamaño de glifo (mínimo 16px en cuerpo) y alertas de legibilidad.
    """
    # 1. Ejecución de la subcapa Tipográfica para UI
    res_tipografia = analizar_tipografia(imagen_path, categoria="ui")
    if isinstance(res_tipografia, dict) and "error" in res_tipografia:
        return res_tipografia

    # Extracción defensiva del resultado de analizar_tipografia
    res_vlm_tipo = res_tipografia.get("resultado", {})
    if isinstance(res_vlm_tipo, dict) and "analisis_tipografico" in res_vlm_tipo:
        datos_tipo = res_vlm_tipo.get("analisis_tipografico", {})
    else:
        datos_tipo = res_vlm_tipo.get("resultado", {}).get("analisis_tipografico", {}) if isinstance(res_vlm_tipo, dict) else {}

    # 2. Auditoría VLM de Microtipografía y Legibilidad en Pantalla
    prompt_legibilidad = f"""
    Analizá la legibilidad de texto y los estándares de microtipografía de esta interfaz de usuario (UI).

    CONTEXTO PREVIO TIPOGRÁFICO:
    - Clasificación formal: {datos_tipo.get('clasificacion_formal', 'No especificada')}
    - Altura de x y legibilidad: {datos_tipo.get('altura_de_x_y_legibilidad', 'No evaluada')}
    - Jerarquía de texto: {datos_tipo.get('maridaje_y_jerarquia', 'No especificada')}

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas markdown.

    INSTRUCCIONES EVALUATIVAS (MICROTIPOGRAFÍA):
    1. 'caracteres_por_linea': Estima la cantidad de caracteres por línea en los párrafos o bloques de lectura continua de la UI. Indicá si se encuentra dentro del rango óptimo recomendado (45 a 75 caracteres).
    2. 'tamano_glifo_estimado_px': Estima el tamaño en píxeles del cuerpo de texto principal de lectura. Indicá si cumple con el estándar mínimo de UI de 16px (1rem).
    3. 'cumple_microtipografia': Responde True si la longitud de línea y el tamaño del glifo son adecuados para lectura continua en pantalla, o False si presenta deficiencias.
    4. 'alertas_legibilidad_microtipografica': Describe detalladamente las alertas o fallas detectadas (ej. "Líneas de texto demasiado largas (>75 caracteres) que dificultan el salto de línea", "Texto secundario o de cuerpo por debajo de 16px", "Contraste o interlineado insuficiente"). Si no hay errores, indicá: "Microtipografía y legibilidad alineadas a estándares UI".

    Estructura JSON estricta:
    {{
        "evaluacion_legibilidad_ui": {{
            "caracteres_por_linea": "Estimación y evaluación del ancho de columna (Rango 45-75)",
            "tamano_glifo_estimado_px": "Estimación del tamaño de fuente en píxeles (Mínimo 16px)",
            "cumple_microtipografia": true,
            "alertas_legibilidad_microtipografica": "Descripción de alertas tipográficas o confirmación"
        }}
    }}
    """

    res_vlm = consultar_minicpm_v(imagen_path, prompt_legibilidad)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb4_legibilidad_texto_ui",
        "bloque": "4. Legibilidad de Texto",
        "marco_teorico": [
            "Estándares de microtipografía en pantallas digitales",
            "Ancho de columna y rango óptimo de lectura (45 a 75 caracteres por línea)",
            "Cuerpo de texto mínimo para legibilidad continua en UI (16px / 1rem)"
        ],
        "desglose_legibilidad": {
            "analisis_tipografico_base": datos_tipo,
            "auditoria_microtipografia": res_vlm.get("resultado", res_vlm)
        }
    }


# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 5 (Accesibilidad WCAG)
def ejec_accesibilidad_wcag_ui(imagen_path: str, categoria_pieza: str = "ui") -> dict:
    """
    Llama a la subcapa de inclusión técnica para obtener el contraste exacto (WCAG/APCA)
    y evalúa con MiniCPM-V + OpenCV la ergonomía motriz (Ley de Fitts desde el centro inferior)
    y el área táctil mínima (44x44px).
    """
    # 1. Ejecución de la subcapa Inclusión Técnica
    res_inclusion = analizar_inclusion_tecnica(imagen_path, categoria="ui")
    if isinstance(res_inclusion, dict) and "error" in res_inclusion:
        return res_inclusion

    # Extracción de datos VLM y matemáticos de la subcapa
    res_vlm_inc = res_inclusion.get("resultado", {})
    if isinstance(res_vlm_inc, dict) and "inclusion_tecnica" in res_vlm_inc:
        datos_inc_vlm = res_vlm_inc.get("inclusion_tecnica", {})
    else:
        datos_inc_vlm = res_vlm_inc.get("resultado", {}).get("inclusion_tecnica", {}) if isinstance(res_vlm_inc, dict) else {}

    datos_wcag_math = res_inclusion.get("wcag_matematico", {})

    # 2. Métrica algorítmica local: Dimensiones para Ley de Fitts
    img_temp = imread_unicode(imagen_path)
    if img_temp is not None:
        h, w, _ = img_temp.shape
        centro_inferior = (int(w / 2), h)  # Origen del pulgar (Bottom-Center)
    else:
        h, w = 1920, 1080
        centro_inferior = (540, 1920)

    # 3. Auditoría VLM de Accesibilidad WCAG y Ergonomía Motriz
    prompt_wcag = f"""
    Analizá la accesibilidad digital (WCAG 3.0 / APCA) y la ergonomía motriz de esta interfaz de usuario (UI).

    CONTEXTO TÉCNICO PREVIO:
    - Resolución de pantalla: {w}x{h} px
    - Origen de interacción táctil (Centro inferior / Thumb Zone): Coordenada {centro_inferior}
    - Ratio de contraste matemático WCAG: {datos_wcag_math.get('ratio_contraste_calculado', 'N/A')}
    - Cumple WCAG AA Normal: {datos_wcag_math.get('cumple_wcag_aa_normal', 'N/A')}
    - Alt-Text sugerido: {datos_inc_vlm.get('alt_text_enriquecido', 'No generado')}

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas markdown.

    INSTRUCCIONES EVALUATIVAS:
    1. 'nivel_cumplimiento_wcag': Basándote en el ratio de contraste ({datos_wcag_math.get('ratio_contraste_calculado', 'N/A')}) y en la legibilidad del texto/iconos, indicá si la pantalla alcanza nivel "AA", "AAA" o "No cumple".
    2. 'area_tactil_minima_44px': Evaluá si los elementos interactivos (botones, íconos, links) respetan el área de toque mínima de 44x44px.
    3. 'evaluacion_ley_fitts_cta': Aplicá la Ley de Fitts evaluando la distancia entre el botón de acción principal (CTA) y el origen inferior ({centro_inferior}). Analizá si está en una zona de fácil alcance o en una zona de alto esfuerzo motriz.
    4. 'alerta_zona_incomoda_cta': Si el CTA principal está ubicado en una zona incómoda de alcanzar (ej. esquina superior izquierda/derecha), emití una alerta. Si está bien posicionado, indicá: "CTA ubicado en zona ergonómica óptima".

    Estructura JSON estricta:
    {{
        "evaluacion_accesibilidad_ui": {{
            "nivel_cumplimiento_wcag": "AA / AAA / No cumple",
            "area_tactil_minima_44px": "Análisis del tamaño de áreas de toque (Target Size)",
            "evaluacion_ley_fitts_cta": "Evaluación de distancia y tiempo de alcanzabilidad desde la zona inferior",
            "alerta_zona_incomoda_cta": "Alerta de esfuerzo motriz o confirmación de zona cómoda"
        }}
    }}
    """

    res_vlm = consultar_minicpm_v(imagen_path, prompt_wcag)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb5_accesibilidad_wcag_ui",
        "bloque": "5. Accesibilidad WCAG",
        "marco_teorico": [
            "Pautas de Accesibilidad para el Contenido Web (WCAG 3.0 / APCA)",
            "Área táctil mínima interactiva (Target Size >= 44x44px)",
            "Ley de Fitts para ergonomía motriz y alcanzabilidad táctil (Thumb Zone)"
        ],
        "desglose_accesibilidad": {
            "datos_pantalla_origen": {"ancho_px": w, "alto_px": h, "centro_inferior_origen": centro_inferior},
            "inclusividad_tecnica_base": datos_inc_vlm,
            "wcag_matematico": datos_wcag_math,
            "auditoria_wcag_y_fitts": res_vlm.get("resultado", res_vlm)
        }
    }

# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 6 (Personalidad e Invariabilidad Escalar)
def ejec_personalidad_e_invariabilidad_escalar_ui(imagen_path: str, categoria_pieza: str = "ui") -> dict:
    """
    Combina cv2.kmeans (paleta dominante), la subcapa de Kandinsky (líneas y tensión) 
    y la subcapa simbólica para cruzar atributos perceptuales (Forma + Color -> Carácter)
    y simular resoluciones críticas (Smartwatch 320px, Mobile 720p) evaluando el colapso de componentes.
    """
    # 1. Extracción cromática (K-Means)
    paleta_color = obtener_paleta_cromatica(imagen_path, cantidad_colores=3)

    # 2. Extracción morfológica (Kandinsky: Diagonales vs Ortogonales)
    res_kandinsky = calcular_tension_kandinsky(imagen_path)

    # 3. Extracción de convenciones simbólicas para UI
    res_simbolica = analizar_semiotica_simbolica(imagen_path, categoria="ui")
    res_vlm_simb = res_simbolica.get("resultado", {}) if isinstance(res_simbolica, dict) else {}
    if isinstance(res_vlm_simb, dict) and "analisis_simbolico" in res_vlm_simb:
        datos_simbolicos = res_vlm_simb.get("analisis_simbolico", {})
    else:
        datos_simbolicos = res_vlm_simb.get("resultado", {}).get("analisis_simbolico", {}) if isinstance(res_vlm_simb, dict) else {}

    # 4. Cálculo algorítmico de factores de escala en resoluciones críticas
    img_temp = imread_unicode(imagen_path)
    if img_temp is not None:
        h, w, _ = img_temp.shape
        factor_smartwatch = round(320.0 / w, 2) if w > 0 else 0.3
        factor_mobile_720p = round(720.0 / w, 2) if w > 0 else 0.6
    else:
        h, w = 1920, 1080
        factor_smartwatch, factor_mobile_720p = 0.16, 0.37

    # 5. Auditoría VLM de Personalidad, Coherencia Estética y Escalabilidad
    prompt_personalidad_escala = f"""
    Analizá la personalidad de la interfaz (UI), sus atributos perceptuales y la invariabilidad escalar en pantallas extremas.

    DATOS TÉCNICOS CROMÁTICOS Y MORFOLÓGICOS:
    - Paleta dominante K-Means: {paleta_color}
    - Geometría y tensión (Kandinsky): {res_kandinsky.get('clasificacion_kandinsky', 'N/A')} ({res_kandinsky.get('analisis_semiotico', '')})
    - Convenciones simbólicas digitales: {datos_simbolicos}
    - Resolución original: {w}x{h} px
    - Factor de escala simulado a Smartwatch (320px): {factor_smartwatch * 100}% de su tamaño original
    - Factor de escala simulado a Celular Básico (720p): {factor_mobile_720p * 100}% de su tamaño original

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas markdown.

    INSTRUCCIONES EVALUATIVAS:
    1. 'atributos_perceptuales_caracter': Cruzá la paleta de colores con la geometría dominante (ortogonal/dinámica) y definí la personalidad/carácter de la interfaz (ej. "Minimalista y tecnológica", "Corporativa y estructurada", "Dinámica y disruptiva").
    2. 'coherencia_estetica_percibida': Evaluá si el lenguaje visual (color + forma + tipografía) es uniforme y transmite solidez de marca, o si genera incoherencia estética.
    3. 'comportamiento_smartwatch_320px': Analizá cómo respondería la interfaz al reducirse a un smartwatch (320px ancho). Describí qué componentes o textos colapsarían por completo.
    4. 'dispositivos_donde_colapsan_tokens': Reportá explícitamente en qué dispositivos (smartwatch 320px, celular básico 720p) los componentes, paddings o textos mínimos pierden legibilidad o colapsan por falta de invariabilidad escalar.

    Estructura JSON estricta:
    {{
        "evaluacion_personalidad_escalabilidad": {{
            "atributos_perceptuales_caracter": "Definición del carácter derivado de forma + color",
            "coherencia_estetica_percibida": "Evaluación de la cohesión estética del sistema visual",
            "comportamiento_smartwatch_320px": "Simulación de legibilidad y colapso en 320px",
            "dispositivos_donde_colapsan_tokens": "Reporte de dispositivos críticos donde colapsan textos o componentes"
        }}
    }}
    """

    res_vlm = consultar_minicpm_v(imagen_path, prompt_personalidad_escala)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb6_personalidad_e_invariabilidad_escalar_ui",
        "bloque": "6. Personalidad de Interfaz e Invariabilidad Escalar",
        "marco_teorico": [
            "Atributos perceptuales de interfaz (Sintaxis cromático-morfológica)",
            "Teoría de Invariabilidad Escalar en Sistemas de Diseño UI/UX",
            "Redimensionamiento simulado en pantallas críticas (Smartwatch 320px / Mobile 720p)"
        ],
        "desglose_personalidad_escala": {
            "paleta_kmeans": paleta_color,
            "tension_kandinsky": res_kandinsky,
            "simbolismo_digital": datos_simbolicos,
            "factores_escala_simulados": {"smartwatch_320px": factor_smartwatch, "mobile_720p": factor_mobile_720p},
            "auditoria_caracter_y_colapso": res_vlm.get("resultado", res_vlm)
        }
    }

# MAPA DE FUNCIONES POR CHECKBOX PARA USO EN LA INTERFAZ
MAPA_CHECKBOXES_CAT5 = {
    "cb1_jerarquia_visual_ui": ejec_jerarquia_visual_ui,
    "cb2_grilla_y_layout_ui": ejec_grilla_y_layout_ui,
    "cb3_sistema_diseno_tokens_ui": ejec_sistema_diseno_tokens_ui,
    "cb4_legibilidad_texto_ui": ejec_legibilidad_texto_ui,
    "cb5_accesibilidad_wcag_ui": ejec_accesibilidad_wcag_ui,
    "cb6_personalidad_e_invariabilidad_escalar_ui": ejec_personalidad_e_invariabilidad_escalar_ui,
}