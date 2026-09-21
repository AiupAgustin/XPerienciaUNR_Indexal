"""
graficos/grafico_zonas.py
Generación del histograma tonal de Ansel Adams con base plana y esquinas superiores curvas.
"""

import io
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# Escala tonal perceptual de grises (Zona 0 a Zona X)
TONOS_ZONAS = [
    "#000000",  # 0
    "#181818",  # I
    "#323232",  # II
    "#4D4D4D",  # III
    "#686868",  # IV
    "#828282",  # V
    "#9D9D9D",  # VI
    "#B7B7B7",  # VII
    "#D2D2D2",  # VIII
    "#E8E8E8",  # IX
    "#FDFDFD",  # X
]

ETIQUETAS_ROMANAS = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def _crear_patch_barra_redondeada(x_centro, ancho, alto, radio, color, edge_color):
    """
    Crea un Patch cuya base inferior es perfectamente plana (esquinas a 90°)
    y solo las dos esquinas superiores son redondeadas.
    """
    x0 = x_centro - ancho / 2.0
    x1 = x_centro + ancho / 2.0
    y0 = 0.0
    y1 = alto

    r = min(radio, ancho / 2.0, alto / 2.0)

    # Si la altura es insignificante, se dibuja un rectángulo plano
    if r <= 0.01:
        return patches.Rectangle((x0, y0), ancho, alto, facecolor=color, edgecolor=edge_color, linewidth=0.7)

    # Trazado SVG con arcos Bezier cuadráticos en la parte superior
    verts = [
        (x0, y0),                    # Inicio base izquierda
        (x0, y1 - r),                # Lado izquierdo hasta inicio de curvatura
        (x0, y1), (x0 + r, y1),      # Curva superior izquierda
        (x1 - r, y1),                # Borde superior plano
        (x1, y1), (x1, y1 - r),      # Curva superior derecha
        (x1, y0),                    # Lado derecho hasta base
        (x0, y0),                    # Cierre base plana
    ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]

    path = Path(verts, codes)
    return patches.PathPatch(path, facecolor=color, edgecolor=edge_color, linewidth=0.7)


def generar_grafico_zonas_base64(distribucion_zonas: dict) -> str:
    if not distribucion_zonas:
        return ""

    if isinstance(distribucion_zonas, dict):
        valores = [float(v) for v in distribucion_zonas.values()]
    else:
        valores = [float(v) for v in distribucion_zonas]

    if len(valores) < 11:
        valores += [0.0] * (11 - len(valores))
    valores = valores[:11]

    max_v = max(valores) if max(valores) > 0 else 1.0

    fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=200)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ancho_barra = 0.90
    radio = 0.035 * max_v  # Radio proporcional a la escala de datos

    for i, (val, color) in enumerate(zip(valores, TONOS_ZONAS)):
        # Altura mínima visual para que las zonas en 0% se vean como una delgada base
        h = max(val, max_v * 0.015)
        edge = "#D1D5DB" if i >= 9 else color

        patch = _crear_patch_barra_redondeada(i, ancho_barra, h, radio, color, edge)
        ax.add_patch(patch)

    # Configuración de límites y visibilidad
    ax.set_xlim(-0.8, 10.8)
    ax.set_ylim(0, max_v * 1.25)
    ax.axis("off")

    font_mono = {"fontfamily": "monospace", "color": "#444748"}

    # 1. Título superior
    ax.text(
        -0.6,
        max_v * 1.18,
        "SISTEMA DE ZONAS · ANSEL ADAMS - DISTRIBUCIÓN TONAL",
        fontsize=9.5,
        weight="medium",
        **font_mono,
    )

    # 2. Etiquetas inferiores (0, I, II...)
    for i, etiqueta in enumerate(ETIQUETAS_ROMANAS):
        ax.text(
            i,
            -max_v * 0.08,
            etiqueta,
            ha="center",
            va="top",
            fontsize=9,
            weight="medium",
            **font_mono,
        )

    # 3. Subtítulos inferiores alineados
    y_subtitulos = -max_v * 0.20
    ax.text(
        -0.5,
        y_subtitulos,
        "Sombras puras",
        ha="left",
        va="top",
        fontsize=8.5,
        **font_mono,
    )
    ax.text(
        5.0,
        y_subtitulos,
        "Medias tintas",
        ha="center",
        va="top",
        fontsize=8.5,
        **font_mono,
    )
    ax.text(
        10.5,
        y_subtitulos,
        "Altas luces",
        ha="right",
        va="top",
        fontsize=8.5,
        **font_mono,
    )

    # Render a memoria en base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=120, bbox_inches="tight", pad_inches=0.08)
    buffer.seek(0)
    b64_str = base64.b64encode(buffer.read()).decode("utf-8").replace("\n", "").replace("\r", "")
    plt.close(fig)

    return f'<img src="data:image/png;base64,{b64_str}" width="560" />'