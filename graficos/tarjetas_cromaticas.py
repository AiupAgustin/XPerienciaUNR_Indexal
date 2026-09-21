"""
graficos/tarjetas_cromaticas.py
Renderizado 1:1 con las especificaciones exactas del inspector de Figma:
- Espaciados (gaps): 8px estrictos entre cada elemento.
- Título rol: 12px Bold, color #0B1020, caja 15px.
- Fila HEX: 11px Regular, color #444748, caja 14px.
- Porcentaje: 11px Bold, color #0057FF, alineado con HEX.
- Barra progreso: alto 4px, radio cápsula 2px, gap 8px.
"""

import io
import base64
from PIL import Image, ImageDraw, ImageFont


def _hex_to_rgb(hex_str: str):
    hex_clean = hex_str.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join([c * 2 for c in hex_clean])
    return tuple(int(hex_clean[i : i + 2], 16) for i in (0, 2, 4))


def _cargar_fuentes_sistema(scale: int):
    """Carga fuentes sans-serif nítidas del sistema (Windows/Linux) con pesos diferenciados."""
    f_bold = None
    f_reg = None

    candidatas_bold = [
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "arialbd.ttf",
    ]
    candidatas_reg = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf",
    ]

    # Fuente Bold (12px base)
    for ruta in candidatas_bold:
        try:
            f_bold = ImageFont.truetype(ruta, 12 * scale)
            break
        except Exception:
            continue
    if not f_bold:
        f_bold = ImageFont.load_default()

    # Fuente Regular (11px base según Figma)
    for ruta in candidatas_reg:
        try:
            f_reg = ImageFont.truetype(ruta, 11 * scale)
            break
        except Exception:
            continue
    if not f_reg:
        f_reg = ImageFont.load_default()

    return f_bold, f_reg


def _dibujar_tarjeta(draw, x_offset, y_offset, w, h, scale, rol, hex_val, pct):
    pad = 12 * scale
    gap = 8 * scale  # 8px exactos entre elementos según captura de Figma

    # 1. Contenedor de la tarjeta (182 x 163 px, borde #C4C6CF, radius 8px, fondo blanco)
    draw.rounded_rectangle(
        [(x_offset, y_offset), (x_offset + w - 1, y_offset + h - 1)],
        radius=8 * scale,
        fill=(255, 255, 255),
        outline=(196, 198, 207),  # #C4C6CF
        width=1 * scale,
    )

    # 2. Bloque de color (Swatch: 156 x 74 px, radius 8px)
    swatch_x1 = x_offset + pad
    swatch_y1 = y_offset + pad
    swatch_x2 = x_offset + w - pad
    swatch_h = 74 * scale
    swatch_y2 = swatch_y1 + swatch_h
    color_rgb = _hex_to_rgb(hex_val)

    draw.rounded_rectangle(
        [(swatch_x1, swatch_y1), (swatch_x2, swatch_y2)],
        radius=8 * scale,
        fill=color_rgb,
    )

    # 3. Tipografías
    font_bold, font_reg = _cargar_fuentes_sistema(scale)

    # 4. Título del Rol (Figma: #0B1020, 12px, altura de caja: 15px)
    caja_rol_h = 15 * scale
    y_caja_rol = swatch_y2 + gap
    draw.text((swatch_x1, y_caja_rol), rol, fill=(11, 16, 32), font=font_bold)  # #0B1020

    # 5. Fila: Código HEX y Porcentaje (Figma: gap 8px tras la caja del rol, altura de caja: 14px)
    caja_hex_h = 14 * scale
    y_caja_hex = y_caja_rol + caja_rol_h + gap

    # Código HEX: color #444748 (según Figma), 11px Regular
    draw.text((swatch_x1, y_caja_hex), hex_val.upper(), fill=(68, 71, 72), font=font_reg)

    # Porcentaje: color #0057FF, 11px Bold, alineado a la derecha
    pct_str = f"{pct}%"
    bbox_pct = draw.textbbox((0, 0), pct_str, font=font_bold)
    w_pct = bbox_pct[2] - bbox_pct[0]
    draw.text((swatch_x2 - w_pct, y_caja_hex), pct_str, fill=(0, 87, 255), font=font_bold)

    # 6. Barra de progreso (Figma: gap 8px tras la caja del texto)
    bar_y1 = y_caja_hex + caja_hex_h + gap
    bar_h = 4 * scale
    bar_y2 = int(bar_y1 + bar_h)
    bar_radius = int(2 * scale)

    # Base gris tenue
    draw.rounded_rectangle(
        [(swatch_x1, bar_y1), (swatch_x2, bar_y2)],
        radius=bar_radius,
        fill=(241, 245, 249),
    )

    # Relleno de progreso azul (#0057FF)
    ancho_util = swatch_x2 - swatch_x1
    w_progreso = max(bar_radius * 2, int(ancho_util * (pct / 100.0)))
    draw.rounded_rectangle(
        [(swatch_x1, bar_y1), (swatch_x1 + w_progreso, bar_y2)],
        radius=bar_radius,
        fill=(0, 87, 255),
    )


def renderizar_tarjetas_html(paleta: list) -> str:
    if not paleta or not isinstance(paleta, list):
        return ""

    num_cards = len(paleta)
    if num_cards == 0:
        return ""

    scale = 3
    w_card = 182 * scale
    h_card = 163 * scale
    gap = 16 * scale  # 16px de separación entre tarjetas

    ancho_total = (w_card * num_cards) + (gap * (num_cards - 1))
    alto_total = h_card

    img = Image.new("RGB", (ancho_total, alto_total), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    for i, item in enumerate(paleta):
        x_offset = i * (w_card + gap)
        rol = item.get("rol", "Color")
        hex_val = item.get("hex", "#000000")
        pct = item.get("porcentaje", 0)
        _dibujar_tarjeta(draw, x_offset, 0, w_card, h_card, scale, rol, hex_val, pct)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    ancho_css = (182 * num_cards) + (16 * (num_cards - 1))

    return f"""
    <div style="margin-top: 14px; margin-bottom: 20px; text-align: left;">
        <img src="data:image/png;base64,{b64_str}" style="width: {ancho_css}px; max-width: 100%; height: auto; display: block;" />
    </div>
    """