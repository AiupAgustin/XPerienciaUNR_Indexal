# Agrupa los resultados de los análisis según los checkboxes

def compilar_datos_reporte(
    imagen_path: str, 
    mapa_global: dict, 
    lista_cb_seleccionados: list, 
    categoria_id: int = 0
) -> dict:
    """Ejecuta los checkboxes seleccionados y consolida el Master JSON."""
    
    # Mapeo de títulos por ID de categoría
    titulos_por_categoria = {
        0: "Análisis Semiótico",
        1: "Análisis Branding y Identidad de Marca",
        2: "Análisis Publicitario",
        3: "Análisis Editorial",
        4: "Análisis de Ilustración / Arte",
        5: "Análisis UI/UX"
    }

    bloques_procesados = []

    for cb_id in lista_cb_seleccionados:
        if cb_id in mapa_global:
            func_ejecutora = mapa_global[cb_id]
            res = func_ejecutora(imagen_path)
            bloques_procesados.append(res)

    return {
        "metadata": {
            "imagen_path": imagen_path,
            "categoria_id": categoria_id,
            "titulo_reporte": titulos_por_categoria.get(categoria_id, "Auditoría de Diseño Visual"),
            "total_bloques": len(bloques_procesados)
        },
        "bloques": bloques_procesados
    }