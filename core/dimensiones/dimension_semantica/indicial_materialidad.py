from core.categorias.config import consultar_minicpm_v

# Diccionario de Prompts Especializados por Categoría (Enfocados en pistas físicas, técnicas y materialidad)
PROMPTS_INDICIALES = {
    "afiche": (
        "Analizá las pistas físicas de producción e impresión de este afiche. "
        "Buscá indicios de técnicas de impresión gráfica (ej. offset, serigrafía, risografía, flexografía), "
        "texturas del papel, pliegues, gramaje visible, desgastes de tinta o grano de impresión."
    ),
    "logo": (
        "Analizá la construcción técnica y materialidad de esta marca gráfica/logotipo. "
        "Identificá si presenta un acabado vectorial plano nativo, efectos de relieve/emboss, "
        "textura de trama impresa, marcas de renderizado digital o indicios de trazado manual."
    ),
    "ui": (
        "Analizá la materialidad y técnica de producción de esta interfaz de usuario (UI). "
        "Identificá indicios de entorno nativo digital, densidad de píxeles, aliasing/suavizado de fuentes, "
        "artefactos de compresión (JPEG/PNG), estilos skeuomórficos (texturas reales) o flat design puro."
    ),
    "general": (
        "Analizá la técnica de origen, soporte y pistas físicas de producción de esta imagen. "
        "Decodificá la materialidad visible: grano de película analógica, ruido digital, textura de superficie, "
        "sistemas de impresión, artefactos de render/IA o trazos del medio de captura/diseño."
    )
}

def analizar_semiotica_indicial(imagen_path: str, categoria: str = "general") -> dict:
    """
    Subcapa Indicial y Materialidad (Peirce): Pistas físicas de producción, origen técnico, 
    soportes, granos y sistemas de impresión.
    """
    # Selección del prompt base según la categoría
    prompt_base = PROMPTS_INDICIALES.get(categoria.lower(), PROMPTS_INDICIALES["general"])
    
    # Inyección de instrucciones de materialidad y estructura abstracta
    prompt_final = f"""
    {prompt_base}

    REQUISITO SINO QUA NON DE SALIDA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON válido, en idioma español de uso común.
    No incluyas preámbulos, notas ni bloques markdown auxiliares.

    INSTRUCCIÓN SEMÁNTICA INDICIAL (MATERIALIDAD):
    Analiza la imagen identificando sus marcas de producción dividiéndolas estrictamente en tres variables físicas/técnicas:
    1. 'tecnica_origen': Determina si es fotografía (analógica/digital), render 3D, ilustración vectorial, diseño digital o pintura.
    2. 'soporte_y_textura': Identifica el soporte observable (ej. textura de papel, grano de película, ruido ISO, pantalla digital, compresión).
    3. 'pistas_produccion': Identifica evidencias del proceso (ej. trama de impresión offset/serigrafía, iluminación de estudio, trazo vectorial, artefactos digitales).

    Construye cada respuesta de manera directa, objetiva y técnica en una sola línea (Ejemplo de estructura abstracta: 'El indicador X revela el proceso Y sobre el soporte Z'). 
    NO inventes características de impresión si la imagen es 100% digital nativa. No copies palabras del ejemplo de estructura.

    La estructura del JSON debe ser exactamente:
    {{
        "analisis_indicial": {{
            "tecnica_origen": "Descripción técnica de la técnica de origen en una sola línea.",
            "soporte_y_textura": "Descripción del soporte, textura o grano observable en una sola línea.",
            "pistas_produccion": "Descripción de los indicios o marcas del proceso de producción en una sola línea."
        }}
    }}
    """
    
    # Consumo de la infraestructura centralizada
    resultado_vlm = consultar_minicpm_v(imagen_path, prompt_final)
    
    # Propagación de errores
    if "error" in resultado_vlm:
        return resultado_vlm
        
    
    return {
        "status": "success",
        "metrica": "Semiótica Indicial y Materialidad (Peirce)",
        "categoria_evaluada": categoria,
        "resultado": resultado_vlm
    }