# Agrupa los resultados de los análisis según los checkboxes
from core.categorias.cat0_analisis_semiotico import MAPA_CHECKBOXES_CAT0


# Mapeo entre los identificadores del frontend y los IDs del backend
MAPA_CATEGORIA_A_ID = {
    "semiotico": 0,
    "logotipo": 1,
    "afiche": 2,
    "packaging": 2,
    "tipografia": 3,
    "ui_ux": 5,
}

# Diccionario que agrupa los mapas de funciones por cada categoría
MAPAS_POR_CATEGORIA = {
    0: MAPA_CHECKBOXES_CAT0,
    # A medida que agreguemos las demás categorías, las agregamos acá:
    # 1: MAPA_CHECKBOXES_CAT1,
    # 2: MAPA_CHECKBOXES_CAT2,
    # 3: MAPA_CHECKBOXES_CAT3,
    # 4: MAPA_CHECKBOXES_CAT4,
    # 5: MAPA_CHECKBOXES_CAT5,
}

def compilar_datos_reporte(
    imagen_path: str, 
    mapa_global: dict = None, 
    lista_cb_seleccionados: list = None, 
    categoria_id: int = 0
) -> dict:
    """Ejecuta los checkboxes seleccionados y consolida el Master JSON."""
    
    # 1. Si no se pasa un mapa_global explícito, usamos el de la categoría correspondiente
    if mapa_global is None or len(mapa_global) == 0:
        mapa_global = MAPAS_POR_CATEGORIA.get(categoria_id, MAPA_CHECKBOXES_CAT0)

    if lista_cb_seleccionados is None:
        lista_cb_seleccionados = []

    # 2. Mapeo de títulos por ID de categoría
    titulos_por_categoria = {
        0: "Análisis Semiótico",
        1: "Análisis Branding y Identidad de Marca",
        2: "Análisis Publicitario",
        3: "Análisis Editorial",
        4: "Análisis de Ilustración / Arte",
        5: "Análisis UI/UX"
    }

    bloques_procesados = []

    # 3. Ejecución de los módulos seleccionados
    for cb_id in lista_cb_seleccionados:
        # Buscamos por el ID directo (ej: "cb1_composicion_visual")
        # o normalizando sin el prefijo (ej: "composicion_visual")
        func_ejecutora = None
        
        if cb_id in mapa_global:
            func_ejecutora = mapa_global[cb_id]
        else:
            # Búsqueda flexible por si en frontend viene sin 'cbX_'
            for k, v in mapa_global.items():
                if k == cb_id or k.endswith(f"_{cb_id}") or cb_id.endswith(f"_{k}"):
                    func_ejecutora = v
                    break

        if func_ejecutora:
            try:
                # Ejecutamos la función de la categoría pasándole la imagen
                res = func_ejecutora(imagen_path)
                bloques_procesados.append(res)
            except Exception as e:
                bloques_procesados.append({
                    "status": "error",
                    "checkbox": cb_id,
                    "error_msg": str(e)
                })

    return {
        "metadata": {
            "imagen_path": imagen_path,
            "categoria_id": categoria_id,
            "titulo_reporte": titulos_por_categoria.get(categoria_id, "Auditoría de Diseño Visual"),
            "total_bloques": len(bloques_procesados)
        },
        "bloques": bloques_procesados
    }