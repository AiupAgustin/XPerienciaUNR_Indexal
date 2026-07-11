
import cv2
import numpy as np

def detectar_lineas_y_angulos(imagen_path):
    """
    Usa Canny y la Transformada de Hough para encontrar las líneas rectas principales
    de la imagen y calcular sus ángulos en grados (0 a 180).
    """
    try:
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": "No se pudo cargar la imagen para el análisis eidético"}
            
        # 1. Pasamos a escala de grises y aplicamos un leve desenfoque para quitar ruido
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        desenfocado = cv2.GaussianBlur(gris, (5, 5), 0)
        
        # 2. Detectamos los bordes con Canny
        bordes = cv2.Canny(desenfocado, 50, 150, apertureSize=3)
        
        # 3. Transformada de Hough para encontrar segmentos de líneas rectas
        # Ajustamos los parámetros para que busque líneas principales y no ruido
        lineas = cv2.HoughLinesP(
            bordes, 
            rho=1, 
            theta=np.pi/180, 
            threshold=100, 
            minLineLength=40, 
            maxLineGap=10
        )
        
        angulos = []
        if lineas is not None:
            for linea in lineas:
                x1, y1, x2, y2 = linea[0]
                # Calculamos el ángulo en radianes y lo pasamos a grados
                angulo_rad = np.arctan2(y2 - y1, x2 - x1)
                angulo_deg = np.degrees(angulo_rad) % 180 # Normalizamos de 0 a 180
                angulos.append(float(angulo_deg))
                
        return angulos
        
    except Exception as e:
        return {"error": f"Error en detección de líneas: {str(e)}"}


def calcular_tension_kandinsky(imagen_path):
    """
    Tarea: Clasifica la composición según el predominio de ángulos (Kandinsky).
    Filtra y evalúa si dominan las diagonales (Tensión Dinámica Alta) o las horizontales/verticales (Estática).
    """
    try:
        angulos = detectar_lineas_y_angulos(imagen_path)
        
        # Si hubo un error en la lectura, arrastramos el diccionario de error
        if isinstance(angulos, dict) and "error" in angulos:
            return angulos
            
        if not angulos:
            return {
                "composicion": "Indeterminada",
                "detalle": "No se detectaron líneas rectas predominantes en la pieza visual.",
                "pct_diagonales": 0.0,
                "pct_ortogonales": 0.0
            }
            
        conteo_diagonales = 0  # Rangos cercanos a 45° y 135°
        conteo_ortogonales = 0  # Rangos cercanos a 0°/180° (horizontales) y 90° (verticales)
        
        # Margen de tolerancia de ej: 22.5 grados alrededor de los ejes para segmentar de forma justa
        for ang in angulos:
            # Diagonales: entre 22.5 y 67.5 (entorno a 45) o entre 112.5 y 157.5 (entorno a 135)
            if (22.5 <= ang < 67.5) or (112.5 <= ang < 157.5):
                conteo_diagonales += 1
            # Estáticas (Horizontales y Verticales)
            elif (0 <= ang < 22.5) or (67.5 <= ang < 112.5) or (157.5 <= ang <= 180):
                conteo_ortogonales += 1
                
        total = len(angulos)
        pct_diag = (conteo_diagonales / total) * 100
        pct_orto = (conteo_ortogonales / total) * 100
        
        # Aplicamos la regla compositiva de Kandinsky
        if pct_diag > pct_orto:
            clasificacion = "Tensión Dinámica Alta"
            diagnostico = "Predominan las líneas diagonales, generando un clima visual de inestabilidad, movimiento y fuerza activa."
        else:
            clasificacion = "Composición Estática"
            diagnostico = "Predominan las líneas horizontales y verticales, reforzando nociones de estabilidad, equilibrio, calma o estructura rígida."
            
        return {
            "clasificacion_kandinsky": clasificacion,
            "analisis_semiotico": diagnostico,
            "metricas": {
                "total_lineas_detectadas": total,
                "porcentaje_diagonales_45_135": round(pct_diag, 2),
                "porcentaje_estaticas_0_90": round(pct_orto, 2)
            }
        }
        
    except Exception as e:
        return {"error": f"Error en análisis de tensión: {str(e)}"}