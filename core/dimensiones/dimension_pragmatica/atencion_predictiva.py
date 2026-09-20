import cv2
import numpy as np
import os
import base64
import unicodedata
from pathlib import Path
from servicios.config import imread_unicode

def calcular_salience_map(imagen_path: str):
    """Calcula el mapa de saliencia combinando contraste espectral y atracción lumínica focal."""
    img = imread_unicode(imagen_path)
    if img is None:
        return None, None

    # 1. Saliencia espectral (texturas, bordes y anomalías visuales)
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    success, sal_spectral = saliency.computeSaliency(img)
    if not success:
        return None, None

    sal_spectral = (sal_spectral * 255).astype("uint8")

    # 2. Luminancia ponderada con estiramiento de contraste
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gris_norm = cv2.normalize(gris, None, 0, 255, cv2.NORM_MINMAX)

    # 3. Fusión: 75% saliencia espectral (sujeto/figura) + 25% luminancia
    saliency_combinada = cv2.addWeighted(sal_spectral, 0.75, gris_norm, 0.25, 0)
    
    # Suavizado para consolidar manchas continuas de atención
    saliency_map = cv2.GaussianBlur(saliency_combinada, (15, 15), 0)

    return img, saliency_map


def analizar_atencion_predictiva(imagen_path: str, output_heatmap_dir: str = "output/heatmaps") -> dict:
    """
    Subcapa Atención Predictiva (Pragmática):
    Genera la imagen con overlay del heatmap y la descripción textual coherente de zonas.
    """
    img, saliency_map = calcular_salience_map(imagen_path)

    if saliency_map is None:
        return {
            "status": "error",
            "mensaje": f"No se pudo cargar o procesar la imagen en {imagen_path}"
        }

    h, w = saliency_map.shape

    # 1. Localización del Núcleo Focal Primario (Punto de Entrada / Punctum)
    saliency_blur = cv2.GaussianBlur(saliency_map, (21, 21), 0)
    
    # Umbral dinámico en el percentil 92 para aislar los focos reales
    corte_top = np.percentile(saliency_blur, 92)
    _, thresh = cv2.threshold(saliency_blur, int(corte_top), 255, cv2.THRESH_BINARY)
    
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contornos:
        # Ponderamos contornos por: Área * (Intensidad media dentro del contorno ^ 1.5)
        mejor_cnt = None
        max_score = -1.0
        
        for cnt in contornos:
            mascara_cnt = np.zeros_like(saliency_blur)
            cv2.drawContours(mascara_cnt, [cnt], -1, 255, -1)
            media_val = cv2.mean(saliency_blur, mask=mascara_cnt)[0]
            area_cnt = cv2.contourArea(cnt)
            score = area_cnt * (media_val ** 1.5)
            if score > max_score:
                max_score = score
                mejor_cnt = cnt
                
        M = cv2.moments(mejor_cnt)
        if M["m00"] > 0:
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
        else:
            center_x, center_y = int(mejor_cnt[0][0][0]), int(mejor_cnt[0][0][1])
    else:
        _, _, _, (center_x, center_y) = cv2.minMaxLoc(saliency_blur)

    # 2. Clasificación espacial por tercios (3x3 grid)
    tercio_w = w // 3
    tercio_h = h // 3

    pos_y_idx = 0 if center_y < tercio_h else (2 if center_y > 2 * tercio_h else 1)
    pos_x_idx = 0 if center_x < tercio_w else (2 if center_x > 2 * tercio_w else 1)

    nombres_y = ["superior", "central", "inferior"]
    nombres_x = ["izquierda", "central", "derecha"]

    pos_y_texto = nombres_y[pos_y_idx]
    pos_x_texto = nombres_x[pos_x_idx]

    if pos_y_texto == "central" and pos_x_texto == "central":
        punto_entrada_desc = "El punto focal primario se ubica en el centro de la composición."
        zona_caliente_desc = "la zona Central / Núcleo de la composición."
    elif pos_y_texto == "central":
        punto_entrada_desc = f"El punto focal primario se ubica en el área central-{pos_x_texto} de la composición."
        zona_caliente_desc = f"el área Central {pos_x_texto.capitalize()} de la pieza."
    elif pos_x_texto == "central":
        punto_entrada_desc = f"El punto focal primario se ubica en el área {pos_y_texto}-central de la composición."
        zona_caliente_desc = f"el sector {pos_y_texto.capitalize()} Central de la composición."
    else:
        punto_entrada_desc = f"El punto focal primario se ubica en el área {pos_y_texto}-{pos_x_texto} de la composición."
        zona_caliente_desc = f"el cuadrante {pos_y_texto.capitalize()} {pos_x_texto.capitalize()}."

    # 3. Detección de Zonas Frías y Recorrido general
    m_h, m_w = h // 2, w // 2
    cuadrantes = {
        "Superior Izquierdo": float(np.mean(saliency_map[0:m_h, 0:m_w])),
        "Superior Derecho": float(np.mean(saliency_map[0:m_h, m_w:w])),
        "Inferior Izquierdo": float(np.mean(saliency_map[m_h:h, 0:m_w])),
        "Inferior Derecho": float(np.mean(saliency_map[m_h:h, m_w:w]))
    }

    zona_fria = min(cuadrantes, key=cuadrantes.get)
    desc_zonas_frias = f"Las áreas de menor saliencia o zonas frías predominan en el cuadrante {zona_fria}."

    if cuadrantes["Superior Izquierdo"] >= cuadrantes["Inferior Derecho"]:
        recorrido_sugerido = "Se observa una tendencia de recorrido en Z (lectura horizontal superior y barrido hacia la base)."
    else:
        recorrido_sugerido = "Atención focalizada con dispersión radial hacia las zonas secundarias."

    desc_zonas_calientes = f"La mayor concentración de atención visual (zona caliente) se localiza en {zona_caliente_desc}"

    # 4. Generación del Heatmap con Overlay
    heatmap_color = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

    success, buffer = cv2.imencode(".jpg", overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    heatmap_data_uri = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}" if success else ""

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
