import cv2
import numpy as np
from core.categorias.config import imread_unicode

def analizar_secuencia_narrativa(imagen_path: str) -> dict:
    """
    Subcapa Secuencia Narrativa (Pragmática):
    Evalúa el flujo del ojo en el tiempo y la aptitud para piezas seriadas,
    comics o packaging desplegable.
    """
    img = imread_unicode(imagen_path)
    if img is None:
        return {
            "status": "error",
            "mensaje": f"No se pudo cargar la imagen en {imagen_path}"
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    area_total = h * w

    # BÚSQUEDA DE CONTORNOS RECTANGULARES (Módulo de Paneles)
    # Aplicamos un umbral adaptativo para tolerar variaciones de iluminación y líneas finas
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    candidatos_paneles = []
    
    # Criterios estrictos para ser considerado una "viñeta/panel"
    area_minima = area_total * 0.04  # Al menos 4% de la pieza
    area_maxima = area_total * 0.70  # Máximo 70% (descarta el marco externo total)

    for cnt in contours:
        # Aproximación poligonal
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        
        # Debe tener 4 vértices (rectángulo/cuadrado)
        if len(approx) == 4:
            x, y, w_box, h_box = cv2.boundingRect(cnt)
            area = w_box * h_box
            
            if area_minima < area < area_maxima:
                # Comprobar la relación de aspecto del rectángulo (evita franjas muy finas como líneas de texto)
                aspecto_caja = w_box / float(h_box)
                if 0.3 < aspecto_caja < 3.0:
                    candidatos_paneles.append((x, y, w_box, h_box))

    # Filtrar rectángulos superpuestos/anidados (Non-Maximum Suppression simplificado)
    paneles_filtrados = []
    for box in candidatos_paneles:
        x, y, wb, hb = box
        es_duplicado = False
        for fx, fy, fwb, fhb in paneles_filtrados:
            # Si el centro está dentro de un panel ya aceptado, lo descartamos
            if abs(x - fx) < 30 and abs(y - fy) < 30:
                es_duplicado = True
                break
        if not es_duplicado:
            paneles_filtrados.append(box)

    paneles_detectados = len(paneles_filtrados)

    # EVALUACIÓN Y CLASIFICACIÓN
    aspect_ratio = w / float(h)

    # Si encontramos al menos 2 puestas en página estructuradas independientes
    if paneles_detectados >= 2:
        tipo_pieza = "Secuencial / Poliscénica (Cómics / Infografía / Paneles)"
        flujo_tiempo = f"Lectura secuencial estructurada en {paneles_detectados} paneles o secciones (narrativa temporal episódica)."
        aplicacion_sugerida = "Apto para historietas, instructivos paso a paso, infografías estructuradas o cómics."
    elif aspect_ratio > 2.2:
        tipo_pieza = "Formato Apaisado Extendido (Packaging desplegable / Banner panorámico)"
        flujo_tiempo = "Flujo horizontal progresivo a lo largo del plano (lectura continua de izquierda a derecha)."
        aplicacion_sugerida = "Especialmente apto para packaging desplegable, fajas de producto o afiches en serie lineal."
    elif aspect_ratio < 0.45:
        tipo_pieza = "Formato Vertical Extendido (Columna / Lomo / Packaging)"
        flujo_tiempo = "Flujo descendente progresivo (barrido vertical de la parte superior hacia la base)."
        aplicacion_sugerida = "Apto para caras laterales de packaging, tótems publicitarios o piezas verticales seriadas."
    else:
        tipo_pieza = "Monoscénica / Afiche Único"
        flujo_tiempo = "Lectura instantánea de cuadro único (captura del instante o concepto central)."
        aplicacion_sugerida = "Apto como afiche individual o portada. Para piezas seriadas requiere continuidad estilística con otras piezas."

    return {
        "status": "success",
        "metrica": "Secuencia Narrativa (Pragmática)",
        "resultado": {
            "estructura_formativa": tipo_pieza,
            "flujo_ojo_en_tiempo": flujo_tiempo,
            "aplicacion_narrativa_sugerida": aplicacion_sugerida,
            "paneles_o_secciones_detectadas": paneles_detectados
        }
    }