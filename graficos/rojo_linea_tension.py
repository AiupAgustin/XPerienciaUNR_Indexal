import base64
import cv2
import io
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from servicios.config import imread_unicode
from graficos.config_heatmaps import COLOR_ROJO_BGR, PARAMS_COMPOSICION

P = PARAMS_COMPOSICION
ACCENT_RED_RGB = (244, 63, 94) # Tono coral/carmesí de la tarjeta de datos

def _is_diagonal(deg: float) -> bool:
    return any(lo <= deg <= hi for lo, hi in P["tension"]["diagonalRanges"])


def merge_segments(raw: list) -> list:
    """Agrupa segmentos casi colineales (respaldo Hough)."""
    t = P["tension"]
    length = lambda s: float(np.hypot(s[2] - s[0], s[3] - s[1]))
    merged: list = []
    for s in sorted(raw, key=length, reverse=True):
        placed = False
        for i, m in enumerate(merged):
            a1 = np.degrees(np.arctan2(-(m[3] - m[1]), m[2] - m[0])) % 180
            a2 = np.degrees(np.arctan2(-(s[3] - s[1]), s[2] - s[0])) % 180
            d = abs(a1 - a2)
            d = 180 - d if d > 90 else d
            if d > t["mergeAngleTol"]:
                continue
            dx, dy = m[2] - m[0], m[3] - m[1]
            L = float(np.hypot(dx, dy)) or 1.0
            dist = lambda px, py: abs(dx * (m[1] - py) - dy * (m[0] - px)) / L
            if dist(s[0], s[1]) > t["mergeDistTol"] or dist(s[2], s[3]) > t["mergeDistTol"]:
                continue
            pts = [(m[0], m[1]), (m[2], m[3]), (s[0], s[1]), (s[2], s[3])]
            best, bd = (pts[0], pts[1]), -1.0
            for a in range(4):
                for b in range(a + 1, 4):
                    dd = float(np.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1]))
                    if dd > bd:
                        bd, best = dd, (pts[a], pts[b])
            merged[i] = (best[0][0], best[0][1], best[1][0], best[1][1])
            placed = True
            break
        if not placed:
            merged.append(s)
    merged.sort(key=length, reverse=True)
    return merged[: t["maxLines"]]


