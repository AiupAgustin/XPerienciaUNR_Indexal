
import cv2
import numpy as np
from pathlib import Path
from core.categorias.config import (consultar_minicpm_v, imread_unicode)
from core.dimensiones.dimension_sintactica.eidetica_y_tensiones_kandinsky import calcular_tension_kandinsky
from core.dimensiones.dimension_sintactica.cromo_semiotica import (
    obtener_paleta_cromatica,
    analizar_atributos_cromaticos,
    evaluar_semiotica_cromatica
)
from core.dimensiones.dimension_sintactica.ansel_adams_luminosidad import analizar_luminosidad_completa
from core.dimensiones.dimension_semantica.retorica_linguistica_barthes import analizar_retorica_barthes
from core.dimensiones.dimension_semantica.iconica_peirce import analizar_semiotica_iconica
from core.dimensiones.dimension_semantica.indicial_materialidad import analizar_semiotica_indicial
from core.dimensiones.dimension_semantica.simbolica import analizar_semiotica_simbolica
from core.dimensiones.dimension_pragmatica.secuencia_narrativa import analizar_secuencia_narrativa
from core.dimensiones.dimension_pragmatica.atencion_predictiva import analizar_atencion_predictiva
from core.dimensiones.dimension_pragmatica.semiotica_agentiva import analizar_semiotica_agentiva

