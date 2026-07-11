
import cv2
import numpy as np

def generar_grilla_tercios(imagen_path, destino_path, color_bgr=(0, 255, 0), grosor=2):
    """
    Tarea: Superpone la Grilla de Tercios (líneas al 33.3% y 66.6%) sobre la imagen.
    Calcula y registra las coordenadas de los 4 puntos de poder (intersecciones).
    Guarda el resultado físicamente en la PC/Servidor en la ruta de destino.
    """
    try:
        # 1. Cargamos la imagen desde la ruta que guardó el backend
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        # Obtenemos las dimensiones reales (Alto, Ancho)
        h, w, _ = img.shape
        
        # 2. Calculamos las posiciones exactas de las líneas divisorias
        x1, x2 = int(w / 3), int(2 * w / 3)
        y1, y2 = int(h / 3), int(2 * h / 3)
        
        # Creamos una copia para dibujar encima sin romper la imagen original en memoria
        img_resultado = img.copy()
        
        # 3. Dibujamos las 2 líneas verticales (cv2.line pide: imagen, inicio, fin, color, grosor)
        cv2.line(img_resultado, (x1, 0), (x1, h), color_bgr, grosor)
        cv2.line(img_resultado, (x2, 0), (x2, h), color_bgr, grosor)
        
        # 4. Dibujamos las 2 líneas horizontales
        cv2.line(img_resultado, (0, y1), (w, y1), color_bgr, grosor)
        cv2.line(img_resultado, (0, y2), (w, y2), color_bgr, grosor)
        
        # 5. Estructuramos las coordenadas de los 4 puntos de poder
        puntos_de_poder = [
            {"punto": "Superior Izquierdo", "coordenadas": (x1, y1)},
            {"punto": "Superior Derecho", "coordenadas": (x2, y1)},
            {"punto": "Inferior Izquierdo", "coordenadas": (x1, y2)},
            {"punto": "Inferior Derecho", "coordenadas": (x2, y2)}
        ]
        
        # 6. Guardamos físicamente la nueva imagen con la grilla dibujada en el disco
        cv2.imwrite(destino_path, img_resultado)
        
        # Retornamos el reporte del éxito de la operación y los datos geométricos
        return {
            "status": "success",
            "archivo_generado": destino_path,
            "dimensiones_imagen": {"ancho": w, "alto": h},
            "lineas_verticales_x": [x1, x2],
            "lineas_horizontales_y": [y1, y2],
            "puntos_de_poder": puntos_de_poder
        }
        
    except Exception as e:
        return {"error": f"Error al generar grilla de tercios: {str(e)}"}
    
    
def generar_grilla_aurea(imagen_path, destino_path, color_bgr=(255, 0, 0), grosor=2):
    """
    Tarea: Superpone la Grilla Áurea basada en la divina proporción (phi = 1.618033).
    Calcula las líneas divisorias al 38.2% y 61.8% del ancho y alto.
    Guarda el archivo modificado físicamente en la PC/Servidor.
    """
    try:
        # 1. Cargamos la imagen original
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        h, w, _ = img.shape
        
        # 2. Matemáticas de la proporción áurea (Factor exacto: 1 / 1.61803398875)
        # Línea 1 (38.2% aprox) y Línea 2 (61.8% aprox)
        x1 = int(w * 0.381966)
        x2 = int(w * 0.618033)
        
        y1 = int(h * 0.381966)
        y2 = int(h * 0.618033)
        
        # Creamos la copia para no destruir la imagen original en memoria
        img_resultado = img.copy()
        
        # 3. Dibujamos las 2 líneas verticales (Por defecto Azul: BGR 255, 0, 0)
        cv2.line(img_resultado, (x1, 0), (x1, h), color_bgr, grosor)
        cv2.line(img_resultado, (x2, 0), (x2, h), color_bgr, grosor)
        
        # 4. Dibujamos las 2 líneas horizontales
        cv2.line(img_resultado, (0, y1), (w, y1), color_bgr, grosor)
        cv2.line(img_resultado, (0, y2), (w, y2), color_bgr, grosor)
        
        # 5. Registramos las coordenadas de los 4 puntos áureos de intersección
        puntos_aureos = [
            {"punto": "Intersección Áurea Sup-Izk", "coordenadas": (x1, y1)},
            {"punto": "Intersección Áurea Sup-Der", "coordenadas": (x2, y1)},
            {"punto": "Intersección Áurea Inf-Izk", "coordenadas": (x1, y2)},
            {"punto": "Intersección Áurea Inf-Der", "coordenadas": (x2, y2)}
        ]
        
        # 6. Guardamos físicamente la nueva imagen con la grilla áurea en el disco
        cv2.imwrite(destino_path, img_resultado)
        
        # Retornamos las métricas geométricas exactas para tu Front/Base de datos
        return {
            "status": "success",
            "archivo_generado": destino_path,
            "dimensiones_imagen": {"ancho": w, "alto": h},
            "lineas_verticales_x": [x1, x2],
            "lineas_horizontales_y": [y1, y2],
            "puntos_aureos": puntos_aureos
        }
        
    except Exception as e:
        return {"error": f"Error al generar grilla áurea: {str(e)}"}
    