def analizar_lineas_tension(imagen_path: str) -> dict:
    """
    Capa de Tensión Vectorial completa (Algoritmo Indexal: flujos tangenciales + respaldo).
    Devuelve métricas semióticas y overlay en Base64.
    """
    img = imread_unicode(imagen_path)
    if img is None:
        return {"status": "error", "mensaje": f"No se pudo cargar la imagen en {imagen_path}"}

    # Normalización de escala según especificación Indexal (maxSide: 1100)
    max_side = P.get("maxSide", 1100)
    h0, w0 = img.shape[:2]
    scale = min(1.0, max_side / max(h0, w0))
    if scale < 1.0:
        img = cv2.resize(img, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_AREA)

    t = P["tension"]
    h, w = img.shape[:2]
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (0, 0), t["blurSigma"])

    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.hypot(gx, gy)
    hi = max(float(np.quantile(mag, t.get("edgePercentile", 0.94))), 6.0)
    edges = cv2.Canny(gray, max(hi * t.get("edgeLowRatio", 0.28), 2.5), hi)

    min_px = max(10, int(round(max(w, h) * t.get("minComponentRatio", 0.028))))
    n, labels, stats, _ = cv2.connectedComponentsWithStats((edges > 0).astype(np.uint8), 8)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        keep[i] = stats[i, cv2.CC_STAT_AREA] >= min_px
    edges = np.where(keep[labels], 255, 0).astype(np.uint8)

    # 1. Extracción de flujos continuos tangenciales
    F = t["flow"]
    min_len = max(w, h) * F["minLengthRatio"]
    # Desenfoque controlado para retener bordes nítidos de objetos en foco
    sm = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2.0)
    fgx = cv2.Sobel(sm, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    fgy = cv2.Sobel(sm, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    fmag = np.hypot(fgx, fgy)
    positive = fmag[fmag > 0.1]
    flows = []

    if positive.size:
        seed_floor = max(1.4, float(np.quantile(positive, F.get("seedPercentile", 0.84))))
        trace_floor = max(0.7, seed_floor * F.get("traceFloorRatio", 0.48))
        ys, xs = np.where(fmag >= seed_floor)
        seeds = sorted(zip(xs, ys), key=lambda p: fmag[p[1], p[0]], reverse=True)
        occupied = np.zeros((h, w), np.uint8)

        def march(sx, sy, sign):
            points, x, y, prev = [], float(sx), float(sy), None
            for _ in range(F.get("maxSteps", 320)):
                ix, iy = int(round(x)), int(round(y))
                if not (1 <= ix < w - 1 and 1 <= iy < h - 1):
                    break
                if len(points) > 2 and fmag[iy, ix] < trace_floor:
                    break
                tx, ty = -float(fgy[iy, ix]) * sign, float(fgx[iy, ix]) * sign
                norm = float(np.hypot(tx, ty))
                if norm < 1e-3:
                    break
                tx, ty = tx / norm, ty / norm
                if prev is not None:
                    if tx * prev[0] + ty * prev[1] < 0:
                        tx, ty = -tx, -ty
                    dot = np.clip(tx * prev[0] + ty * prev[1], -1, 1)
                    if np.degrees(np.arccos(dot)) > F.get("maxTurn", 38):
                        break
                    tx, ty = tx * 0.6 + prev[0] * 0.4, ty * 0.6 + prev[1] * 0.4
                    norm = float(np.hypot(tx, ty)) or 1.0
                    tx, ty = tx / norm, ty / norm
                points.append((x, y))
                prev = (tx, ty)
                x += tx * F["sampleStep"]
                y += ty * F["sampleStep"]
            return points

        for sx, sy in seeds:
            if len(flows) >= F["maxFlows"]:
                break
            if occupied[sy, sx]:
                continue
            raw = list(reversed(march(sx, sy, -1)))[:-1] + march(sx, sy, 1)
            if len(raw) < 4:
                continue
            poly = cv2.approxPolyDP(np.array(raw, np.float32), F["simplifyTol"], False).reshape(-1, 2)
            length = cv2.arcLength(poly.reshape(-1, 1, 2), False)
            span = float(np.hypot(*(poly[-1] - poly[0])))
            if length < min_len or span < min_len * 0.35:
                continue
            flows.append((poly, length))
            mask = np.zeros((h, w), np.uint8)
            cv2.polylines(mask, [np.rint(np.array(raw)).astype(np.int32)], False, 255, max(1, F.get("suppressionRadius", 10) * 2))
            occupied[mask > 0] = 1
        flows.sort(key=lambda f: f[1], reverse=True)

    # 2. Respaldo para contornos orgánicos
    if not flows:
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in contours:
            if cv2.arcLength(c, False) / 2.0 < min_len:
                continue
            poly = cv2.approxPolyDP(c, F["simplifyTol"], False).reshape(-1, 2)
            if len(poly) >= 2:
                flows.append((poly, cv2.arcLength(c, False) / 2.0))
        flows = sorted(flows, key=lambda f: f[1], reverse=True)[: F["maxFlows"]]

    # 3. Respaldo para geometría recta
    if not flows:
        segs = []
        for ratio in (t["houghThresholdRatio"], *t["fallbackRatios"]):
            lines = cv2.HoughLinesP(
                edges,
                1,
                np.pi / 180,
                threshold=max(18, int(max(w, h) * ratio)),
                minLineLength=int(max(w, h) * t["minLineLengthRatio"] * (1 if ratio > 0.1 else 0.7)),
                maxLineGap=int(max(4, max(w, h) * t["maxLineGapRatio"])),
            )
            raw = [] if lines is None else [tuple(map(int, l[0])) for l in lines]
            segs = merge_segments(raw)
            if len(segs) >= 3:
                break
        flows = [
            (np.array([[x1, y1], [x2, y2]], np.int32), float(np.hypot(x2 - x1, y2 - y1)))
            for x1, y1, x2, y2 in segs
        ]

    # Dibujo de directrices e intersecciones
    capa_roja = np.zeros_like(img)
    info = []
    for poly, _ln in flows:
        x1, y1 = int(poly[0][0]), int(poly[0][1])
        x2, y2 = int(poly[-1][0]), int(poly[-1][1])
        deg = float(np.degrees(np.arctan2(-(y2 - y1), x2 - x1)) % 180)
        diag = _is_diagonal(deg)
        info.append((x1, y1, x2, y2, deg, diag))
        thick = max(3, int(round(t["lineWidth"] + (1 if diag else 0))))
        cv2.polylines(capa_roja, [poly.astype(np.int32)], False, COLOR_ROJO_BGR, thick, cv2.LINE_AA)

    nodes = 0
    for i in range(len(info)):
        for j in range(i + 1, len(info)):
            a, b = info[i], info[j]
            d = abs(a[4] - b[4])
            d = 180 - d if d > 90 else d
            if d < t["minAcuteAngle"]:
                continue
            d1 = (a[2] - a[0], a[3] - a[1])
            d2 = (b[2] - b[0], b[3] - b[1])
            den = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(den) < 1e-6:
                continue
            s = ((b[0] - a[0]) * d2[1] - (b[1] - a[1]) * d2[0]) / den
            x, y = a[0] + s * d1[0], a[1] + s * d1[1]
            inside = lambda sg: (min(sg[0], sg[2]) - 2 <= x <= max(sg[0], sg[2]) + 2
                                 and min(sg[1], sg[3]) - 2 <= y <= max(sg[1], sg[3]) + 2)
            if not (inside(a) and inside(b)) or not (0 <= x <= w and 0 <= y <= h):
                continue
            nodes += 1
            cv2.circle(capa_roja, (int(x), int(y)), int(t["nodeRadius"]), COLOR_ROJO_BGR, -1, cv2.LINE_AA)

    n = max(1, len(info))
    diagonals = sum(1 for item in info if item[5])
    pct_diag = round((diagonals / n) * 100.0, 1)
    pct_orto = round(((len(info) - diagonals) / n) * 100.0, 1)

    sx = sy = 0.0
    for x1, y1, x2, y2, deg, _ in info:
        ln = float(np.hypot(x2 - x1, y2 - y1))
        rad = np.radians(deg * 2)
        sx += ln * np.cos(rad)
        sy += ln * np.sin(rad)
    dominant = round(float(np.degrees(np.arctan2(sy, sx)) / 2 % 180), 1) if info else 0.0

    # Diagnóstico semiótico unificado
    if pct_diag >= 50.0:
        clasificacion = "Tensión Dinámica Alta"
        analisis = f"Predominio de fuerzas diagonales ({pct_diag}%): los vectores oblicuos quiebran la rigidez ortogonal y activan el espacio plástico con tensión y movimiento dirigido."
    elif pct_diag >= 25.0:
        clasificacion = "Tensión Dinámica Moderada"
        analisis = f"Presencia equilibrada de diagonales ({pct_diag}%) y ejes ortogonales ({pct_orto}%): introduce dinamismo y dirección visual manteniendo anclajes de estabilidad estructural."
    else:
        clasificacion = "Composición Estática"
        analisis = f"Predominio de ejes ortogonales ({pct_orto}%): las fuerzas horizontales y verticales asientan la pieza en el plano, priorizando el reposo y la solidez compositiva."

    # Fusión visual oficial Indexal: Screen sobre base al 55%
    alpha = 0.55
    alpha_tension = min(1.0, alpha + 0.35)  # 0.90
    base_atenuada = (img.astype(np.float32) * 0.55) / 255.0
    l_norm = (capa_roja.astype(np.float32) / 255.0) * alpha_tension
    overlay = np.clip((1.0 - (1.0 - base_atenuada) * (1.0 - l_norm)) * 255.0, 0, 255).astype(np.uint8)

    metricas_analiticas = {
        "total_flujos": len(info),
        "pct_diagonales": pct_diag,
        "pct_ortogonales": pct_orto,
        "angulo_dominante": dominant,
        "nodos_cruces": nodes,
        "clasificacion_kandinsky": clasificacion
    }

    # Fusión del mapa de calor con la tarjeta gráfica y canal alfa
    compuesta_img = fusionar_mapa_con_tarjeta(overlay, metricas_analiticas)

    # Reescalar si excede el ancho óptimo de visualización/PDF (reduce ~20MB a ~700KB)
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
        "metrica": "Tensión Vectorial / Líneas de Tensión (Kandinsky)",
        "resultado": {
            "path_imagen_overlay": compuesta_data_uri,
            "metricas_analiticas": metricas_analiticas,
            "descripcion_textual_zonas": {
                "clasificacion": clasificacion,
                "analisis_semiotico": analisis,
                "direccion_dominante": f"{dominant}°",
                "nodos_interseccion": f"{nodes} cruces de tensión"
            }
        }
    }

# -------------------------------------------------------------------------
# RENDERIZADO VISUAL: CHIP / TARJETA LÍNEAS DE TENSIÓN
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


def renderizar_tarjeta_lineas_tension(metricas: dict, scale: float = 3.0) -> Image.Image:
    """
    Dibuja el chip visual de Líneas de Tensión con diseño dark mode,
    proporciones uniformes y acentos carmesí/rojo (#F43F5E).
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
    draw.text((pad_x, y_cursor), "LÍNEAS DE TENSIÓN", fill=(154, 160, 172), font=f_title)
    y_cursor += int(16 * scale)

    # 3. KPI Principal (Número de flujos dominantes)
    total_flujos = metricas.get("total_flujos", 0)
    draw.text((pad_x, y_cursor), str(total_flujos), fill=ACCENT_RED_RGB, font=f_kpi)

    # 4. Bajada / Subtítulo del KPI
    y_cursor += int(29 * scale)
    draw.text((pad_x, y_cursor), "flujos directrices dominantes", fill=(154, 160, 172), font=f_desc)
    y_cursor += int(22 * scale)

    # 5. Barra de progreso (% de diagonales = dinamismo)
    bar_w = w_card - (pad_x * 2)
    bar_h = max(2, int(4 * scale))
    bar_radius = max(1, int(2 * scale))

    draw.rounded_rectangle(
        [(pad_x, y_cursor), (pad_x + bar_w, y_cursor + bar_h)],
        radius=bar_radius,
        fill=(51, 56, 70),
    )

    pct_diag = metricas.get("pct_diagonales", 0.0)
    fill_w = max(bar_radius * 2, int(bar_w * (pct_diag / 100.0)))
    draw.rounded_rectangle(
        [(pad_x, y_cursor), (pad_x + fill_w, y_cursor + bar_h)],
        radius=bar_radius,
        fill=ACCENT_RED_RGB,
    )
    y_cursor += int(13 * scale)

    # 6. Métricas secundarias
    pct_orto = int(round(metricas.get("pct_ortogonales", 0.0)))
    deg_dom = int(round(metricas.get("angulo_dominante", 0.0)))
    nodos = metricas.get("nodos_cruces", 0)

    linea_1 = f"{int(round(pct_diag))}% diagonales  ·  {pct_orto}%"
    linea_2 = "horizontales/verticales"
    linea_3 = f"dirección dominante {deg_dom}°  ·  {nodos} cruces"

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

    tarjeta_img = renderizar_tarjeta_lineas_tension(metricas, scale=scale_dinamico)

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