# FUNCION AUXILIAR PARA CALCULAR SIMETRÍA CENTRAL (usada en funciones de checkbox 1)
def _calcular_simetria_central(imagen_path: str) -> dict:
    """Calcula la simetría de la imagen respecto al centro vertical."""
    img = imread_unicode(imagen_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"error": "No se pudo cargar la imagen para simetría"}
        
    h, w = img.shape
    mitad_izq = img[:, :w//2]
    mitad_der = cv2.flip(img[:, w//2:], 1)
    
    min_w = min(mitad_izq.shape[1], mitad_der.shape[1])
    diferencia = cv2.absdiff(mitad_izq[:, :min_w], mitad_der[:, :min_w])
    
    simetria = 1.0 - (float(np.mean(diferencia)) / 255.0)
    return {
        "indice_simetria": round(simetria, 2),
        "estado": "Equilibrio simétrico" if simetria > 0.70 else "Asimetría dinámica"
    }

# FUNCIÓN QUE SE ASOCIA AL CHECKBOX 1 (composición visual)
def ejec_composicion_visual(imagen_path: str) -> dict:
    res_kandinsky = calcular_tension_kandinsky(imagen_path)
    res_simetria = _calcular_simetria_central(imagen_path)
    
    # 1. Extraemos métricas para evaluar la estabilidad vs. conflicto dramático
    clasificacion = res_kandinsky.get("clasificacion_kandinsky", "").lower()
    metricas_lineas = res_kandinsky.get("metricas", {})
    
    pct_diagonales = metricas_lineas.get("porcentaje_diagonales_45_135", 0)
    estado_simetria = res_simetria.get("estado", "") if isinstance(res_simetria, dict) else ""

    # 2. Lógica de negocio para determinar el diagnóstico
    if "dinámica" in clasificacion or pct_diagonales > 25.0:
        if "simétrico" in estado_simetria.lower():
            diagnostico = (
                "Composición monumental en equilibrio tenso: Coexiste una simetría de masa "
                "marcada con fuertes diagonales y tensiones estructurales "
                "que aportan dinamismo sin perder el eje central."
            )
        else:
            diagnostico = (
                "Composición con alto conflicto dramático: Predominan tensiones dinámicas "
                "y diagonales que rompen la estabilidad visual y generan fuerza narrativa."
            )
    elif "estática" in clasificacion and "simétrico" in estado_simetria.lower():
        diagnostico = (
            "Composición de alta estabilidad: Estructura rígida, equilibrada y sin quiebres "
            "dramáticos significativos. Transmite orden, calma y permanencia."
        )
    else:
        diagnostico = (
            "Composición en equilibrio tenso: Coexisten elementos de orden estricto "
            "con ligeras asimetrías o diagonales secundarias."
        )

    # 3. Retornamos el diccionario incluyendo la clave explícita para la tabla
    return {
        "status": "success",
        "checkbox": "cb1_composicion_visual",
        "bloque": "1. Composición Visual",
        "analisis_estabilidad_vs_conflicto": diagnostico,
        "tension_y_lineas": res_kandinsky,
        "balance_simetrico": res_simetria
    }

# FUNCION QUE SE ASOCIA AL CHECKBOX 2 ( paleta cromática)
def ejec_paleta_cromatica(imagen_path: str) -> dict:
    """
    Combina K-Means, atributos cromaticos (Ansel Adams/Temperatura)
    y evaluación semiótica (relaciones angulares + Eva Heller/Itten).
    """
    paleta = obtener_paleta_cromatica(imagen_path, cantidad_colores=3)
    atributos = analizar_atributos_cromaticos(imagen_path)
    
    if isinstance(paleta, dict) and "error" in paleta:
        return paleta
    if isinstance(atributos, dict) and "error" in atributos:
        return atributos

    temp_dom = atributos["contraste_temperatura"]["temperatura_dominante"]
    semiotica = evaluar_semiotica_cromatica(paleta, temp_dom)

    return {
        "status": "success",
        "checkbox": "cb2_paleta_cromatica",
        "bloque": "2. Paleta Cromática",
        "paleta_kmeans": paleta,
        "atributos_luminancia_y_temperatura": atributos,
        "analisis_semiotico_color": semiotica
    }

# FUNCION QUE SE ASOCIA AL CHECKBOX 3 (iluminación)
def ejec_iluminacion_y_punctum(imagen_path: str, categoria_pieza: str = "general") -> dict:
    # 1. Sistema de Zonas de Ansel Adams (Rango Dinámico y Exposición)
    res_adams = analizar_luminosidad_completa(imagen_path)
    if isinstance(res_adams, dict) and "error" in res_adams:
        return res_adams

    # 2. Localización del Quiebre Óptico / Saliencia Predictiva
    res_atencion = analizar_atencion_predictiva(imagen_path)
    
    punto_quiebre = {}
    if isinstance(res_atencion, dict) and res_atencion.get("status") == "success" and "resultado" in res_atencion:
        resultado_atencion = res_atencion["resultado"]
        desc_zonas = resultado_atencion.get("descripcion_textual_zonas", {})
        raw_heatmap = resultado_atencion.get("path_imagen_overlay")
        
        # Formateo limpio como ruta absoluta o relativa simple (NO uses .as_uri())
        if raw_heatmap:
            p = Path(raw_heatmap).resolve()
            if p.exists():
                heatmap_clean = str(p)  # Devuelve 'C:\tu\ruta\a\heatmap.jpg'
            else:
                heatmap_clean = str(raw_heatmap).replace("\\", "/")
        else:
            heatmap_clean = "Mapa de calor no generado"

        punto_quiebre = {
            "punto_entrada": desc_zonas.get("punto_entrada_visual", "Centro compositivo"),
            "zonas_calientes": desc_zonas.get("zonas_calientes", "Área central"),
            "mapa_de_calor_saliencia": heatmap_clean
        }

    # 3. Diagnóstico de Anacronismos
    diagnostico_anacronismos = "No se detectan anacronismos visuales o discontinuidades temporales en la pieza."

    return {
        "status": "success",
        "bloque": "3. Iluminación y Punctum",
        "checkbox": "cb3_iluminacion",
        "sistema_zonas_adams": {
            "evaluacion_rango_dinamico": res_adams.get("evaluacion_rango_dinamico", res_adams.get("veredicto")),
            "descripcion": res_adams.get("descripcion"),
            "distribucion": res_adams.get("distribucion_completa", {})
        },
        "quiebre_optico_saliencia": punto_quiebre,
        "analisis_anacronismos": diagnostico_anacronismos
    }

# FUNCION QUE SE ASOCIA AL CHECKBOX 4 (semiotica de la imagen)
def ejec_semiotica_de_la_imagen(imagen_path: str, categoria_pieza: str = "general") -> dict:
    """
    Integra la tricotomía peirciana (Ícono, Índice, Símbolo) 
    y decodifica la significación (Saussure, Santaella, Eco).
    """
    # 1. Dimensión Icónica (Reconocimiento denotativo del significante)
    res_iconico = analizar_semiotica_iconica(imagen_path, categoria_pieza)
    if isinstance(res_iconico, dict) and "error" in res_iconico:
        return res_iconico

    # 2. Dimensión Indicial (Materialidad, huellas físicas y técnica de producción)
    res_indicial = analizar_semiotica_indicial(imagen_path, categoria_pieza)
    if isinstance(res_indicial, dict) and "error" in res_indicial:
        return res_indicial

    # 3. Dimensión Simbólica (Códigos culturales, Saussure/Eco y niveles geográficos)
    res_simbolico = analizar_semiotica_simbolica(imagen_path, categoria_pieza)
    if isinstance(res_simbolico, dict) and "error" in res_simbolico:
        return res_simbolico

    return {
        "status": "success",
        "checkbox": "cb4_semiotica_imagen",
        "bloque": "4. Semiótica de la Imagen",
        "marco_teorico": [
            "Charles Sanders Peirce (Tricotomía del Signo: Ícono, Índice, Símbolo)",
            "Ferdinand de Saussure (Significante / Significado)",
            "Lucia Santaella (Matriz Visual / Verbal-Icónica)",
            "Umberto Eco (Códigos y Convenciones Culturales)"
        ],
        "desglose_semiotico": {
            "analisis_iconico_denotativo": res_iconico.get("resultado", {}),
            "analisis_indicial_materialidad": res_indicial.get("resultado", {}),
            "analisis_simbolico_cultural": res_simbolico.get("resultado", {})
        }
    }

# FUNCION QUE SE ASOCIA AL CHECKBOX 5 (retórica visual)
def ejec_retorica_visual(imagen_path: str, categoria_pieza: str = "general") -> dict:
    """
    Integra la retórica lingüística (Barthes), la detección física de paneles/amontonamiento (OpenCV)
    y la clasificación VLM de figuras retóricas (Hipérbole, Metáfora, Scolari, Traversa).
    """
    # 1. Análisis de Retórica Lingüística (Anclaje vs. Relevo - Barthes)
    res_barthes = analizar_retorica_barthes(imagen_path, categoria_pieza)
    if isinstance(res_barthes, dict) and "error" in res_barthes:
        return res_barthes

    # 2. Análisis Estructural de Paneles y Amontonamiento (OpenCV / NumPy)
    res_secuencia = analizar_secuencia_narrativa(imagen_path)
    if isinstance(res_secuencia, dict) and res_secuencia.get("status") == "error":
        return res_secuencia

    # 3. Diagnóstico de Figuras Retóricas y Condensación Semántica (Scolari / Traversa)
    prompt_retorica = f"""
    Analizá la pieza gráfica desde la teoría de la Retórica Visual (Semántica -> Pragmática).
    Evaluá desproporciones de escala, amontonamiento de signos y condensaciones digitales según Carlos Scolari y Oscar Traversa.

    REGLA STRICTA DE FIDELIDAD PERCEPTIVA:
    1. Basá tu análisis EXCLUSIVAMENTE en los elementos, objetos y sujetos que identificás de forma directa e incontestable en la imagen.
    2. Queda estrictamente prohibido incluir, suponer o mencionar elementos que no estén físicamente presentes en la composición.
    3. Para evaluar el amontonamiento de signos, restringite ÚNICAMENTE a los elementos icónicos visibles en la escena.

    REGLA EVALUATIVA DE ESCALA Y DESPROPORCIÓN:
    - Evaluá si existe una alteración/edición intencionada de tamaño entre los objetos (fotomontaje, ilustración) o si la escala responde a la perspectiva y proporción real de la escena.
    - Si la escena muestra objetos o estructuras en su proporción física real (aunque sean de gran magnitud o escala monumental), catalogá en 'diagnostico_figura_dominante' como 'Composición Literal (Sin figura)' o 'Antítesis / Contraste visual'. Reservá 'Hipérbole por escala' EXCLUSIVAMENTE para exageraciones o manipulaciones de tamaño irreales en fotomontajes o ilustraciones.

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas.

    INSTRUCCIONES EVALUATIVAS:
    1. 'diagnostico_figura_dominante': Elegí ÚNICAMENTE una etiqueta entre: 
       "Composición Literal (Sin figura)", "Antítesis / Contraste visual", "Metáfora visual", "Condensación Semántica Digital", "Sinécdoque" o "Hipérbole por escala".
    2. 'operacion_escala_y_desproporcion': Evaluá si existe una desproporción intencionada por fotomontaje/ilustración o si se trata de la perspectiva y escala real de una fotografía.
    3. 'colision_amontonamiento_signos': Describí la acumulación o interacción visual basándote únicamente en el inventario real de los objetos visibles.
    4. 'fundamentacion_teorica': Explicación breve (1 o 2 líneas) citando los principios de Scolari o Traversa aplicados.

    Estructura estricta del JSON:
    {{
        "analisis_retorica_visual": {{
            "diagnostico_figura_dominante": "Composición Literal (Sin figura) / Antítesis / Contraste visual / Metáfora / Etc.",
            "operacion_escala_y_desproporcion": "Análisis de proporción objeto/fondo basado en elementos visibles",
            "colision_amontonamiento_signos": "Evaluación de amontonamiento basada en los objetos reales de la escena",
            "fundamentacion_teorica": "Fundamentación técnica según Scolari / Traversa"
        }}
    }}
    """
    
    res_vlm = consultar_minicpm_v(imagen_path, prompt_retorica)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb5_retorica_visual",
        "bloque": "5. Retórica Visual",
        "marco_teorico": [
            "Roland Barthes (Retórica e interacción Texto-Imagen)",
            "Figuras Retóricas Clásicas (Metáfora, Hipérbole por escala, Antítesis)",
            "Carlos Scolari / Oscar Traversa (Condensados de pantalla, hipermediación)"
        ],
        "desglose_retorico": {
            "mensaje_linguistico_barthes": res_barthes.get("resultado", {}),
            "estructura_paneles_y_formato": res_secuencia.get("resultado", {}),
            "diagnostico_figuras_y_condensacion": res_vlm.get("resultado", res_vlm)
        }
    }

# FUNCION QUE SE ASOCIA AL CHECKBOX 6 (contexto y denotación)

def ejec_contexto_y_denotacion(imagen_path: str, categoria_pieza: str = "general") -> dict:
    """
    Síntesis de las 3 dimensiones de Charles Morris (Sintáctica, Semántica, Pragmática)
    y lectura de fondo con la dicotomía Denotación / Connotación de Roland Barthes.
    """
    # 1. Análisis de Semiótica Agentiva (Connotación y Efecto de Sentido Pragmático)
    res_agentiva = analizar_semiotica_agentiva(imagen_path, categoria_pieza)
    if isinstance(res_agentiva, dict) and "error" in res_agentiva:
        return res_agentiva

    # 2. Diagnóstico de Síntesis Denotativa vs. Connotativa (Morris / Barthes)
    prompt_sintesis = f"""
    Realizá una síntesis semiótica integral de la pieza gráfica bajo la teoría de Charles Morris (Sintáctica, Semántica, Pragmática)
    y la lectura de fondo de Roland Barthes (Denotación vs. Connotación).

    REQUISITO SINO QUA NON DE SALIDA:
    Responde EXCLUSIVAMENTE con un objeto JSON válido en idioma español. Sin preámbulos ni notas.

    REGLA GENERAL DE FIDELIDAD DENOTATIVA ABSTRACTA:
    1. En el 'nivel_denotativo_literal', realizá un inventario visual estricto basado en la morfología, formas, texturas, volumen y materialidad de los elementos observados.
    2. Identificá cada componente según su función estructural o perceptiva visible (ej. estructuras, superficies, figuras en movimiento, volúmenes, accesorios).
    3. Mantené la máxima literalidad observacional: no asignes nombres de organismos, seres vivos ni categorías complejas a menos que queden incontestablemente evidenciados por su anatomía o forma gráfica real.
    4. Queda estrictamente prohibido incluir sustantivos o etiquetas por mera analogía visual, textura o color si el elemento no está representado explícitamente.
    5. Redactá todas las respuestas como cadenas de texto continuo en español, sin volcar estructuras de diccionario o código crudo.

    INSTRUCCIONES EVALUATIVAS:
    1. 'nivel_denotativo_literal': Descripción literal e inventario objetivo de lo que se ve en la pieza.
    2. 'nivel_connotativo_de_fondo': Interpretación de fondo, mitología, valores culturales o ideológicos transmitidos.
    3. 'sintesis_dimensiones_morris': Resumen del cruce entre el orden sintáctico (formas/color), semántico (significados) y pragmático (impacto).
    4. 'sintesis_niveles_clave': Cadena de texto limpia que consolide los conceptos denotativos y connotativos principales (Ejemplo: "Denotativo: [elementos directos] | Connotativo: [conceptos de fondo]").

    Estructura JSON estricta:
    {{
        "reporte_contexto_y_denotacion": {{
            "nivel_denotativo_literal": "Descripción literal e inventario físico de la pieza",
            "nivel_connotativo_de_fondo": "Lectura ideológica y simbólica subyacente",
            "sintesis_dimensiones_morris": "Cruce sintáctico-semántico-pragmático",
            "sintesis_niveles_clave": "Denotativo: [elementos directos] | Connotativo: [conceptos de fondo]"
        }}
    }}
    """
    res_vlm = consultar_minicpm_v(imagen_path, prompt_sintesis)
    if isinstance(res_vlm, dict) and "error" in res_vlm:
        return res_vlm

    return {
        "status": "success",
        "checkbox": "cb6_contexto_denotacion",
        "bloque": "6. Contexto y Denotación",
        "marco_teorico": [
            "Charles Morris (Síntesis de dimensiones: Sintáctica, Semántica, Pragmática)",
            "Roland Barthes (Nivel Denotativo vs. Nivel Connotativo)",
            "Semiótica Agentiva (Clima, emoción y acción provocada)"
        ],
        "desglose_integrador": {
            "semiotica_agentiva_pragmatica": res_agentiva.get("resultado", {}),
            "reporte_denotacion_connotacion": res_vlm.get("resultado", res_vlm)
        }
    }

# MAPA DE FUNCIONES POR CHECKBOX PARA USO EN LA INTERFAZ
MAPA_CHECKBOXES_CAT0 = {
    "cb1_composicion_visual": ejec_composicion_visual,
    "cb2_paleta_cromatica": ejec_paleta_cromatica,
    "cb3_iluminacion": ejec_iluminacion_y_punctum,
    "cb4_semiotica_imagen": ejec_semiotica_de_la_imagen,
    "cb5_retorica_visual": ejec_retorica_visual,
    "cb6_contexto_denotacion": ejec_contexto_y_denotacion
}