def generar_grilla_muller_brockmann(imagen_path, destino_path, columnas=4, filas=4, calle=15, color_bgr=(0, 165, 255), grosor=2):
    """
    Tarea: Superpone una Grilla Modular de Müller-Brockmann con columnas, filas y calles (gutters).
    Calcula dinámicamente el tamaño de los módulos restando el espacio de las calles intermedias.
    Guarda el resultado físico en el disco y retorna el mapa de coordenadas de los bloques.
    """
    try:
        # 1. Cargamos la imagen original
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        h, w, _ = img.shape
        img_resultado = img.copy()
        
        # 2. Matemáticas de las calles (Si hay N columnas, hay N-1 calles en el medio)
        ancho_total_calles = (columnas - 1) * calle
        alto_total_calles = (filas - 1) * calle
        
        # Tamaño neto de cada módulo individual (flexible según el tamaño de la imagen)
        ancho_modulo = (w - ancho_total_calles) / columnas
        alto_modulo = (h - alto_total_calles) / filas
        
        modulos_coordenadas = []
        
        # 3. Doble bucle para recorrer la matriz y dibujar módulo por módulo
        for i in range(columnas):
            for j in range(filas):
                # Calculamos el píxel de inicio y fin para el rectángulo actual
                x_inicio = int(i * (ancho_modulo + calle))
                y_inicio = int(j * (alto_modulo + calle))
                x_fin = int(x_inicio + ancho_modulo)
                y_fin = int(y_inicio + alto_modulo)
                
                # Guardamos la data de este bloque para tu futuro Front
                modulos_coordenadas.append({
                    "modulo": f"Col_{i}_Fila_{j}",
                    "top_left": (x_inicio, y_inicio),
                    "bottom_right": (x_fin, y_fin)
                })
                
                # Dibujamos el contorno del rectángulo (Color Naranja por defecto: BGR 0, 165, 255)
                cv2.rectangle(img_resultado, (x_inicio, y_inicio), (x_fin, y_fin), color_bgr, grosor)
                
        # 4. Guardamos físicamente la imagen resultante en el disco
        cv2.imwrite(destino_path, img_resultado)
        
        # Retornamos toda la metadata técnica de la retícula
        return {
            "status": "success",
            "archivo_generado": destino_path,
            "configuracion_grilla": {"columnas": columnas, "filas": filas, "calle_px": calle},
            "dimensiones_modulos": {"ancho_modulo": round(ancho_modulo, 2), "alto_modulo": round(alto_modulo, 2)},
            "modulos": modulos_coordenadas
        }
        
    except Exception as e:
        return {"error": f"Error al generar grilla Müller-Brockmann: {str(e)}"}
    

