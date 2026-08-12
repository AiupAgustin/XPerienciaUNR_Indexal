import cv2
import numpy as np
from core.categorias.config import imread_unicode

def obtener_paleta_cromatica(imagen_path, cantidad_colores=3):
    """
    Extrae la paleta cromática exacta de una imagen usando K-Means Clustering.
    Redimensiona la pieza para optimizar el rendimiento del servidor local.
    
    Devuelve una lista de diccionarios con los códigos HEX y RGB de los 3 colores dominantes.
    """
    try:
        # Leemos la imagen con OpenCV
        img = imread_unicode(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        # OpenCV lee en BGR, lo pasamos a RGB que es el estándar de diseño
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Redimensionamos a 150x150 píxeles para que el cálculo matemático sea más rápido
        img_small = cv2.resize(img_rgb, (150, 150), interpolation=cv2.INTER_AREA)
        
        # Transformamos la matriz de la imagen en una lista plana de píxeles (R, G, B)
        pixeles = img_small.reshape(-1, 3)
        pixeles = np.float32(pixeles) # OpenCV exige que los datos sean de tipo flotante para K-Means
        
        # Definimos los criterios de parada (10 iteraciones o precisión de 1.0)
        criterios = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        
        # Ejecutamos K-Means para agrupar los colores en 'k' clusters (familias)
        _, _, centros = cv2.kmeans(
            pixeles, 
            cantidad_colores, 
            None, 
            criterios, 
            10, 
            cv2.KMEANS_RANDOM_CENTERS
        )
        
        # Convertimos los centros de los grupos a números enteros (0-255)
        centros = np.uint8(centros)
        
        # Iteramos los colores encontrados y guardamos tanto HEX como RGB en diccionarios
        paleta_completa = []
        for color in centros:
            # Convertimos a int nativo de Python para que no dé problemas al serializar
            r, g, b = int(color[0]), int(color[1]), int(color[2])
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            paleta_completa.append({
                "hex": hex_color,
                "rgb": (r, g, b)
            })
            
        return paleta_completa

    except Exception as e:
        return {"error": f"Error interno en el procesamiento de color: {str(e)}"}

def analizar_atributos_cromaticos(imagen_path):
    """
    Analiza la imagen completa píxel por píxel 
    para garantizar máxima precisión en Brillo (Ansel Adams), Saturación y Temperatura.
    """
    try:
        img = imread_unicode(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen para atributos"}
            
        # Redimensionamos para optimizar rendimiento
        img_small = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)
            
        # Pasamos a HSV para medir Saturación (S) y Brillo Real (V)
        img_hsv = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
        saturacion_promedio = np.mean(img_hsv[:, :, 1])
        brillo_promedio = np.mean(img_hsv[:, :, 2])
        
        # Mapeamos al Sistema de Zonas de Ansel Adams
        zona_numerica = int(brillo_promedio // 23.18)
        zona_numerica = min(zona_numerica, 10)
        mapeo_ansel_adams = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        zona_ansel_dominante = mapeo_ansel_adams[zona_numerica]
        
        if saturacion_promedio < 18.0:
            temperatura_dominante = "Acromática / Neutra"
            porcentaje_calido = 0.0
            porcentaje_frio = 0.0
        else:
            # Evaluación precisa de temperatura usando espacio CIELAB (Eje b* = Azul vs Amarillo)
            img_lab = cv2.cvtColor(img_small, cv2.COLOR_BGR2LAB)
            b_channel = img_lab[:, :, 2].astype(np.float32) - 128.0  # b* > 0 cálido, b* < 0 frío
            
            # Subimos el umbral a 8.0 para que el concreto solar no sume como cálido
            umbral = 8.0
            pixels_calidos = np.sum(b_channel > umbral)
            pixels_frios = np.sum(b_channel < -umbral)
            total_pixels = b_channel.size
            
            porcentaje_calido = (pixels_calidos / total_pixels) * 100
            porcentaje_frio = (pixels_frios / total_pixels) * 100
            
            # ACA VA EL CAMBIO:
            # Si los porcentajes están cerca (menos de 10% de diferencia), la pieza se considera equilibrada/neutra
            diferencia_temp = abs(porcentaje_calido - porcentaje_frio)
            
            if diferencia_temp < 10.0:
                temperatura_dominante = "Neutra / Equilibrada"
            elif porcentaje_calido > porcentaje_frio:
                temperatura_dominante = "Cálida"
            else:
                temperatura_dominante = "Fría"
        
        return {
            "brillo_promedio_0_255": round(float(brillo_promedio), 2),
            "ansel_adams_zona_promedio": zona_ansel_dominante,
            "saturacion_promedio_0_255": round(float(saturacion_promedio), 2),
            "contraste_temperatura": {
                "temperatura_dominante": temperatura_dominante,
                "porcentaje_calido": round(porcentaje_calido, 2),
                "porcentaje_frio": round(porcentaje_frio, 2)
            }
        }
    
    except Exception as e:
        return {"error": f"Error en atributos: {str(e)}"}

# Evaluador de semiótica cromática
def evaluar_semiotica_cromatica(paleta_rgb, temperatura_dominante):
    """
    Evalúa la relación angular en el círculo cromático (Hue) 
    y asigna la interpretación semiótica según Eva Heller / Kandinsky / Itten.
    """
    if not paleta_rgb or isinstance(paleta_rgb, dict):
        return {"error": "Paleta no válida para análisis semiótico"}

    if "acromática" in temperatura_dominante.lower():
        return {
            "esquema_relacional": "Monocromático Acromático (B&N)",
            "diferencia_angular_grados": 0.0,
            "marco_teorico": "Eva Heller / Ansel Adams",
            "significado_cultural_psicologico": (
                "Composición acromática en escala de grises. "
                "Enfatiza el contraste de luces y sombras, el drama formal y la estructura gráfica."
            ),
            "clima_temperatura": "Clima acromático / neutro."
        }

    # Mapeo explícito para la concordancia gramatical
    mapa_gramatical = {
        "cálida": "cálido",
        "fría": "frío",
        "neutra / equilibrada": "neutro / equilibrado"
    }
    temp_key = temperatura_dominante.lower()
    temp_masculina = mapa_gramatical.get(temp_key, temp_key)

    # Extraemos el valor Hue (0° a 360°) de cada color de la paleta
    hues = []
    for item in paleta_rgb:
        r, g, b = item["rgb"]
        pixel_rgb = np.uint8([[[r, g, b]]])
        pixel_hsv = cv2.cvtColor(pixel_rgb, cv2.COLOR_RGB2HSV)[0][0]
        hue_deg = float(pixel_hsv[0]) * 2.0  # Mapeo a 360°
        hues.append(hue_deg)

    # Evaluamos la relación angular entre los dos colores más prominentes
    h1, h2 = hues[0], hues[1]
    diff_angulo = min(abs(h1 - h2), 360 - abs(h1 - h2))

    # Determinamos el esquema de composición
    if diff_angulo < 45:
        esquema = "Análogo"
        marco = "Johannes Itten / Eva Heller"
        diagnostico = "Dominio de continuidad y armonía cromática. Transmite cohesión, serenidad y fluidez sin tensiones bruscas."
    elif 135 <= diff_angulo <= 225:
        esquema = "Complementario"
        marco = "Kandinsky / Itten"
        diagnostico = "Alta polaridad y vibración visual. Genera un fuerte contraste dramático, dinamismo y un punto de atracción inmediato."
    else:
        esquema = "Tríada / Acorde Disonante"
        marco = "Eva Heller"
        diagnostico = "Diversidad cromática estimulante. Adecuada para composiciones complejas, narrativa social o gráfica publicitaria dinámicas."

    return {
        "esquema_relacional": esquema,
        "diferencia_angular_grados": round(diff_angulo, 1),
        "marco_teorico": marco,
        "significado_cultural_psicologico": diagnostico,
        "clima_temperatura": f"Clima predominantemente {temp_masculina}."
    }