import base64
import cv2
import numpy as np
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from servicios.config import imread_unicode
from graficos.config_heatmaps import COLOR_AZUL_BGR, PARAMS_COMPOSICION

W_CFG = PARAMS_COMPOSICION.get("peso", PARAMS_COMPOSICION.get("weight", {}))

# Azul Indexal oficial (#0057FF)
ACCENT_BLUE_RGB = (0, 87, 255)


def _calcular_capa_peso(img: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Segmenta las masas de peso visual por umbral adaptativo Otsu
    e invierte el fondo perimetral, idéntico a la versión web oficial.
    """
    h, w = img.shape[:2]
    cx_img, cy_img = w / 2.0, h / 2.0
    half_diag = float(np.hypot(cx_img, cy_img))

    # Parámetros desde config_heatmaps (P["weight"])
    blur_sigma = W_CFG.get("blurSigma", 4.5)
    min_area_ratio = W_CFG.get("minAreaRatio", 0.012)
    max_masses = int(W_CFG.get("maxMasses", 8))
    lw = max(2, int(round(W_CFG.get("lineWidth", 2.5))))

    # 1. Mapa de nitidez focal estricto
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    suave_fino = cv2.GaussianBlur(gray, (0, 0), sigmaX=blur_sigma)
    suave_macro = cv2.GaussianBlur(gray, (0, 0), sigmaX=blur_sigma * 5.0)
    saliencia = cv2.absdiff(suave_fino, suave_macro)

    # Gradiente Sobel normalizado
    gx = cv2.Sobel(suave_fino, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(suave_fino, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.hypot(gx, gy)
    mag_norm = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    saliencia_norm = cv2.normalize(saliencia, None, 0, 255, cv2.NORM_MINMAX)

    # 2. Emisión y brillo relativo respecto al fondo general (sol macizo)
    med_brillo = float(np.mean(gray))
    std_brillo = float(np.std(gray))
    brillo_destacado = np.maximum(0.0, gray.astype(np.float32) - (med_brillo + 0.85 * std_brillo))

    # Filtro estricto de fondo desenfocado difuso (paredes lisas de estudio)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1].astype(np.float32) / 255.0

    # Pared difusa: muy baja saturación y nula alta frecuencia
    es_fondo_difuso = (sat < 0.25) & (mag_norm < 40)

    # Extinción de brillo en paredes lisas para que no entren por luz_norm
    brillo_destacado_limpio = brillo_destacado.copy()
    brillo_destacado_limpio[es_fondo_difuso] = 0.0

    if np.max(brillo_destacado_limpio) > 0:
        luz_norm = cv2.normalize(brillo_destacado_limpio, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    else:
        luz_norm = np.zeros_like(gray)

    # Atenuación de saliencia en fondo plano
    saliencia_filtrada = saliencia_norm.copy()
    saliencia_filtrada[es_fondo_difuso] = 0

    # Combinación base
    mapa_base = cv2.max(saliencia_filtrada, luz_norm)

    # Integración de textura y foco
    textura_foco = cv2.min(mag_norm, saliencia_filtrada)
    mapa_final = cv2.max(mapa_base, (textura_foco.astype(np.float32) * 0.90).astype(np.uint8))

    # Binarización Otsu general (1.05 preserva instrumentos delgados como el saxo)
    thr_otsu, _ = cv2.threshold(mapa_final, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, binary = cv2.threshold(mapa_final, int(thr_otsu * 1.05), 255, cv2.THRESH_BINARY)

    # Morfología: cierre para unir estructuras continuas y apertura suave
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k_close)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k_open)

    # 3. Contornos y momentos de inercia
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = max(64, int(w * h * min_area_ratio))
    total_frame_area = float(w * h)

    masses_raw = []
    for c in contours:
        m = cv2.moments(c)
        area = float(m["m00"])
        if area < min_area:
            continue

        # Descartar parches pegados al marco
        x_box, y_box, w_box, h_box = cv2.boundingRect(c)
        toca_borde = (x_box <= 3 or y_box <= 3 or (x_box + w_box) >= w - 4 or (y_box + h_box) >= h - 4)
        if toca_borde and (area / total_frame_area) < 0.12:
            continue

        cx = m["m10"] / area
        cy = m["m01"] / area
        torque = area * (float(np.hypot(cx - cx_img, cy - cy_img)) / half_diag)
        masses_raw.append({"c": c, "area": area, "cx": cx, "cy": cy, "torque": torque})

    # 4. Poda por Dominancia y Escala:
    if masses_raw:
        masas_ordenadas = sorted(masses_raw, key=lambda d: d["area"], reverse=True)
        area_maxima = masas_ordenadas[0]["area"]
        max_t = max(d["torque"] for d in masses_raw)

        # Para calificar como masa activa, un elemento secundario debe tener al menos
        # el 55% del área de la masa dominante y un torque relevante (>= 45%).
        # Esto descarta de inmediato los carretes de hilo y elementos de utilería periféricos.
        masses = [
            d for d in masses_raw
            if d["area"] >= area_maxima * 0.55 and d["torque"] >= max_t * 0.45
        ][:max_masses]

        if not any(d["area"] == area_maxima for d in masses):
            masses.append(masas_ordenadas[0])

        masses.sort(key=lambda d: d["torque"], reverse=True)
    else:
        masses = []

    max_torque = max((d["torque"] for d in masses), default=1.0) or 1.0

    # 5. Renderizado translúcido
    layer = np.zeros_like(img)
    for d in masses:
        rel = d["torque"] / max_torque
        fill = np.zeros_like(img)
        cv2.drawContours(fill, [d["c"]], -1, COLOR_AZUL_BGR, -1)
        layer = np.maximum(layer, (fill.astype(np.float32) * (0.14 + 0.5 * rel)).astype(np.uint8))

    # 6. Líneas conectoras y nodos de masa
    for d in masses:
        rel = d["torque"] / max_torque
        p = (int(round(d["cx"])), int(round(d["cy"])))
        cv2.line(
            layer,
            (int(round(cx_img)), int(round(cy_img))),
            p,
            COLOR_AZUL_BGR,
            max(1, int(round(lw * (0.5 + rel)))),
            cv2.LINE_AA
        )
        cv2.circle(layer, p, max(4, int(np.sqrt(d["area"]) * 0.09)), COLOR_AZUL_BGR, -1, cv2.LINE_AA)

    # 7. Centro de gravedad global (mira)
    total_area = sum(d["area"] for d in masses)
    if total_area > 0:
        gx = sum(d["area"] * d["cx"] for d in masses) / total_area
        gy = sum(d["area"] * d["cy"] for d in masses) / total_area
    else:
        gx, gy = cx_img, cy_img

    arm = int(max(20, min(w, h) * 0.05))
    gxi, gyi = int(round(gx)), int(round(gy))
    cv2.line(layer, (gxi - arm, gyi), (gxi + arm, gyi), COLOR_AZUL_BGR, lw, cv2.LINE_AA)
    cv2.line(layer, (gxi, gyi - arm), (gxi, gyi + arm), COLOR_AZUL_BGR, lw, cv2.LINE_AA)
    cv2.circle(layer, (gxi, gyi), int(arm * 0.55), COLOR_AZUL_BGR, lw, cv2.LINE_AA)
    cv2.circle(layer, (int(round(cx_img)), int(round(cy_img))), int(arm * 0.3), COLOR_AZUL_BGR, 1, cv2.LINE_AA)

    heaviest_pct = round((masas_ordenadas[0]["area"] / (w * h) * 100.0), 1) if masses_raw else 0.0

    metricas = {
        "total_masas": len(masses),
        "porcentaje_area_ocupada": round((total_area / (w * h)) * 100.0, 1),
        "masa_mas_pesada_pct": heaviest_pct,
        "desbalance_radial_pct": round(min(100.0, float(np.hypot(gx - cx_img, gy - cy_img)) / half_diag * 100.0), 1),
        "centro_gravedad": {"x": round(gx / w, 3), "y": round(gy / h, 3)},
        "posicion_px": {"x": gxi, "y": gyi}
    }

    return layer, metricas


def analizar_peso_visual(imagen_path: str) -> dict:
    """
    Subcapa Peso Visual / Torque compositivo (Indexal Módulo A - #0057FF).
    Integra momentos de inercia 2D con simetría morfométrica existente.
    """
    # Import local diferido para evitar importación circular con cat0
    from core.categorias.cat0_analisis_semiotico import _calcular_simetria_central

    img = imread_unicode(imagen_path)
    if img is None:
        return {"status": "error", "mensaje": f"No se pudo cargar la imagen en {imagen_path}"}

    res_simetria = _calcular_simetria_central(imagen_path)
    if isinstance(res_simetria, dict) and "error" in res_simetria:
        return {"status": "error", "mensaje": res_simetria["error"]}

    capa_azul, metricas_peso = _calcular_capa_peso(img)

    alpha = 0.55
    base_atenuada = (img.astype(np.float32) * 0.55) / 255.0
    l_norm = (capa_azul.astype(np.float32) / 255.0) * min(1.0, alpha + 0.4)
    overlay = np.clip((1.0 - (1.0 - base_atenuada) * (1.0 - l_norm)) * 255.0, 0, 255).astype(np.uint8)

    # Fusión del mapa de calor con la tarjeta gráfica y fondo transparente
    compuesta_img = fusionar_mapa_con_tarjeta(overlay, metricas_peso)

    # Reescalar si supera el ancho útil de renderizado (reduce de ~20MB a ~700KB)
    max_ancho = 900
    if compuesta_img.width > max_ancho:
        nuevo_alto = int(compuesta_img.height * (max_ancho / compuesta_img.width))
        compuesta_salida = compuesta_img.resize((max_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    else:
        compuesta_salida = compuesta_img

    buf_compuesta = io.BytesIO()
    compuesta_salida.save(buf_compuesta, format="PNG", optimize=True)
    compuesta_data_uri = f"data:image/png;base64,{base64.b64encode(buf_compuesta.getvalue()).decode('utf-8')}"

    return {
        "status": "success",
        "metrica": "Peso Visual / Torque e Inercia (Indexal)",
        "resultado": {
            "path_imagen_overlay": compuesta_data_uri,
            "metricas_analiticas": {
                **metricas_peso,
                "indice_simetria": res_simetria.get("indice_simetria"),
                "desviacion_centro_masa_1d": res_simetria.get("desviacion_centro_masa"),
                "clasificacion_simetria": res_simetria.get("estado")
            },
            "descripcion_textual": {
                "clasificacion_balance": res_simetria.get("estado", ""),
                "desbalance_radial": f"{metricas_peso['desbalance_radial_pct']}% respecto al centro",
                "centro_gravedad": f"({metricas_peso['centro_gravedad']['x']}, {metricas_peso['centro_gravedad']['y']})",
                "masas_activas": metricas_peso["total_masas"]
            }
        }
    }

# -------------------------------------------------------------------------
# RENDERIZADO VISUAL: CHIP / TARJETA PESO VISUAL
# -------------------------------------------------------------------------

_current = Path(__file__).resolve().parent
CARPETA_FUENTES = None
for _ in range(4):
    candidata = _current / "assets" / "fonts"
    if candidata.exists():
        CARPETA_FUENTES = candidata
        break
    _current = _current.parent

if not CARPETA_FUENTES:
    CARPETA_FUENTES = Path("assets/fonts").resolve()


def _cargar_fuentes_tarjeta(scale: float):
    tam_title = max(8, int(11 * scale))
    tam_kpi = max(14, int(24 * scale))
    tam_desc = max(8, int(11 * scale))
    tam_mono = max(7, int(9.5 * scale))

    ruta_bold = CARPETA_FUENTES / "SpaceGrotesk-Bold.ttf"
    ruta_reg = CARPETA_FUENTES / "SpaceGrotesk-Regular.ttf"

    f_title, f_kpi, f_desc, f_mono = None, None, None, None
    try:
        if ruta_bold.exists():
            f_title = ImageFont.truetype(str(ruta_bold), tam_title)
            f_kpi = ImageFont.truetype(str(ruta_bold), tam_kpi)
        if ruta_reg.exists():
            f_desc = ImageFont.truetype(str(ruta_reg), tam_desc)
            f_mono = ImageFont.truetype(str(ruta_reg), tam_mono)
    except Exception:
        pass

    f_title = f_title or ImageFont.load_default()
    f_kpi = f_kpi or ImageFont.load_default()
    f_desc = f_desc or ImageFont.load_default()
    f_mono = f_mono or ImageFont.load_default()

    return f_title, f_kpi, f_desc, f_mono


def renderizar_tarjeta_peso_visual(metricas: dict, scale: float = 3.0) -> Image.Image:
    """
    Dibuja el chip visual de Peso Visual / Torque con diseño dark mode,
    proporciones armónicas y acento azul eléctrico (#0057FF).
    """
    w_card = int(210 * scale)
    h_card = int(162 * scale)
    pad_x = int(16 * scale)
    pad_y = int(13 * scale)

    img = Image.new("RGBA", (w_card, h_card), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Contenedor Dark (#13151B, borde #232733)
    radius = max(4, int(10 * scale))
    draw.rounded_rectangle(
        [(0, 0), (w_card - 1, h_card - 1)],
        radius=radius,
        fill=(19, 21, 27),
        outline=(35, 39, 51),
        width=max(1, int(1 * scale)),
    )

    f_title, f_kpi, f_desc, f_mono = _cargar_fuentes_tarjeta(scale)

    # 2. Título de categoría
    y_cursor = pad_y
    draw.text((pad_x, y_cursor), "PESO VISUAL", fill=(154, 160, 172), font=f_title)
    y_cursor += int(16 * scale)

    # 3. KPI Principal (% de desequilibrio respecto al centro)
    desbalance = metricas.get("desbalance_radial_pct", 0.0)
    draw.text((pad_x, y_cursor), f"{desbalance}%", fill=ACCENT_BLUE_RGB, font=f_kpi)

    # 4. Bajada / Subtítulo del KPI en 2 líneas
    y_cursor += int(29 * scale)
    draw.text((pad_x, y_cursor), "de desequilibrio respecto del centro", fill=(154, 160, 172), font=f_desc)
    y_cursor += int(13 * scale)
    draw.text((pad_x, y_cursor), "de la pieza", fill=(154, 160, 172), font=f_desc)
    y_cursor += int(22 * scale)

    # 5. Barra de progreso (% de desequilibrio)
    bar_w = w_card - (pad_x * 2)
    bar_h = max(2, int(4 * scale))
    bar_radius = max(1, int(2 * scale))

    draw.rounded_rectangle(
        [(pad_x, y_cursor), (pad_x + bar_w, y_cursor + bar_h)],
        radius=bar_radius,
        fill=(51, 56, 70),
    )

    fill_w = max(bar_radius * 2, int(bar_w * (desbalance / 100.0)))
    draw.rounded_rectangle(
        [(pad_x, y_cursor), (pad_x + fill_w, y_cursor + bar_h)],
        radius=bar_radius,
        fill=ACCENT_BLUE_RGB,
    )
    y_cursor += int(13 * scale)

    # 6. Métricas secundarias (3 líneas)
    n_masas = metricas.get("total_masas", 0)
    area_tot = metricas.get("porcentaje_area_ocupada", 0.0)
    cg = metricas.get("centro_gravedad", {"x": 0.5, "y": 0.5})
    cg_x = int(round(cg.get("x", 0.5) * 100))
    cg_y = int(round(cg.get("y", 0.5) * 100))
    heaviest = metricas.get("masa_mas_pesada_pct", 0.0)

    texto_masas = "masa" if n_masas == 1 else "masas"
    linea_1 = f"{n_masas} {texto_masas}  ·  {area_tot}% de la pieza"
    linea_2 = f"centro de gravedad en x {cg_x}% · y {cg_y}%"
    linea_3 = f"masa más pesada: {heaviest}% de la pieza"

    draw.text((pad_x, y_cursor), linea_1, fill=(138, 143, 156), font=f_mono)
    y_cursor += int(11 * scale)
    draw.text((pad_x, y_cursor), linea_2, fill=(138, 143, 156), font=f_mono)
    y_cursor += int(11 * scale)
    draw.text((pad_x, y_cursor), linea_3, fill=(138, 143, 156), font=f_mono)

    return img


def fusionar_mapa_con_tarjeta(mapa_bgr: np.ndarray, metricas: dict) -> Image.Image:
    """
    Concatena verticalmente el mapa de calor arriba y su tarjeta informativa debajo.
    Aplica escala armónica según orientación (vertical/apaisada) y fondo transparente.
    """
    mapa_rgb = cv2.cvtColor(mapa_bgr, cv2.COLOR_BGR2RGB)
    mapa_pil = Image.fromarray(mapa_rgb)

    ancho_mapa = mapa_pil.width
    alto_mapa = mapa_pil.height
    aspect_ratio = ancho_mapa / float(alto_mapa)

    if aspect_ratio > 1.15:
        pct_ancho = 0.60
    elif aspect_ratio > 0.85:
        pct_ancho = 0.75
    else:
        pct_ancho = 0.88

    ancho_tarjeta_target = int(ancho_mapa * pct_ancho)
    scale_dinamico = max(1.0, ancho_tarjeta_target / 210.0)

    tarjeta_img = renderizar_tarjeta_peso_visual(metricas, scale=scale_dinamico)

    w_card = tarjeta_img.width
    h_card = tarjeta_img.height

    gap = int(12 * scale_dinamico)
    pad_bottom = int(14 * scale_dinamico)

    alto_total = alto_mapa + gap + h_card + pad_bottom

    bloque = Image.new("RGBA", (ancho_mapa, alto_total), (0, 0, 0, 0))
    bloque.paste(mapa_pil, (0, 0))

    x_offset = (ancho_mapa - w_card) // 2
    bloque.paste(tarjeta_img, (x_offset, alto_mapa + gap))

    return bloque