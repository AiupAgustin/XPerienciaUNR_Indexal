import cv2
import numpy as np
import os
from pathlib import Path

def calcular_salience_map(imagen_path: str):
    """Calcula el mapa de saliencia visual usando el algoritmo de OpenCV."""
    img = cv2.imread(imagen_path)
    if img is None:
        return None, None

    # Algoritmo de saliencia espectral de OpenCV
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    success, saliency_map = saliency.computeSaliency(img)

    if not success:
        return None, None

    # Normalizar a rango 0-255
    saliency_map = (saliency_map * 255).astype("uint8")
    return img, saliency_map


def analizar_atencion_predictiva(imagen_path: str, output_heatmap_dir: str = "output/heatmaps") -> dict:
    """
    Subcapa Atención Predictiva (Pragmática):
    Genera la imagen con overlay del heatmap y la descripción textual de zonas.
    """
    img, saliency_map = calcular_salience_map(imagen_path)

    if saliency_map is None:
        return {
            "status": "error",
            "mensaje": f"No se pudo cargar o procesar la imagen en {imagen_path}"
        }

    h, w = saliency_map.shape

    # Definición de Región Central vs Periferia (Análisis de 5 zonas)
    m_h, m_w = h // 2, w // 2
    margin_h, margin_w = h // 4, w // 4

    # ROI Central (el 50% central de la imagen)
    q_centro = np.mean(saliency_map[margin_h : h - margin_h, margin_w : w - margin_w])
    
    # Cuadrantes periféricos
    q_sup_izq = np.mean(saliency_map[0:m_h, 0:m_w])
    q_sup_der = np.mean(saliency_map[0:m_h, m_w:w])
    q_inf_izq = np.mean(saliency_map[m_h:h, 0:m_w])
    q_inf_der = np.mean(saliency_map[m_h:h, m_w:w])

    cuadrantes = {
        "Superior Izquierdo": q_sup_izq,
        "Superior Derecho": q_sup_der,
        "Inferior Izquierdo": q_inf_izq,
        "Inferior Derecho": q_inf_der
    }

    # Determinar si el centro domina sobre los cuadrantes periféricos
    promedio_periferia = np.mean(list(cuadrantes.values()))
    
    # Si la intensidad media del centro supera sensiblemente a la periferia
    es_foco_central = q_centro > (promedio_periferia * 1.25)

    if es_foco_central:
        zona_caliente_desc = "la zona Central / Núcleo de la composición."
        recorrido_sugerido = "Atención concentrada de manera focalizada y radial hacia el centro de la pieza."
    else:
        zona_caliente = max(cuadrantes, key=cuadrantes.get)
        zona_caliente_desc = f"el cuadrante {zona_caliente}."
        
        if q_sup_izq > q_inf_der and q_sup_der > q_inf_izq:
            recorrido_sugerido = "Se observa una tendencia de recorrido en Z (lectura horizontal superior y barrido hacia la base)."
        elif q_sup_izq > q_sup_der and q_inf_izq > q_inf_der:
            recorrido_sugerido = "Se observa una tendencia de recorrido en F (escaneo vertical primario en el margen izquierdo)."
        else:
            recorrido_sugerido = "Atención distribuida en la periferia de la composición."

    # Determinar Punto de Entrada
    _, _, _, max_loc = cv2.minMaxLoc(saliency_map)
    
    # Evaluar si el punto máximo está en el área central
    if margin_w <= max_loc[0] <= (w - margin_w) and margin_h <= max_loc[1] <= (h - margin_h):
        punto_entrada_desc = "El punto focal primario se ubica en el centro de la composición."
    else:
        pos_y_texto = "superior" if max_loc[1] < m_h else "inferior"
        pos_x_texto = "izquierda" if max_loc[0] < m_w else "derecha"
        punto_entrada_desc = f"El punto focal primario se ubica en el área {pos_y_texto}-{pos_x_texto} de la composición."

    # Construir Descripciones Finales (con evaluación de simetría en zonas frías)
    desc_zonas_calientes = f"La mayor concentración de atención visual (zona caliente) se localiza en {zona_caliente_desc}"
    
    # Detección inteligente de Zonas Frías (empates técnicos y franjas)
    val_min = min(cuadrantes.values())
    cuadrantes_frios = [q for q, val in cuadrantes.items() if val <= val_min * 1.15]

    if len(cuadrantes_frios) > 1:
        if "Inferior Izquierdo" in cuadrantes_frios and "Inferior Derecho" in cuadrantes_frios:
            desc_zonas_frias = "Las áreas de menor saliencia o zonas frías se concentran de manera simétrica en la franja inferior (base de la composición)."
        elif "Superior Izquierdo" in cuadrantes_frios and "Superior Derecho" in cuadrantes_frios:
            desc_zonas_frias = "Las áreas de menor saliencia o zonas frías se concentran de manera simétrica en la franja superior de la composición."
        else:
            nombres_frios = " e ".join([q.lower() for q in cuadrantes_frios])
            desc_zonas_frias = f"Las áreas de menor saliencia o zonas frías se distribuyen entre los cuadrantes {nombres_frios}."
    else:
        zona_fria = min(cuadrantes, key=cuadrantes.get)
        desc_zonas_frias = f"Las áreas de menor saliencia o zonas frías predominan en el cuadrante {zona_fria}."

    # Generación y Guardado de la Imagen con Overlay
    heatmap_color = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    output_dir = BASE_DIR / output_heatmap_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    nombre_base = Path(imagen_path).stem
    path_salida_heatmap = str(output_dir / f"heatmap_{nombre_base}.jpg")

    cv2.imwrite(path_salida_heatmap, overlay)

    # Salida limpia cumpliendo el requerimiento exacto
    return {
        "status": "success",
        "metrica": "Atención Predictiva / HeatMap (Pragmática)",
        "resultado": {
            "path_imagen_overlay": path_salida_heatmap,
            "descripcion_textual_zonas": {
                "punto_entrada_visual": punto_entrada_desc,
                "zonas_calientes": desc_zonas_calientes,
                "zonas_frias": desc_zonas_frias,
                "recorrido_visual_estimado": recorrido_sugerido
            }
        }
    }