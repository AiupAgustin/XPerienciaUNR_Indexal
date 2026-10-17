import base64
import cv2
import numpy as np
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from servicios.config import imread_unicode
from graficos.config_heatmaps import PARAMS_COMPOSICION

# Extracción de parámetros desde la fuente única de verdad
C_CFG = PARAMS_COMPOSICION.get("chroma", {})
PALETTE = PARAMS_COMPOSICION.get("palette", {})
MACRO_BLUR_SIGMA = PARAMS_COMPOSICION.get("macroBlurSigma", 3.0)


def hex_to_bgr(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


WARN_BGR = hex_to_bgr(PALETTE.get("warn", "#FEF9C3"))


def _is_monochrome(img: np.ndarray) -> bool:
    """Detecta si la pieza carece de saturación cromática útil."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1].astype(np.float32) / 255.0
    b, g, r = img[:, :, 0].astype(np.int16), img[:, :, 1].astype(np.int16), img[:, :, 2].astype(np.int16)
    spread = np.maximum(np.maximum(b, g), r) - np.minimum(np.minimum(b, g), r)
    colored_pct = float((spread > 12).mean())
    return colored_pct < 0.02 or float(sat.mean()) < 0.04


def _calcular_capa_cromatica(img: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Calcula las bandas topográficas de saturación + temperatura cálida.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hue = hsv[:, :, 0] * 2.0  # Rango 0..360
    sat = hsv[:, :, 1] / 255.0

    # Calidez por matiz: +1 en naranja (45°), -1 en azul (225°)
    temp = np.cos(np.radians(hue - 45.0))
    field = sat * (C_CFG.get("satWeight", 0.6) + C_CFG.get("warmWeight", 0.4) * np.maximum(0.0, temp))
    sm = cv2.GaussianBlur(field, (0, 0), C_CFG.get("blurSigma", 4.0))

    ref = max(float(np.quantile(sm, C_CFG.get("normPercentile", 0.99))), C_CFG.get("minReference", 0.35))
    v = np.clip(sm / ref, 0, 1)

    bands = int(C_CFG.get("bands", 5))
    bi = np.clip((v * bands).astype(np.int32), 0, bands - 1)
    alpha = np.where(v < C_CFG.get("peakThreshold", 0.55), 0.0, np.minimum(1.0, (bi + 1) / bands) * 0.9)

    warn = np.array(WARN_BGR, np.float32)
    out = warn[None, None, :] * alpha[:, :, None]

    # Contornos escalonados entre bandas
    edge = np.zeros(bi.shape, bool)
    edge[:, 1:] |= bi[:, 1:] != bi[:, :-1]
    edge[1:, :] |= bi[1:, :] != bi[:-1, :]
    edge &= bi > 0
    th = max(1, int(round(C_CFG.get("contourWidth", 1.5))))
    if th > 1:
        edge = cv2.dilate(edge.astype(np.uint8), np.ones((th, th), np.uint8)).astype(bool)
    out[edge] = warn

    hot = v >= C_CFG.get("peakThreshold", 0.55)
    total = float(hot.sum())
    ys, xs = np.nonzero(hot)

    if total > 0:
        wgt = v[hot]
        cx = float((xs * wgt).sum() / wgt.sum()) / img.shape[1]
        cy = float((ys * wgt).sum() / wgt.sum()) / img.shape[0]
        warm_pct = float((temp[hot] > 0).sum()) / total * 100.0
    else:
        cx, cy, warm_pct = 0.5, 0.5, 0.0

    chroma_pct = (total / v.size) * 100.0
    cold_pct = 100.0 - warm_pct if total > 0 else 0.0

    metricas = {
        "es_monocromo": False,
        "porcentaje_pico_cromatico": round(chroma_pct, 1),
        "porcentaje_calido": round(warm_pct, 1),
        "porcentaje_frio": round(cold_pct, 1),
        "centro_cromatico": {"x": round(cx * 100.0, 1), "y": round(cy * 100.0, 1)},
    }
    return np.clip(out, 0, 255).astype(np.uint8), metricas


def _calcular_capa_luminancia_monocromo(img: np.ndarray) -> tuple[np.ndarray, dict]:
    """Respaldo para piezas en escala de grises: gradiente por contraste y relieve."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    macro = cv2.GaussianBlur(gray, (0, 0), MACRO_BLUR_SIGMA)
    base = cv2.GaussianBlur(gray, (0, 0), max(6.0, C_CFG.get("blurSigma", 4.0) * 4))
    contrast = np.abs(macro - base) / 255.0

    gx = cv2.Sobel(macro, cv2.CV_32F, 1, 0, ksize=3) / 255.0
    gy = cv2.Sobel(macro, cv2.CV_32F, 0, 1, ksize=3) / 255.0
    texture = np.sqrt(gx * gx + gy * gy) / 4.0

    field = np.clip(contrast * C_CFG.get("contrastWeight", 1.4) + texture * C_CFG.get("textureWeight", 0.3), 0, 1)
    sm = cv2.GaussianBlur(field, (0, 0), C_CFG.get("blurSigma", 4.0))
    ref = max(float(np.quantile(sm, C_CFG.get("normPercentile", 0.99))), 0.06)
    v = np.clip(sm / ref, 0, 1)

    bands = int(C_CFG.get("bands", 5))
    bi = np.clip((v * bands).astype(np.int32), 0, bands - 1)
    alpha = np.where(v < C_CFG.get("peakThreshold", 0.55), 0.0, np.minimum(1.0, (bi + 1) / bands) * 0.9)

    warn = np.array(WARN_BGR, np.float32)
    out = warn[None, None, :] * alpha[:, :, None]

    edge = np.zeros(bi.shape, bool)
    edge[:, 1:] |= bi[:, 1:] != bi[:, :-1]
    edge[1:, :] |= bi[1:, :] != bi[:-1, :]
    edge &= bi > 0
    th = max(1, int(round(C_CFG.get("contourWidth", 1.5))))
    if th > 1:
        edge = cv2.dilate(edge.astype(np.uint8), np.ones((th, th), np.uint8)).astype(bool)
    out[edge] = warn

    hot = v >= C_CFG.get("peakThreshold", 0.55)
    total = float(hot.sum())
    ys, xs = np.nonzero(hot)

    if total > 0:
        wgt = v[hot]
        cx = float((xs * wgt).sum() / wgt.sum()) / img.shape[1]
        cy = float((ys * wgt).sum() / wgt.sum()) / img.shape[0]
        light_pct = float((gray[hot] >= 128).sum()) / total * 100.0
    else:
        cx, cy, light_pct = 0.5, 0.5, 0.0

    metricas = {
        "es_monocromo": True,
        "porcentaje_pico_cromatico": round((total / v.size) * 100.0, 1),
        "porcentaje_calido": round(light_pct, 1),  # Claridad en monocromo
        "porcentaje_frio": round(100.0 - light_pct if total > 0 else 0.0, 1),
        "centro_cromatico": {"x": round(cx * 100.0, 1), "y": round(cy * 100.0, 1)},
    }
    return np.clip(out, 0, 255).astype(np.uint8), metricas


def analizar_gradiente_cromatico(imagen_path: str) -> dict:
    """
    Subcapa Gradiente Cromático / Focos de Color (Indexal Módulo A - #FEF9C3).
    Aísla saturación y temperatura independiente de la luminancia.
    """
    img = imread_unicode(imagen_path)
    if img is None:
        return {"status": "error", "mensaje": f"No se pudo cargar la imagen en {imagen_path}"}

    mono = _is_monochrome(img)
    capa_warn, metricas_chroma = (
        _calcular_capa_luminancia_monocromo(img) if mono else _calcular_capa_cromatica(img)
    )

    # Fusión screen idéntica a la especificación oficial
    alpha = 0.55
    base_atenuada = (img.astype(np.float32) * 0.55) / 255.0
    l_norm = (capa_warn.astype(np.float32) / 255.0) * min(1.0, alpha + 0.2)
    overlay = np.clip((1.0 - (1.0 - base_atenuada) * (1.0 - l_norm)) * 255.0, 0, 255).astype(np.uint8)

    # Fusionamos mapa arriba + tarjeta abajo con escala armónica
    compuesta_img = fusionar_mapa_con_tarjeta(overlay, metricas_chroma)

    # Reescalar si excede el ancho óptimo de visualización/PDF (reduce ~20MB a ~700KB)
    max_ancho = 900
    if compuesta_img.width > max_ancho:
        nuevo_alto = int(compuesta_img.height * (max_ancho / compuesta_img.width))
        compuesta_salida = compuesta_img.resize((max_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    else:
        compuesta_salida = compuesta_img

    # 3. Codificamos la imagen compuesta a Base64 URI
    buf_compuesta = io.BytesIO()
    compuesta_salida.save(buf_compuesta, format="PNG", optimize=True)
    compuesta_data_uri = f"data:image/png;base64,{base64.b64encode(buf_compuesta.getvalue()).decode('utf-8')}"

    return {
        "status": "success",
        "metrica": "Gradiente Cromático / Focos de color (Indexal)",
        "resultado": {
            "path_imagen_overlay": compuesta_data_uri,
            "metricas_analiticas": metricas_chroma,
            "descripcion_textual": {
                "picos_saturacion": f"{metricas_chroma['porcentaje_pico_cromatico']}% de la pieza son picos de saturación y temperatura",
                "relacion_temperatura": f"{int(round(metricas_chroma['porcentaje_calido']))}% cálido · {int(round(metricas_chroma['porcentaje_frio']))}% frío",
                "centro_cromatico": f"x {int(round(metricas_chroma['centro_cromatico']['x']))}% · y {int(round(metricas_chroma['centro_cromatico']['y']))}%",
            }
        }
    }

# -------------------------------------------------------------------------
# RENDERIZADO VISUAL: CHIP / TARJETA INFORMATIVA GRADIENTE CROMÁTICO
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


def _cargar_fuentes_tarjeta(scale: int):
    """Carga Space Grotesk en sus distintos pesos y tamaños."""
    tam_title = int(11 * scale)
    tam_kpi = int(24 * scale)
    tam_desc = int(11 * scale)
    tam_mono = int(10 * scale)

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

    # Fallbacks defensivos
    f_title = f_title or ImageFont.load_default()
    f_kpi = f_kpi or ImageFont.load_default()
    f_desc = f_desc or ImageFont.load_default()
    f_mono = f_mono or ImageFont.load_default()

    return f_title, f_kpi, f_desc, f_mono


def renderizar_tarjeta_gradiente_cromatico(metricas: dict, scale: float = 3.0) -> Image.Image:
    """
    Dibuja el chip visual de Gradiente Cromático con estilo dark mode,
    escalando proporcionalmente según el factor de escala dinámico.
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
    draw.text((pad_x, y_cursor), "GRADIENTE CROMÁTICO", fill=(154, 160, 172), font=f_title)
    y_cursor += int(16 * scale)

    # 3. KPI Principal (amarillo cálido #FEF08A)
    pct_pico = metricas.get("porcentaje_pico_cromatico", 0.0)
    kpi_str = f"{pct_pico}%"
    draw.text((pad_x, y_cursor), kpi_str, fill=(254, 240, 138), font=f_kpi)

    # 4. Bajada / Subtítulo del KPI en 2 líneas
    y_cursor += int(29 * scale)
    draw.text((pad_x, y_cursor), "de la pieza son picos de", fill=(154, 160, 172), font=f_desc)
    y_cursor += int(13 * scale)
    draw.text((pad_x, y_cursor), "saturación y temperatura", fill=(154, 160, 172), font=f_desc)
    y_cursor += int(22 * scale)

    # 5. Barra de progreso
    bar_w = w_card - (pad_x * 2)
    bar_h = max(2, int(4 * scale))
    bar_radius = max(1, int(2 * scale))

    # Fondo barra
    draw.rounded_rectangle(
        [(pad_x, y_cursor), (pad_x + bar_w, y_cursor + bar_h)],
        radius=bar_radius,
        fill=(51, 56, 70),
    )
    # Relleno activo
    fill_w = max(bar_radius * 2, int(bar_w * (pct_pico / 100.0)))
    draw.rounded_rectangle(
        [(pad_x, y_cursor), (pad_x + fill_w, y_cursor + bar_h)],
        radius=bar_radius,
        fill=(254, 240, 138),
    )
    y_cursor += int(13 * scale)

    # 6. Métricas secundarias
    calido = int(round(metricas.get("porcentaje_calido", 0.0)))
    frio = int(round(metricas.get("porcentaje_frio", 0.0)))
    cc = metricas.get("centro_cromatico", {"x": 50, "y": 50})
    cx = int(round(cc.get("x", 50)))
    cy = int(round(cc.get("y", 50)))

    linea_1 = f"{calido}% cálido  ·  {frio}% frío"
    linea_2 = f"centro cromático en x {cx}% · y {cy}%"

    draw.text((pad_x, y_cursor), linea_1, fill=(138, 143, 156), font=f_mono)
    y_cursor += int(12 * scale)
    draw.text((pad_x, y_cursor), linea_2, fill=(138, 143, 156), font=f_mono)

    return img

def fusionar_mapa_con_tarjeta(mapa_bgr: np.ndarray, metricas: dict) -> Image.Image:
    """
    Concatena verticalmente el mapa de calor arriba y su tarjeta informativa debajo.
    Calcula dinámicamente la escala de la tarjeta para que mantenga proporciones
    perfectas sin importar la orientación (horizontal vs vertical) o resolución de la foto.
    """
    mapa_rgb = cv2.cvtColor(mapa_bgr, cv2.COLOR_BGR2RGB)
    mapa_pil = Image.fromarray(mapa_rgb)

    ancho_mapa = mapa_pil.width
    alto_mapa = mapa_pil.height
    aspect_ratio = ancho_mapa / float(alto_mapa)

    # Proporción armónica de ancho según orientación:
    # - Horizontal (aspect > 1.15): tarjeta al 60% del ancho del mapa
    # - Cuadrada / Vertical: tarjeta al 86% del ancho del mapa
    if aspect_ratio > 1.15:
        pct_ancho = 0.60
    elif aspect_ratio > 0.85:
        pct_ancho = 0.75
    else:
        pct_ancho = 0.88

    ancho_tarjeta_target = int(ancho_mapa * pct_ancho)
    
    # 210px es el ancho base de diseño de la tarjeta
    scale_dinamico = max(1.0, ancho_tarjeta_target / 210.0)

    # Renderizamos la tarjeta nativa a su escala matemática exacta (sin pixelar)
    tarjeta_img = renderizar_tarjeta_gradiente_cromatico(metricas, scale=scale_dinamico)

    w_card = tarjeta_img.width
    h_card = tarjeta_img.height

    gap = int(12 * scale_dinamico)
    pad_bottom = int(14 * scale_dinamico)

    alto_total = alto_mapa + gap + h_card + pad_bottom

    # Creamos el lienzo transparente
    bloque = Image.new("RGBA", (ancho_mapa, alto_total), (0, 0, 0, 0))
    bloque.paste(mapa_pil, (0, 0))

    # Pegamos la tarjeta siempre centrada
    x_offset = (ancho_mapa - w_card) // 2
    bloque.paste(tarjeta_img, (x_offset, alto_mapa + gap))

    return bloque