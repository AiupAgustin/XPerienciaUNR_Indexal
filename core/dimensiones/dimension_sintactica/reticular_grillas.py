
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
    

def generar_grilla_van_de_graaf(imagen_path, destino_path, color_lineas_bgr=(180, 180, 180), color_caja_bgr=(255, 0, 132), grosor=2):
    """
    Tarea: Superpone el Canon de Van de Graaf (proporciones de manuscritos medievales).
    Traza las diagonales principales de construcción y calcula la caja tipográfica resultante.
    Guarda el archivo modificado en el disco y retorna las coordenadas geométricas.
    """
    try:
        # 1. Cargamos la imagen original
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        h, w, _ = img.shape
        img_resultado = img.copy()
        
        # 2. Definimos los puntos clave de las esquinas (Eje Y invertido)
        sup_izq = (0, 0)
        sup_der = (w, 0)
        inf_izq = (0, h)
        inf_der = (w, h)
        punto_medio_sup = (int(w / 2), 0)
        
        # 3. Trazamos las líneas guía geométricas (Regla y Compás)
        # Diagonal Mayor
        cv2.line(img_resultado, sup_izq, inf_der, color_lineas_bgr, 1)
        # Diagonal Inversa
        cv2.line(img_resultado, inf_izq, sup_der, color_lineas_bgr, 1)
        # Diagonal a la mitad (para construcción del recto)
        cv2.line(img_resultado, inf_izq, punto_medio_sup, color_lineas_bgr, 1)
        
        # 4. Cálculo de la Caja Tipográfica (La proporción áurea de Van de Graaf es en novenos)
        x_inicio = int(w / 9)
        y_inicio = int(h / 9)
        x_fin = int(7 * w / 9)  # Deja 2/9 de margen externo
        y_fin = int(7 * h / 9)  # Deja 2/9 de margen inferior
        
        # 5. Dibujamos la caja de contenido principal (Por defecto un Magenta vibrante)
        cv2.rectangle(img_resultado, (x_inicio, y_inicio), (x_fin, y_fin), color_caja_bgr, grosor)
        
        # 6. Guardamos el resultado en el disco
        cv2.imwrite(destino_path, img_resultado)
        
        # Retornamos la metadata para el reporte técnico o el Front
        return {
            "status": "success",
            "archivo_generado": destino_path,
            "dimensiones_imagen": {"ancho": w, "alto": h},
            "caja_contenido": {
                "top_left": (x_inicio, y_inicio),
                "bottom_right": (x_fin, y_fin),
                "ancho_caja": x_fin - x_inicio,
                "alto_caja": y_fin - y_inicio
            },
            "margenes_calculados": {
                "superior": y_inicio,
                "inferior": h - y_fin,
                "interno_izq": x_inicio,
                "externo_der": w - x_fin
            }
        }
        
    except Exception as e:
        return {"error": f"Error al generar Canon de Van de Graaf: {str(e)}"}
    
def generar_grilla_diagonal_dinamica(imagen_path, destino_path, color_bgr=(255, 0, 255), grosor=1):
    """
    Tarea: Superpone una Grilla Diagonal Dinámica basada en la relación de aspecto del lienzo.
    Traza las diagonales principales y las líneas recíprocas desde los puntos medios 
    para marcar los ángulos armónicos de tensión visual.
    Guarda el archivo modificado en el disco y retorna los puntos clave calculados.
    """
    try:
        # 1. Cargamos la imagen original
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen desde la ruta: {imagen_path}"}
            
        h, w, _ = img.shape
        img_resultado = img.copy()
        
        # 2. Definimos las coordenadas de las esquinas
        sup_izq = (0, 0)
        sup_der = (w, 0)
        inf_izq = (0, h)
        inf_der = (w, h)
        
        # 3. Calculamos los puntos medios de los cuatro bordes (Centros de los ejes)
        medio_sup = (int(w / 2), 0)
        medio_inf = (int(w / 2), h)
        medio_izq = (0, int(h / 2))
        medio_der = (w, int(h / 2))
        centro_absoluto = (int(w / 2), int(h / 2))
        
        # 4. Dibujamos las Diagonales Principales del encuadre externo
        cv2.line(img_resultado, sup_izq, inf_der, color_bgr, grosor)
        cv2.line(img_resultado, inf_izq, sup_der, color_bgr, grosor)
        
        # 5. Dibujamos las líneas de tensión interna (Vectores recíprocos y rombo central)
        # Unimos puntos medios opuestos para marcar los ejes rectos principales
        cv2.line(img_resultado, medio_sup, medio_inf, color_bgr, grosor)
        cv2.line(img_resultado, medio_izq, medio_der, color_bgr, grosor)
        
        # Unimos los puntos medios entre sí para formar el diamante/rombo dinámico interno
        cv2.line(img_resultado, medio_sup, medio_der, color_bgr, grosor)
        cv2.line(img_resultado, medio_der, medio_inf, color_bgr, grosor)
        cv2.line(img_resultado, medio_inf, medio_izq, color_bgr, grosor)
        cv2.line(img_resultado, medio_izq, medio_sup, color_bgr, grosor)
        
        # 6. Guardamos físicamente la imagen resultante en el disco
        cv2.imwrite(destino_path, img_resultado)
        
        # Retornamos la metadata técnica de los vectores
        return {
            "status": "success",
            "archivo_generado": destino_path,
            "dimensiones_imagen": {"ancho": w, "alto": h},
            "puntos_clave": {
                "centro": centro_absoluto,
                "puntos_medios": {
                    "superior": medio_sup,
                    "inferior": medio_inf,
                    "izquierdo": medio_izq,
                    "derecho": medio_der
                }
            }
        }
        
    except Exception as e:
        return {"error": f"Error al generar grilla diagonal dinámica: {str(e)}"}