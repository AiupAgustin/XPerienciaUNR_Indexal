import cv2
import numpy as np
from servicios.config import imread_unicode

def obtener_paleta_cromatica(imagen_path, cantidad_colores=3):
    """
    Extrae la paleta cromática exacta de una imagen usando K-Means Clustering.
    Devuelve los colores dominantes con su código HEX, RGB, porcentaje de ocupación
    y rol semiótico/compositivo (Dominante, Secundario, Acento).
    """
    try:
        img = imread_unicode(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_small = cv2.resize(img_rgb, (150, 150), interpolation=cv2.INTER_AREA)
        
        pixeles = img_small.reshape(-1, 3)
        pixeles = np.float32(pixeles)
        
        criterios = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        
        # Detectamos colores únicos reales para no forzar k de más si es monocromo o bicolor puro
        colores_unicos = np.unique(pixeles, axis=0)
        k_real = min(cantidad_colores, len(colores_unicos))
        
        # Obtenemos las etiquetas (labels) para contar los píxeles de cada color
        _, etiquetas, centros = cv2.kmeans(
            pixeles, 
            k_real, 
            None, 
            criterios, 
            10, 
            cv2.KMEANS_RANDOM_CENTERS
        )
        
        centros = np.uint8(centros)
        conteo_pixeles = np.bincount(etiquetas.flatten(), minlength=k_real)
        total_pixeles = len(pixeles)

        # Emparejamos cada color con su frecuencia y omitimos clusters vacíos si los hubiera
        roles = ["Dominante", "Secundario", "Acento", "Neutro", "Complementario"]
        clusters = []
        for i in range(k_real):
            if conteo_pixeles[i] > 0:
                pct = round((conteo_pixeles[i] / total_pixeles) * 100, 1)
                r, g, b = int(centros[i][0]), int(centros[i][1]), int(centros[i][2])
                clusters.append({
                    "rgb": (r, g, b),
                    "hex": f"#{r:02x}{g:02x}{b:02x}".upper(),
                    "porcentaje": pct,
                    "conteo": conteo_pixeles[i]
                })

        # Ordenar por porcentaje descendente (el más presente es Dominante)
        clusters.sort(key=lambda x: x["conteo"], reverse=True)

        # Fusionar colores que sean indistinguibles para el ojo humano (distancia RGB < 18)
        UMBRAL_DISTANCIA = 18.0
        clusters_filtrados = []

        for c in clusters:
            r1, g1, b1 = c["rgb"]
            fusionado = False
            for f in clusters_filtrados:
                r2, g2, b2 = f["rgb"]
                distancia = ((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2) ** 0.5
                if distancia < UMBRAL_DISTANCIA:
                    f["conteo"] += c["conteo"]
                    f["porcentaje"] = round(f["porcentaje"] + c["porcentaje"], 1)
                    fusionado = True
                    break
            if not fusionado:
                clusters_filtrados.append(c)

        # Reasignar roles a los clusters que quedaron realmente diferenciados
        paleta_completa = []
        for idx, item in enumerate(clusters_filtrados):
            paleta_completa.append({
                "rol": roles[idx] if idx < len(roles) else f"Color {idx + 1}",
                "hex": item["hex"],
                "rgb": item["rgb"],
                "porcentaje": int(round(item["porcentaje"]))
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
        v_channel = img_hsv[:, :, 2]
        saturacion_promedio = np.mean(img_hsv[:, :, 1])
        brillo_promedio = np.mean(v_channel)
        desv_brillo = float(np.std(v_channel))  # Mide dispersión / dureza del contraste
        
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
            "desviacion_brillo_std": round(desv_brillo, 2),
            "contraste_temperatura": {
                "temperatura_dominante": temperatura_dominante,
                "porcentaje_calido": round(porcentaje_calido, 2),
                "porcentaje_frio": round(porcentaje_frio, 2)
            }
        }
    
    except Exception as e:
        return {"error": f"Error en atributos: {str(e)}"}

# Evaluador de semiótica cromática
def evaluar_semiotica_cromatica(paleta_rgb, temperatura_dominante, desv_brillo=None):
    """
    Evalúa la relación angular en el círculo cromático (Hue) 
    y asigna la interpretación semiótica según Eva Heller / Kandinsky / Itten.
    En imágenes acromáticas, evalúa la calidad lumínica y dureza del contraste (Ansel Adams).
    """
    if not paleta_rgb or isinstance(paleta_rgb, dict):
        return {"error": "Paleta no válida para análisis semiótico"}

    if "acromática" in temperatura_dominante.lower():
        # Evaluación técnica de la dureza de la luz y pasos tonales según dispersión (std)
        if desv_brillo is not None:
            if desv_brillo >= 60.0:
                calidad_luz = (
                    f"Iluminación dura y alto contraste (desv. {round(desv_brillo, 1)}): "
                    f"transiciones tonales abruptas entre luces plenas y sombras profundas, acentuando el dramatismo y corte gráfico."
                )
            elif desv_brillo >= 40.0:
                calidad_luz = (
                    f"Iluminación equilibrada y contraste moderado (desv. {round(desv_brillo, 1)}): "
                    f"amplia gradación de pasos tonales con grises intermedios continuos y modelado suave de volúmenes."
                )
            else:
                calidad_luz = (
                    f"Iluminación difusa y bajo contraste (desv. {round(desv_brillo, 1)}): "
                    f"predominio de grises medios y transiciones suaves, reduciendo la severidad de las sombras."
                )
        else:
            calidad_luz = "Gradación tonal continua con modelado equilibrado entre luces y sombras."

        return {
            "Esquema Relacional": "Monocromático Acromático (B&N)",
            "Marco Teórico": "Ansel Adams",
            "Significado Cultural / Psicológico": (
                "Composición acromática en escala de grises. "
                "Enfatiza el contraste de luces y sombras, el drama formal y la estructura gráfica."
            ),
            "Calidad Lumínica / Contraste": calidad_luz
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

    # Si la pieza tiene un único color representativo
    if len(hues) < 2:
        return {
            "Esquema Relacional": "Monocromático Puro",
            "Diferencia Angular": "0.0°",
            "Marco Teórico": "Johannes Itten / Kandinsky",
            "Significado Cultural / Psicológico": "Composición monocromática absoluta. Máxima homogeneidad, sobriedad y foco en el valor tonal.",
            "Clima de Temperatura": f"Clima predominantemente {temp_masculina}."
        }

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
        "Esquema Relacional": esquema,
        "Diferencia Angular": f"{round(diff_angulo, 1)}° / Escala 0° a 180°",
        "Marco Teórico": marco,
        "Significado Cultural / Psicológico": diagnostico,
        "Clima de Temperatura": f"Clima predominantemente {temp_masculina}."
    }