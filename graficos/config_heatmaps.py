"""
Configuración centralizada y parámetros de visión para los mapas compositivos
(Gradiente cromático, Tensión vectorial y Peso visual).
"""

PARAMS_COMPOSICION = {
    "maxSide": 1100,
    "macroBlurSigma": 3.0,
    "palette": {
        "neutralDark": "#44474E",
        "neutralMid": "#74777F",
        "blue": "#0057FF",
        "red": "#C94B63",
        "warn": "#FEF9C3"
    },
    "chroma": {
        "bands": 5,
        "blurSigma": 4.0,
        "satWeight": 0.6,
        "warmWeight": 0.4,
        "peakThreshold": 0.55,
        "normPercentile": 0.99,
        "minReference": 0.35,
        "contourWidth": 1.5,
        "contrastWeight": 1.4,
        "textureWeight": 0.3
    },
    "tension": {
        "blurSigma": 4.2,
        "cannyLow": 80,
        "cannyHigh": 170,
        "houghThresholdRatio": 0.22,
        "minLineLengthRatio": 0.18,
        "maxLineGapRatio": 0.03,
        "maxLines": 14,
        "morphOpenRadius": 1,
        "edgePercentile": 0.88,
        "edgeLowRatio": 0.38,
        "minComponentRatio": 0.016,
        "flow": {
            "minLengthRatio": 0.05,        # Permite capturar tramos del saxofón sin exigir un recorrido tan extenso
            "maxFlows": 12,
            "simplifyTol": 2.5,
            "linkDist": 28,
            "linkAngleTol": 38,
            "sampleStep": 2,
            "seedPercentile": 0.89,        # Exige mayor nitidez para arrancar el trazo (ignora el desenfoque del fondo)
            "traceFloorRatio": 0.48,
            "maxTurn": 38,
            "suppressionRadius": 5,        # Radio menor para permitir directrices paralelas en el cuerpo del instrumento
            "maxSteps": 320
        },
        "mergeAngleTol": 7.0,
        "mergeDistTol": 12.0,
        "fallbackRatios": [0.16, 0.12],
        "diagonalRanges": [
            (15.0, 75.0),
            (105.0, 165.0)
        ],
        "minAcuteAngle": 15.0,
        "lineWidth": 3.5,
        "nodeRadius": 5
    },
    "weight": {
        "blurSigma": 4.5,
        "minAreaRatio": 0.012,
        "maxMasses": 8,
        "morphOpenRadius": 2,
        "lineWidth": 2.5
    },
    "display": {
        "singleLayerOpacity": 0.85,
        "blendDefault": 0.5
    }
}


def hex_a_bgr(color_hex: str) -> tuple[int, int, int]:
    """Convierte un color hexadecimal '#RRGGBB' al formato BGR usado por OpenCV."""
    color_hex = color_hex.lstrip("#")
    r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
    return (b, g, r)


# Colores BGR precalculados listos para dibujar
COLOR_ROJO_BGR = hex_a_bgr(PARAMS_COMPOSICION["palette"]["red"])       # #C94B63 -> (99, 75, 201)
COLOR_AZUL_BGR = hex_a_bgr(PARAMS_COMPOSICION["palette"]["blue"])      # #0057FF -> (255, 87, 0)
COLOR_AMARILLO_BGR = hex_a_bgr(PARAMS_COMPOSICION["palette"]["warn"])  # #FEF9C3 -> (195, 249, 254)