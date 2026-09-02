import cv2
import numpy as np
import os
import base64
import unicodedata
from pathlib import Path
from core.categorias.config import imread_unicode

def calcular_salience_map(imagen_path: str):
    """Calcula el mapa de saliencia visual usando el algoritmo de OpenCV."""
    img = imread_unicode(imagen_path)
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

    # Definición de Región Central vs Periferia
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

    # En lugar de 1 solo píxel (sensible a ruido), buscamos el centro de masa de la zona de mayor saliencia
    # Aplicamos un umbral para quedarnos solo con el top 10% de áreas más calientes
    umbral_corte = int(np.percentile(saliency_map, 90))
    _, thresh = cv2.threshold(saliency_map, umbral_corte, 255, cv2.THRESH_BINARY)
    
    # Si la imagen tiene zonas calientes claras
    M = cv2.moments(thresh)
    if M["m00"] > 0:
        # Centroide ponderado de las zonas de mayor intensidad visual
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
    else:
        # Fallback si no supera el umbral: usamos minMaxLoc sobre imagen desenfocada
        saliency_suave = cv2.GaussianBlur(saliency_map, (21, 21), 0)
        _, _, _, (center_x, center_y) = cv2.minMaxLoc(saliency_suave)

    # Evaluamos posición del centroide usando división por tercios (3x3 grid)
    tercio_w = w // 3
    tercio_h = h // 3

    pos_y_texto = "superior" if center_y < tercio_h else ("inferior" if center_y > 2 * tercio_h else "central")
    pos_x_texto = "izquierda" if center_x < tercio_w else ("derecha" if center_x > 2 * tercio_w else "central")

    if pos_y_texto == "central" and pos_x_texto == "central":
        punto_entrada_desc = "El punto focal primario se ubica en el centro de la composición."
    elif pos_y_texto == "central":
        punto_entrada_desc = f"El punto focal primario se ubica en el área central-{pos_x_texto} de la composición."
    elif pos_x_texto == "central":
        punto_entrada_desc = f"El punto focal primario se ubica en el área {pos_y_texto}-central de la composición."
    else:
        punto_entrada_desc = f"El punto focal primario se ubica en el área {pos_y_texto}-{pos_x_texto} de la composición."

    # Construir Descripciones Finales
    desc_zonas_calientes = f"La mayor concentración de atención visual (zona caliente) se localiza en {zona_caliente_desc}"
    
    # Detección inteligente de Zonas Frías
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

    # Generación de la Imagen con Overlay en memoria RAM (sin tocar disco)
    heatmap_color = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

    success, buffer = cv2.imencode(".jpg", overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if success:
        b64_str = base64.b64encode(buffer).decode("utf-8")
        heatmap_data_uri = f"data:image/jpeg;base64,{b64_str}"
    else:
        heatmap_data_uri = ""

    return {
        "status": "success",
        "metrica": "Atención Predictiva / HeatMap (Pragmática)",
        "resultado": {
            "path_imagen_overlay": heatmap_data_uri,
            "descripcion_textual_zonas": {
                "punto_entrada_visual": punto_entrada_desc,
                "zonas_calientes": desc_zonas_calientes,
                "zonas_frias": desc_zonas_frias,
                "recorrido_visual_estimado": recorrido_sugerido
            }
        }
    }
