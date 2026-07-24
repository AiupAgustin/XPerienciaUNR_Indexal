import cv2
import numpy as np

def calcular_sistema_zonas(imagen_path):
    """
    Divide la imagen en las 11 zonas de Ansel Adams (0 al 10)
    y calcula el porcentaje de ocupación de cada zona en la pieza gráfica.
    """
    try:
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": "No se pudo cargar la imagen para el análisis de Ansel Adams"}

        #convierte la imagen a escala de grises    
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        total_pixeles = gris.size
        
        # El ancho de cada zona en una escala de 0-255 es de ~23.18 (cada zona vale casi 23 puntos de brillo)
        ancho_zona = 255 / 11
        distribucion_zonas = {}
        
        for zona in range(11):
            limite_inferior = int(zona * ancho_zona)
            limite_superior = int((zona + 1) * ancho_zona) if zona < 10 else 255
            
            # Contamos cuántos píxeles caen en este rango de luminosidad
            cantidad_pixeles = np.sum((gris >= limite_inferior) & (gris <= limite_superior))
            porcentaje = (cantidad_pixeles / total_pixeles) * 100
            
            # Guardamos con número romano para respetar la nomenclatura clásica
            romanos = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
            distribucion_zonas[f"Zona_{romanos[zona]}"] = round(porcentaje, 2)
            
        return distribucion_zonas
        
    except Exception as e:
        return {"error": f"Error calculando zonas de Ansel Adams: {str(e)}"}

def evaluar_rango_dinamico_adams(distribucion_zonas):
    """
    Aplica la lógica de negocio sobre la distribución de tonos.
    Si la imagen está muy empastada en los extremos (subexpuesta o quemada), penaliza.
    """
    try:
        # Agrupamos para analizar el equilibrio tonal
        extremo_oscuro = distribucion_zonas["Zona_0"] + distribucion_zonas["Zona_I"]
        extremo_claro = distribucion_zonas["Zona_IX"] + distribucion_zonas["Zona_X"]
        tonos_medios = sum(distribucion_zonas[z] for z in ["Zona_IV", "Zona_V", "Zona_VI"])
        
        # Matriz de decisión basada en equilibrio tonal de la pieza
        if extremo_oscuro > 60.0 or extremo_claro > 60.0:
            veredicto = "Weak"
            nota = "Rango dinámico deficiente. La imagen está excesivamente empastada en las sombras o quemada en las luces altas."
        elif tonos_medios >= 20.0:
            veredicto = "Strong"
            nota = "Excelente rango dinámico. Se observa una transición tonal rica y un uso equilibrado del sistema de zonas."
        else:
            veredicto = "Fair"
            nota = "Rango dinámico aceptable, aunque la composición tonal tiende a ser muy contrastada, perdiendo riqueza en tonos medios."
            
        return {
            "status": "success",
            "metrica": "Luminosidad (Ansel Adams)",
            "veredicto": veredicto,
            "descripcion": nota,
            "distribucion_completa": distribucion_zonas
        }
    except Exception as e:
        return {"error": f"Error evaluando rango dinámico: {str(e)}"}
    

def analizar_luminosidad_completa(imagen_path):
    """
    Función clave de la Subcapa: 
    Conecta el sistema de zonas con la evaluación de rango dinámico.
    """
    # Ejecutamos la primera función para escanear los píxeles y armar las zonas
    resultado_zonas = calcular_sistema_zonas(imagen_path)
    
    # Control de errores por si la imagen no cargó
    if "error" in resultado_zonas:
        return resultado_zonas
        
    # Le pasamos la salida de la primera a la segunda función
    reporte_final = evaluar_rango_dinamico_adams(resultado_zonas)
    
    return reporte_final