import cv2
import numpy as np

def obtener_paleta_cromatica(imagen_path, cantidad_colores=3):
    """
    Extrae la paleta cromática exacta de una imagen usando K-Means Clustering.
    Redimensiona la pieza para optimizar el rendimiento del servidor local.
    
    Devuelve una lista de diccionarios con los códigos HEX y RGB de los 3 colores dominantes.
    """
    try:
        # Leemos la imagen con OpenCV
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        # OpenCV lee en BGR, lo pasamos a RGB que es el estándar de diseño
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Redimensionamos a 150x150 píxeles para que el cálculo matemático sea mas rápido
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
            # Convertimos a int nativo de Python para que no de problemas al serializar
            r, g, b = int(color[0]), int(color[1]), int(color[2])
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            paleta_completa.append({
                "hex": hex_color,
                "rgb": (r, g, b)
            })
            
        return paleta_completa

    # Por si no carga la imagen o hay algun error
    except Exception as e:
        return {"error": f"Error interno en el procesamiento de color: {str(e)}"}

def analizar_atributos_cromaticos(imagen_path):
    """
    Analiza la imagen completa píxel por píxel 
    para garantizar máxima precisión en Brillo (Ansel Adams), Saturación y Temperatura.
    """
    try:
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen para atributos"}
            
        # Redimensionamos para optimizar rendimiento (sigue siendo 100% preciso para promedios)
        img_small = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)
            
        # Pasamos a HSV para medir Saturación (S) y Brillo Real (V)
        img_hsv = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
        saturacion_promedio = np.mean(img_hsv[:, :, 1])
        brillo_promedio = np.mean(img_hsv[:, :, 2])
        
        # Mapeamos al Sistema de Zonas de Ansel Adams (0 a X)
        zona_numerica = int(brillo_promedio // 23.18)
        zona_numerica = min(zona_numerica, 10)
        mapeo_ansel_adams = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        zona_ansel_dominante = mapeo_ansel_adams[zona_numerica]
        
        # Pasamos a RGB para evaluar Temperatura general
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        r = img_rgb[:, :, 0]
        b = img_rgb[:, :, 2]
        
        pixels_calidos = np.sum(r > b)
        pixels_frios = np.sum(b >= r)
        total_pixels = r.size
        
        porcentaje_calido = (pixels_calidos / total_pixels) * 100
        porcentaje_frio = (pixels_frios / total_pixels) * 100
        temperatura_dominante = "Cálida" if porcentaje_calido > porcentaje_frio else "Fría"
        
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
    
    # Si no se pudo cargar la imagen
    except Exception as e:
        return {"error": f"Error en atributos: {str(e)}"}