import cv2
import numpy as np
from servicios.config import imread_unicode

def evaluar_contraste_figura_fondo(imagen_path):
    """
    Evalúa la legibilidad analizando el rango dinámico (luminancia) 
    y la densidad de ruido/bordes en el fondo (simulando WCAG + Histograma de bordes).
    Retorna un veredicto categórico: 'Strong', 'Fair' o 'Weak'.
    """
    try:
        # Cargamos la imagen original
        img = imread_unicode(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen: {imagen_path}"}
            
        # Convertimos a escala de grises para analizar luminancia pura (brillo)
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gris.shape
        
        # Análisis del Histograma y Rango Dinámico (Luminancia)
        # Calculamos los percentiles para entender qué tan separados están los oscuros de los claros
        # Esto es para no tomar lo 100% blanco o negro que pueden ser pocos pixeles
        p10 = np.percentile(gris, 10)  # Zona de sombras (figura o fondo oscuro)
        p90 = np.percentile(gris, 90)  # Zona de luces (figura o fondo claro)
        
        # Simulación del ratio de contraste basado en el rango dinámico percibido
        # La fórmula WCAG simplificada busca la relación entre el punto más claro y el más oscuro
        # Para WCAG hay que calcular la relacion entre el color mas claro y mas oscuro
        # Le sumo 0.05 al denominador por si p10 es cero por ser 100% negro
        ratio_perceptual = (p90 + 0.05) / (p10 + 0.05)
        
        # Análisis de Densidad de Bordes (Fondo ruidoso vs liso)
        # Usamos Canny para detectar todas las altas frecuencias (texturas, micro-bordes)
        bordes = cv2.Canny(gris, 50, 150)
        total_pixeles_borde = np.sum(bordes == 255)
        densidad_bordes = (total_pixeles_borde / (h * w)) * 100  # Porcentaje de ruido
        
        # Matriz de Decisión (Lógica de negocio para clasificar)
        # Un ratio WCAG alto (> 4.5) con pocos bordes de fondo es ideal (Strong)
        if ratio_perceptual >= 4.5 and densidad_bordes < 5.0:
            veredicto = "Strong"
            nota = "Excelente contraste de luminancia y fondo limpio que estaca la figura."
        
        # igual a 3 es el minimo aceptable
        elif ratio_perceptual >= 3.0 and densidad_bordes < 10.0:
            veredicto = "Fair"
            nota = "Contraste aceptable, pero el fondo presenta texturas o variaciones que complican la lectura."
        else:
            veredicto = "Weak"
            nota = "Contraste deficiente o fondo con excesivo ruido visual. Riesgo alto de empastamiento."
            
        return {
            "status": "success",
            "metrica": "Contraste Figura-Fondo",
            "veredicto": veredicto,
            "detalles_tecnicos": {
                "ratio_perceptual_wcag": round(ratio_perceptual, 2),
                "densidad_ruido_bordes_porcentaje": round(densidad_bordes, 2),
                "descripcion": nota
            }
        }
        
    except Exception as e:
        return {"error": f"Error en análisis de contraste: {str(e)}"}
    

def evaluar_solidez_estructural(imagen_path, tipo_grilla="tercios"):
    """
    Mide la alineación exacta calculando las líneas guía específicas 
    para cada una de las grillas del sistema.
    """
    try:
        img = imread_unicode(imagen_path)
        if img is None:
            return {"error": f"No se pudo cargar la imagen: {imagen_path}"}
        h, w, _ = img.shape
        
        lineas_referencia_x = []
        lineas_referencia_y = []
        
        # MATEMÁTICA DE LÍNEAS GUÍA REALES PARA CADA GRILLA
        if tipo_grilla == "tercios":
            lineas_referencia_x = [int(w / 3), int(2 * w / 3)]
            lineas_referencia_y = [int(h / 3), int(2 * h / 3)]
            
        elif tipo_grilla == "van_de_graaf":
            lineas_referencia_x = [int(w / 9), int(7 * w / 9)]
            lineas_referencia_y = [int(h / 9), int(7 * h / 9)]
            
        elif tipo_grilla == "modular":
            # Müller-Brockmann estándar: calculamos calles en cuartos (4x4)
            lineas_referencia_x = [int(w / 4), int(w / 2), int(3 * w / 4)]
            lineas_referencia_y = [int(h / 4), int(h / 2), int(3 * h / 4)]
            
        elif tipo_grilla == "diagonal_dinamica":
            # Para diagonales, evaluamos alineación con los centros de los ejes y el centro absoluto
            lineas_referencia_x = [int(w / 2)]
            lineas_referencia_y = [int(h / 2)]
            
        else:
            lineas_referencia_x = [int(w / 3), int(2 * w / 3)]
            lineas_referencia_y = [int(h / 3), int(2 * h / 3)]

        # Procesamiento de contornos para detectar bloques
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        desenfoque = cv2.GaussianBlur(gris, (7, 7), 0)
        _, umbral = cv2.threshold(desenfoque, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        elementos_alineados = 0
        total_elementos_significativos = 0
        umbral_tolerancia_pixeles = 15  
        
        for c in contornos:
            x, y, ancho_caja, alto_caja = cv2.boundingRect(c)
            if ancho_caja > (w * 0.05) or alto_caja > (h * 0.05):
                total_elementos_significativos += 1
                
                cerca_x = any(abs(x - lx) <= umbral_tolerancia_pixeles or abs((x + ancho_caja) - lx) <= umbral_tolerancia_pixeles for lx in lineas_referencia_x)
                cerca_y = any(abs(y - ly) <= umbral_tolerancia_pixeles or abs((y + alto_caja) - ly) <= umbral_tolerancia_pixeles for ly in lineas_referencia_y)
                
                # Para la diagonal dinámica sumamos una verificación de esquinas y centros cruzados
                if tipo_grilla == "diagonal_dinamica":
                    cerca_diagonal = abs(x - y) <= umbral_tolerancia_pixeles or abs((x + ancho_caja) - (h - y)) <= umbral_tolerancia_pixeles
                    if cerca_x or cerca_y or cerca_diagonal:
                        elementos_alineados += 1
                else:
                    if cerca_x or cerca_y:
                        elementos_alineados += 1

        if total_elementos_significativos == 0:
            ratio_solidez = 1.0  
        else:
            ratio_solidez = elementos_alineados / total_elementos_significativos
            
        if ratio_solidez >= 0.70:
            veredicto = "Strong"
            nota = f"Estructura muy sólida bajo la grilla de referencia: {tipo_grilla}."
        elif ratio_solidez >= 0.40:
            veredicto = "Fair"
            nota = f"Composición aceptable. Algunos elementos se desvían de la grilla {tipo_grilla}."
        else:
            veredicto = "Weak"
            nota = f"Estructura descuidada. No respeta los ejes de la grilla {tipo_grilla}."

        return {
            "status": "success",
            "veredicto": veredicto,
            "grilla_utilizada": tipo_grilla,
            "porcentaje_efectivo": round(ratio_solidez * 100, 2),
            "descripcion": nota
        }
    except Exception as e:
        return {"error": f"Error en análisis de solidez: {str(e)}"}


def calcular_composicion_experta(imagen_path, categoria="general"):
    """
    Cruza el contraste con la solidez estructural de la
    grilla IDEAL elegida para cada categoría.
    """
    try:
        resultado_contraste = evaluar_contraste_figura_fondo(imagen_path)
        if "error" in resultado_contraste:
            return resultado_contraste
            
        categoria = categoria.lower().strip()
        
        # ASIGNACIÓN DE LA GRILLA IDEAL REAL
        if categoria == "ui_ux":
            tipo_grilla_optima = "modular"
        elif categoria == "logotipos":
            tipo_grilla_optima = "diagonal_dinamica"
        elif categoria == "afiches_posters":
            tipo_grilla_optima = "tercios"
        elif categoria == "tipografia_lettering":
            tipo_grilla_optima = "van_de_graaf"
        elif categoria == "packaging":
            tipo_grilla_optima = "modular"
        else:
            tipo_grilla_optima = "tercios"
            
        # Ejecuta la solidez con la grilla ideal real que corresponde
        resultado_estructura = evaluar_solidez_estructural(imagen_path, tipo_grilla=tipo_grilla_optima)
        if "error" in resultado_estructura:
            return resultado_estructura
            
        v_contraste = resultado_contraste["veredicto"]
        v_estructura = resultado_estructura["veredicto"]
        
        if v_contraste == "Strong" and v_estructura == "Strong":
            veredicto_global = "Strong"
            diagnostico = f"Excelente. Cumple los estándares estructurales de {tipo_grilla_optima} para {categoria}."
        elif v_contraste == "Weak" or v_estructura == "Weak":
            veredicto_global = "Weak"
            diagnostico = f"Deficiente. Falló el contraste o no respeta la grilla {tipo_grilla_optima} requerida para {categoria}."
        else:
            veredicto_global = "Fair"
            diagnostico = f"Aceptable para {categoria}, pero tiene margen de mejora bajo la grilla {tipo_grilla_optima}."
            
        return {
            "status": "success",
            "categoria_analizada": categoria,
            "grilla_utilizada": tipo_grilla_optima,
            "veredicto_maestro": veredicto_global,
            "diagnostico": diagnostico,
            "detalle_contraste": resultado_contraste,
            "detalle_estructura": resultado_estructura
        }
    except Exception as e:
        return {"error": f"Error en composición experta: {str(e)}"}
