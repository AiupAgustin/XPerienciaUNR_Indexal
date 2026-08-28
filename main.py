
#streamlit run main.py

import time
import os
import base64
import streamlit as st
import streamlit.components.v1 as components
import json
import math
from core.reportes.orquestador import compilar_datos_reporte, MAPA_CATEGORIA_A_ID
from core.reportes.generador_html import renderizar_reporte_html
from core.reportes.generador_pdf import generar_reporte_pdf

# Ruta absoluta garantizada a assets/imagenes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_IMAGENES = os.path.join(BASE_DIR, "assets", "imagenes")


# -----------------------------------------------------------------
# FUNCIÓN AUXILIAR GLOBAL: CONVERTIR SVG A BASE64
# -----------------------------------------------------------------
def cargar_svg_base64(ruta_relativa):
    try:
        with open(ruta_relativa, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""

# -----------------------------------------------------------------
# FUNCIÓN AUXILIAR: GENERAR HTML DEL SIDEBAR CON ITEM ACTIVO
# -----------------------------------------------------------------
def obtener_sidebar_html(
    item_activo="reportes",
    img_logo="",
    icon_home="",
    icon_note_add="",
    icon_photo_lib="",
    icon_assessment="",
    icon_settings="",
):
    act_inicio = "active" if item_activo == "inicio" else ""
    act_nuevo = "active" if item_activo == "nuevo" else ""
    act_galeria = "active" if item_activo == "galeria" else ""
    act_reportes = "active" if item_activo == "reportes" else ""
    act_config = "active" if item_activo == "config" else ""

    return f"""
    <style>
        /* Íconos inactivos forzados a gris neutro */
        .nav-item-btn .nav-icon-img {{
            width: 16px;
            height: 16px;
            min-width: 16px;
            min-height: 16px;
            display: block;
            flex-shrink: 0;
            filter: brightness(0) saturate(100%) invert(27%) sepia(6%) saturate(432%) hue-rotate(152deg) brightness(93%) contrast(86%) !important;
            transition: filter 0.2s ease;
        }}

        /* Ícono del botón activo forzado al azul Indexal */
        .nav-item-btn.active .nav-icon-img {{
            filter: invert(19%) sepia(97%) saturate(5412%) hue-rotate(225deg) brightness(102%) contrast(106%) !important;
        }}
    </style>

    <aside class="sidebar">
        <div class="sidebar-brand" id="btnSidebarLogo">
            <img src="{img_logo}" class="sidebar-logo-img" alt="Indexal">
            <span class="sidebar-brand-text">INDEXAL</span>
        </div>

        <div class="nav-label-wrap">
            <span class="menu-title">MENÚ PRINCIPAL</span>
        </div>
        
        <div class="nav-items-wrapper">
            <button class="nav-item-btn {act_inicio}" id="btnMenuInicio">
                <img src="{icon_home}" class="nav-icon-img" alt="Inicio">
                <span class="nav-item-text">Inicio</span>
            </button>

            <button class="nav-item-btn {act_nuevo}" id="btnMenuNuevo">
                <img src="{icon_note_add}" class="nav-icon-img" alt="Nuevo análisis">
                <span class="nav-item-text">Nuevo análisis</span>
            </button>

            <button class="nav-item-btn {act_galeria}" id="btnMenuGaleria">
                <img src="{icon_photo_lib}" class="nav-icon-img" alt="Galería">
                <span class="nav-item-text">Galería</span>
            </button>

            <button class="nav-item-btn {act_reportes}" id="btnMenuReportes">
                <img src="{icon_assessment}" class="nav-icon-img" alt="Reportes">
                <span class="nav-item-text">Reportes</span>
            </button>

            <button class="nav-item-btn {act_config}" id="btnMenuConfig">
                <img src="{icon_settings}" class="nav-icon-img" alt="Configuración">
                <span class="nav-item-text">Configuración</span>
            </button>
        </div>
    </aside>
    """

st.set_page_config(
    page_title="Indexal", 
    page_icon="assets/iconos/spinner.svg", 
    layout="centered"
)

# -----------------------------------------------------------------
# 1. INICIALIZACIÓN SEGURA DE ESTADO (Evita AttributeError)
# -----------------------------------------------------------------
if "pantalla_actual" not in st.session_state:
    st.session_state["pantalla_actual"] = "splash"

if "filtro_galeria" not in st.session_state:
    st.session_state["filtro_galeria"] = "Todo"

# -----------------------------------------------------------------
# PANTALLA 1: SPLASH SCREEN (Logo e Instrucción Cliqueables)
# -----------------------------------------------------------------
def render_splash():
    st.markdown("""
        <style>
        /* Fondo principal */
        .stApp {
            background-color: #0B1020 !important;
        }
        
        header[data-testid="stHeader"] { display: none !important; }
        #MainMenu, footer { visibility: hidden; }
        .element-container a.anchor-link { display: none !important; }

        /* Centrado absoluto vertical y horizontal */
        div[data-testid="stAppViewBlockContainer"] {
            padding-top: 0px !important;
            margin-top: 0px !important;
            min-height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
        }

        .block-container {
            max-width: 400px !important;
            padding: 0px !important;
            margin: auto !important;
        }

        /* Anular gaps/espacios automáticos de Streamlit en Splash */
        div[data-testid="stVerticalBlock"] > div {
            gap: 0px !important;
            margin-bottom: 0px !important;
        }

        /* OCULTAR COMPLETAMENTE EL BOTÓN NATIVO DESDE EL INICIO */
        div.stButton,
        div[data-testid="stElementContainer"]:has(div.stButton) {
            display: none !important;
            visibility: hidden !important;
            position: absolute !important;
            top: -9999px !important;
            left: -9999px !important;
            width: 0px !important;
            height: 0px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            overflow: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. LEER Y CONVERTIR EL LOGO A BASE64
    img_src = cargar_svg_base64("assets/iconos/logo_x.svg")

    # 2. LOGO + TEXTO INTEGRADOS CON 15PX EXACTOS
    splash_html = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500&display=swap');

            html, body {{ 
                margin: 0 !important; 
                padding: 0 !important; 
                overflow: hidden !important; 
                background: transparent !important;
                height: 100% !important;
                width: 100% !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
            }}

            .splash-wrapper {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 100%;
                user-select: none;
            }}

            .splash-logo {{
                width: 229px;
                height: 229px;
                cursor: pointer;
                transition: transform 0.2s ease;
                display: block;
            }}

            .splash-logo:hover {{
                transform: scale(1.03);
            }}

            .splash-text {{
                width: 300px;
                max-width: 100%;
                color: #808799;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.4px;
                text-align: center;
                margin-top: 15px; /* Distancia exacta de Figma */
                cursor: pointer;
                transition: color 0.2s ease;
            }}

            .splash-text:hover {{
                color: #FFFFFF;
            }}
        </style>

        <div class="splash-wrapper">
            <img src="{img_src}" id="splashLogo" class="splash-logo" alt="Indexal Logo">
            <span id="splashText" class="splash-text">Haga clic en el centro para ingresar</span>
        </div>

        <script>
            const parentDoc = window.parent.document;
            
            function triggerNavigation() {{
                const hiddenBtn = parentDoc.querySelector('div.stButton button');
                if (hiddenBtn) {{
                    hiddenBtn.click();
                }}
            }}

            // Clic en el logo
            document.getElementById('splashLogo').addEventListener('click', triggerNavigation);

            // Clic en el texto
            document.getElementById('splashText').addEventListener('click', triggerNavigation);
        </script>
    """
    
    components.html(splash_html, height=280)

    # 3. EL BOTÓN DISPARADOR CON CARÁCTER INVISIBLE (Cero texto visible al cargar)
    if st.button("\u200b", key="btn_hidden"):
        st.session_state["pantalla_actual"] = "home"
        st.rerun()

# -----------------------------------------------------------------
# PANTALLA 2: HOME
# -----------------------------------------------------------------
def render_home():
    st.markdown("""
        <style>
        /* Importamos Orbitron, Inter y Space Grotesk */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@600;700&family=Space+Grotesk:wght@500&display=swap');

        /* Fondo principal */
        .stApp {
            background-color: #0B1020 !important;
        }
        
        /* Ocultar header e interfaz por defecto */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        #MainMenu, footer {visibility: hidden;}
        .element-container a.anchor-link {display: none !important;}
        h1 a, h2 a, h3 a {display: none !important;}

        /* Centrado vertical absoluto con Flexbox */
        div[data-testid="stAppViewBlockContainer"] {
            padding-top: 0px !important;
            margin-top: 0px !important;
            min-height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        /* Contenedor principal */
        .block-container {
            max-width: 400px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            margin: auto !important;
        }

        /* Reducción de gaps de Streamlit */
        [data-testid="stVerticalBlock"] > div {
            gap: 0px !important;
        }

        /* Título INDEXAL */
        .title-indexal {
            color: #FFFFFF !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 34px !important;
            font-weight: 700 !important;
            letter-spacing: 3px !important;
            text-align: center !important;
            margin-top: 0px !important;
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
            line-height: 1 !important; /* Mantiene la caja colapsada al texto */
        }

        /* Subtítulo (Ajuste forzado a 1px) */
        .subtitle-indexal {
            color: #668CF2 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            letter-spacing: 2px !important;
            text-align: center !important;
            margin-top: 1px !important; /* Distancia exacta de 1px */
            margin-bottom: 43px !important;
            padding-top: 0px !important;
            line-height: 1 !important;
        }

        /* Separación de botones */
        [data-testid="stHorizontalBlock"] {
            gap: 16px !important;
        }

        /* ESTILOS DEL BOTÓN "ANALIZAR IMAGEN" */
        div.stButton > button[kind="primary"] {
            background-color: #0057FF !important; /* <--- Color Hex de Figma */
            color: #FFFFFF !important;             /* Color del texto */
            border: none !important;
            border-radius: 8px !important;         /* Radio de esquinas */
            height: 51px !important;               /* <--- Altura calculada/fijada */
            padding: 16px 24px !important;         /* <--- Relleno de Figma */
            font-family: 'Space Grotesk', sans-serif !important; 
            font-size: 14.5px !important;
            font-weight: 500 !important;           /* Peso/Grosor de la fuente */
        }

        /* ESTILOS DEL BOTÓN "EXPLORAR GALERIA" */
        div.stButton > button[kind="secondary"] {
            background-color: #262B38 !important; /* <--- Hex exacto */
            color: #BFC4D1 !important;            /* <--- Color de texto exacto */
            border: 1px solid #4D5261 !important;  /* <--- Borde exacto */
            border-radius: 8px !important;
            height: 51px !important;
            padding: 16px 24px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 14.5px !important;
            font-weight: 500 !important;
        }

        </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # ELEMENTO 1: TÍTULO Y SUBTÍTULO
    # -----------------------------------------------------------------
    st.markdown("""
        <div translate="no">
            <h1 class="title-indexal">INDEXAL</h1>
            <p class="subtitle-indexal">ANÁLISIS VISUAL ASISTIDO POR IA</p>
        </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # ELEMENTO 2: BOTONES
    # -----------------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analizar imagen", use_container_width=True, type="primary"):
            st.session_state["pantalla_actual"] = "analizar"
            st.rerun()
    with col2:
        if st.button("Explorar galería", use_container_width=True, type="secondary"):
            st.session_state["pantalla_actual"] = "galeria"
            st.rerun()

# -----------------------------------------------------------------
# PANTALLA 3: GALERÍA DE IMÁGENES ANALIZADAS 
# -----------------------------------------------------------------

def render_galeria():
    import math

    st.markdown(
        """
        <script>
            if (!parent.document.getElementById('font-space-grotesk')) {
                const link = parent.document.createElement('link');
                link.id = 'font-space-grotesk';
                link.rel = 'stylesheet';
                link.href = 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap';
                parent.document.head.appendChild(link);
            }
        </script>

        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp, .stApp * {
            font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        }

        .stApp {
            background-color: #EAEAE8 !important;
        }

        header[data-testid="stHeader"], header, .stAppHeader { 
            display: none !important; 
            height: 0px !important;
            visibility: hidden !important;
        }

        #MainMenu, footer { visibility: hidden; }

        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewBlockContainer"],
        div[data-testid="stMainBlockContainer"],
        section.main, .stMain, .main {
            padding: 0px !important;
            margin: 0px !important;
            min-height: auto !important;
            display: block !important;
            background-color: #EAEAE8 !important;
        }

        .block-container, div[data-testid="block-container"] {
            max-width: 100% !important;
            width: 100% !important;
            padding: 0px !important;
            margin: 0px !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0px !important;
        }
        
        div[data-testid="stVerticalBlock"] > div:first-child {
            margin-top: 0px !important;
            padding-top: 0px !important;
        }

        div.stButton, div[data-testid="stElementContainer"]:has(div.stButton) {
            display: none !important;
            visibility: hidden !important;
            position: absolute !important;
            top: -9999px !important;
            left: -9999px !important;
            width: 0px !important;
            height: 0px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            overflow: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    img_logo = cargar_svg_base64("assets/iconos/logo_x.svg")
    icon_chart_src = cargar_svg_base64("assets/iconos/icon-nav-chart.svg")
    icon_doc_src = cargar_svg_base64("assets/iconos/icon-nav-doc.svg")
    icon_arrow_src = cargar_svg_base64("assets/iconos/vector.svg")

    # MOCK DATA CON NOMBRES DE CATEGORÍA CORREGIDOS
    INFORMES_MOCK = [
        {
            "id": "inf_01",
            "categoria": "Semiótico",
            "filtro_key": "semiotico",
            "descripcion": "Sistema de identidad completo con aplicaciones en distintos soportes",
            "modulo": "Análisis completo · 6 módulos",
            "color_placeholder": "#E6C2B4",
            "imagen_url": None,
        },
        {
            "id": "inf_02",
            "categoria": "UI / UX",
            "filtro_key": "ui_ux",
            "descripcion": "Pantalla principal con sistema de navegación y visualización de datos",
            "modulo": "Módulo A · Composición visual",
            "color_placeholder": "#6B7280",
            "imagen_url": None,
        },
        {
            "id": "inf_03",
            "categoria": "Packaging",
            "filtro_key": "packaging",
            "descripcion": "Packaging minimalista con código cromático funcional para línea premium",
            "modulo": "Módulo B · Paleta cromática",
            "color_placeholder": "#36635C",
            "imagen_url": None,
        },
        {
            "id": "inf_04",
            "categoria": "Tipografía",
            "filtro_key": "tipografia",
            "descripcion": "Jerarquía tipográfica para publicación impresa y digital",
            "modulo": "Módulos A, B, C · Visual",
            "color_placeholder": "#C8C4B7",
            "imagen_url": None,
        },
        {
            "id": "inf_05",
            "categoria": "Logotipo",
            "filtro_key": "logotipo",
            "descripcion": "Construcción de isotipo y aplicaciones sobre fondo oscuro",
            "modulo": "Análisis completo · 6 módulos",
            "color_placeholder": "#282B30",
            "imagen_url": None,
        },
        {
            "id": "inf_06",
            "categoria": "Afiches",
            "filtro_key": "afiches",
            "descripcion": "Serie de afiches con sistema modular de retícula",
            "modulo": "Módulo E · Retórica visual",
            "color_placeholder": "#D8A75F",
            "imagen_url": None,
        },
    ]

    # Conteo dinámico de categorías
    cant_semiotico = sum(1 for x in INFORMES_MOCK if x["filtro_key"] == "semiotico")
    cant_logotipo = sum(1 for x in INFORMES_MOCK if x["filtro_key"] == "logotipo")
    cant_afiches = sum(1 for x in INFORMES_MOCK if x["filtro_key"] == "afiches")
    cant_packaging = sum(1 for x in INFORMES_MOCK if x["filtro_key"] == "packaging")
    cant_tipografia = sum(1 for x in INFORMES_MOCK if x["filtro_key"] == "tipografia")
    cant_uiux = sum(1 for x in INFORMES_MOCK if x["filtro_key"] == "ui_ux")

    # Construcción dinámica de tarjetas
    cards_html = ""
    for item in INFORMES_MOCK:
        # Si tiene imagen real la muestra; si no, usa el placeholder cromático
        if item.get("imagen_url"):
            area_visual = f'<div class="card-image-area" style="background-image: url(\'{item["imagen_url"]}\'); background-size: cover; background-position: center;"></div>'
        else:
            area_visual = f'<div class="card-image-area" style="background-color: {item.get("color_placeholder", "#E5E7EB")};"></div>'

        cards_html += f"""
        <div class="card-item notranslate" data-category="{item['filtro_key']}" translate="no">
            {area_visual}
            <div class="card-body">
                <h3 class="card-title" translate="no">{item['categoria']}</h3>
                <p class="card-desc" translate="no">{item['descripcion']}</p>
                <div class="card-footer-row">
                    <span class="card-module-text" translate="no">{item['modulo']}</span>
                </div>
            </div>
        </div>
        """

    # HTML Unificado
    galeria_unificada_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Space Grotesk', sans-serif !important;
                -webkit-font-smoothing: antialiased;
            }}

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background-color: #EAEAE8 !important;
                width: 100% !important;
                min-height: 100vh !important;
                display: flex;
                flex-direction: column;
            }}

            /* NAVBAR */
            .navbar-container {{
                width: 100%;
                height: 76px;
                background-color: #0B1020;
                padding: 0 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-shrink: 0;
            }}

            .navbar-brand {{
                display: flex;
                align-items: center;
                gap: 12px;
                cursor: pointer;
                text-decoration: none;
                transition: opacity 0.2s ease;
            }}

            .navbar-brand:hover {{ opacity: 0.85; }}

            .navbar-logo-img {{
                width: 32px;
                height: 32px;
                display: block;
            }}

            .navbar-brand-text {{
                color: #FFFFFF;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 17px;
                font-weight: 700;
            }}

            .navbar-nav {{
                display: flex;
                align-items: center;
                gap: 26px;
            }}

            .nav-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13.5px;
                font-weight: 400;
                color: #BFC4CC;
                cursor: pointer;
                transition: color 0.2s ease;
            }}

            .nav-item:hover {{ color: #FFFFFF; }}

            .nav-icon {{
                width: 14px;
                height: 14px;
                display: block;
            }}

            /* HERO */
            .hero-container {{
                width: 100%;
                background-color: #F4F4F2;
                padding: 64px 48px 48px 48px;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
                flex-shrink: 0;
            }}

            .hero-text-block {{
                display: flex;
                flex-direction: column;
            }}

            .hero-badge {{
                color: #0057FF;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 4.2px;
                margin: 0;
            }}

            .hero-title {{
                color: #111111;
                font-size: 64px;
                font-weight: 700;
                line-height: 1;
                letter-spacing: -1.6px;
                margin: 16px 0 0 0;
            }}

            .hero-subtitle {{
                color: #444748;
                font-size: 15px;
                font-weight: 400;
                letter-spacing: 0.8px;
                margin: 16px 0 0 0;
            }}

            .hero-btn-action {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 28px;
                background-color: #0057FF;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: background-color 0.2s ease, transform 0.1s ease;
            }}

            .hero-btn-action:hover {{ background-color: #0046D5; }}
            .hero-btn-action:active {{ transform: scale(0.98); }}

            .hero-btn-text {{
                color: #FFFFFF;
                font-size: 16.5px;
                font-weight: 700;
            }}

            .hero-btn-icon {{
                width: 12px;
                height: 8px;
                display: block;
            }}

            /* BARRA DE FILTROS */
            .filters-bar-container {{
                width: 100%;
                height: 73px;
                background-color: #EAEAE8;
                padding: 20px 48px;
                display: flex;
                align-items: center;
                gap: 12px;
                overflow-x: auto;
                flex-shrink: 0;
            }}

            .filter-btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                height: 33px;
                padding: 8px 16px;
                border-radius: 999px;
                cursor: pointer;
                user-select: none;
                border: 1px solid #C4C6CF;
                background-color: #FFFFFF;
                color: #111111;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s ease;
                flex-shrink: 0;
                outline: none;
            }}

            .filter-btn:hover {{
                background-color: #F8F9FA;
                border-color: #A8ACB4;
            }}

            .filter-btn.active {{
                background-color: #0057FF !important;
                border-color: #0057FF !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
            }}

            .filter-btn.active .filter-pill-count {{
                color: #FFFFFF !important;
            }}

            .filter-pill-count {{
                color: #444748;
                font-size: 12px;
                font-weight: 400;
            }}

            /* GRILLA */
            .galeria-section-container {{
                width: 100%;
                background-color: #EAEAE8;
                padding: 24px 48px 48px 48px;
                flex: 1;
            }}

            .galeria-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                width: 100%;
            }}

            .card-item {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #C4C6CF;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                cursor: pointer;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }}

            .card-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            }}

            .card-image-area {{
                width: 100%;
                height: 220px;
                display: block;
            }}

            .card-body {{
                display: flex;
                flex-direction: column;
                padding: 20px 20px 22px 20px;
                gap: 10px;
                background-color: #FFFFFF;
                box-sizing: border-box;
            }}

            .card-title {{
                color: #111111;
                font-size: 16px;
                font-weight: 700;
                line-height: 1.2;
                letter-spacing: -0.3px;
                margin: 0;
            }}

            .card-desc {{
                color: #5E6366;
                font-size: 13px;
                font-weight: 400;
                line-height: 1.4;
                margin: 0;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                min-height: 36px;
            }}

            .card-footer-row {{
                display: flex;
                align-items: center;
                width: 100%;
                margin-top: 6px;
            }}

            .card-module-text {{
                color: #444748;
                font-size: 12px;
                font-weight: 400;
                line-height: normal;
                text-align: left;
            }}

            /* FOOTER */
            .footer-container {{
                display: flex;
                width: 100%;
                padding: 20px 48px;
                justify-content: space-between;
                align-items: center;
                background: #FFFFFF;
                border-top: 1px solid #C4C6CF;
                margin-top: auto;
                flex-shrink: 0;
            }}

            .footer-text {{
                color: #444748;
                font-size: 12px;
                font-weight: 400;
                margin: 0;
            }}

            .footer-links {{ display: flex; gap: 20px; }}

            .footer-link {{
                color: #0057FF;
                font-size: 12px;
                font-weight: 500;
                text-decoration: none;
            }}

            .footer-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <!-- NAVBAR -->
        <div class="navbar-container">
            <div class="navbar-brand" id="btnLogoHome">
                <img src="{img_logo}" class="navbar-logo-img" alt="Indexal">
                <span class="navbar-brand-text" translate="no">INDEXAL</span>
            </div>
            <div class="navbar-nav">
                <div class="nav-item" id="btnNavAnalisis">
                    <img src="{icon_chart_src}" class="nav-icon" alt="Análisis">
                    <span translate="no">Análisis</span>
                </div>
                <div class="nav-item" id="btnNavReportes">
                    <img src="{icon_doc_src}" class="nav-icon" alt="Reportes">
                    <span translate="no">Reportes</span>
                </div>
            </div>
        </div>

        <!-- HERO -->
        <div class="hero-container">
            <div class="hero-text-block">
                <div class="hero-badge" translate="no">DIAGNÓSTICO VISUAL ASISTIDO POR IA</div>
                <h1 class="hero-title" translate="no">Galería de<br>imágenes<br>analizadas</h1>
                <div class="hero-subtitle" translate="no">SEMIÓTICO · TÉCNICO · PDF</div>
            </div>
            <div class="hero-action-block">
                <button class="hero-btn-action" id="btnAnalizarImagen">
                    <span class="hero-btn-text" translate="no">Analizar mi imagen</span>
                    <img src="{icon_arrow_src}" class="hero-btn-icon" alt="->">
                </button>
            </div>
        </div>

        <!-- FILTROS -->
        <div class="filters-bar-container">
            <button class="filter-btn active" data-filter="all" translate="no">Todo</button>
            <button class="filter-btn" data-filter="semiotico">
                <span translate="no">Semiótico</span>
                <span class="filter-pill-count" translate="no">{cant_semiotico}</span>
            </button>
            <button class="filter-btn" data-filter="logotipo">
                <span translate="no">Logotipo</span>
                <span class="filter-pill-count" translate="no">{cant_logotipo}</span>
            </button>
            <button class="filter-btn" data-filter="afiches">
                <span translate="no">Afiches</span>
                <span class="filter-pill-count" translate="no">{cant_afiches}</span>
            </button>
            <button class="filter-btn" data-filter="packaging">
                <span translate="no">Packaging</span>
                <span class="filter-pill-count" translate="no">{cant_packaging}</span>
            </button>
            <button class="filter-btn" data-filter="tipografia">
                <span translate="no">Tipografía</span>
                <span class="filter-pill-count" translate="no">{cant_tipografia}</span>
            </button>
            <button class="filter-btn" data-filter="ui_ux">
                <span translate="no">UI/UX</span>
                <span class="filter-pill-count" translate="no">{cant_uiux}</span>
            </button>
        </div>

        <!-- GRILLA DE CARDS -->
        <div class="galeria-section-container notranslate" translate="no">
            <div class="galeria-grid" id="gridGaleria" translate="no">
                {cards_html}
            </div>
        </div>

        <!-- FOOTER -->
        <footer class="footer-container notranslate" translate="no">
            <p class="footer-text">© 2026 Indexal - Análisis visual asistido por IA - Todos los derechos reservados</p>
            <div class="footer-links">
                <a href="javascript:void(0)" class="footer-link">Términos y condiciones</a>
                <a href="javascript:void(0)" class="footer-link">Política de privacidad</a>
            </div>
        </footer>

        <script>
            const parentDoc = window.parent.document;
            
            // Navegación
            document.getElementById('btnLogoHome').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 0) allButtons[0].click();
            }});

            document.getElementById('btnAnalizarImagen').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 1) allButtons[1].click();
            }});

            document.getElementById('btnNavAnalisis').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 1) allButtons[1].click();
            }});

            document.getElementById('btnNavReportes').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 2) allButtons[2].click();
            }});

            // Lógica interactiva de Filtros
            const filterButtons = document.querySelectorAll('.filter-btn');
            const cards = document.querySelectorAll('.card-item');

            filterButtons.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    filterButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');

                    const selectedFilter = this.getAttribute('data-filter');

                    cards.forEach(card => {{
                        const cardCategory = card.getAttribute('data-category');
                        if (selectedFilter === 'all' || cardCategory === selectedFilter) {{
                            card.style.display = 'flex';
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """

    # Disparadores ocultos de Streamlit
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("\u200b", key="btn_hidden_nav_home"):
            st.session_state["pantalla_actual"] = "home"
            st.rerun()
    with col_btn2:
        if st.button("\u200b", key="btn_hidden_analizar"):
            st.session_state["pantalla_actual"] = "analizar"
            st.rerun()
    with col_btn3:
        if st.button("\u200b", key="btn_hidden_nav_reportes"):
            st.session_state["pantalla_actual"] = "reportes"
            st.rerun()

    total_tarjetas = len(INFORMES_MOCK)
    filas = max(1, math.ceil(total_tarjetas / 3))
    
    altura_grilla_dinamica = (filas * 395) + 24
    altura_total_componente = 76 + 360 + 73 + altura_grilla_dinamica + 65 

    components.html(galeria_unificada_html, height=altura_total_componente, scrolling=False)

# -----------------------------------------------------------------
# PANTALLA 4: NUEVO ANÁLISIS
# -----------------------------------------------------------------
def render_analizar():
    if "paso_actual" not in st.session_state:
        st.session_state["paso_actual"] = 1
    if "tipo_analisis" not in st.session_state:
        st.session_state["tipo_analisis"] = None
    if "imagen_cargada" not in st.session_state:
        st.session_state["imagen_cargada"] = False

    # Estado de módulos transversales
    if "transversal_wcag" not in st.session_state:
        st.session_state["transversal_wcag"] = False
    if "transversal_historicas" not in st.session_state:
        st.session_state["transversal_historicas"] = False

    # Diccionario de módulos individuales (6 módulos)
    modulos_por_categoria = {
        "semiotico": [
            {
                "id": "composicion_visual",
                "titulo": "Composición visual",
                "desc": (
                    "Evaluación de pesos visuales, tensiones, grillas y"
                    " equilibrio general."
                ),
            },
            {
                "id": "paleta_cromatica",
                "titulo": "Paleta cromática",
                "desc": (
                    "Estudio de armonía de color, contrastes, saturación y"
                    " temperatura."
                ),
            },
            {
                "id": "iluminacion",
                "titulo": "Iluminación",
                "desc": (
                    "Análisis de sombras, puntos de luz, volumen y profundidad"
                    " visual."
                ),
            },
            {
                "id": "semiotica_imagen",
                "titulo": "Semiótica de la imagen",
                "desc": (
                    "Interpretación de signos, simbolismo cultural y códigos"
                    " visuales."
                ),
            },
            {
                "id": "retorica_visual",
                "titulo": "Retórica visual",
                "desc": (
                    "Identificación de metáforas, metonimias, hipérboles y"
                    " figuras retóricas."
                ),
            },
            {
                "id": "contexto_denotacion",
                "titulo": "Contexto y denotación",
                "desc": (
                    "Nivel literal de los elementos observables y su contexto"
                    " comunicacional."
                ),
            },
        ]
    }

    lista_modulos_activa = modulos_por_categoria.get(
        st.session_state["tipo_analisis"] or "semiotico",
        modulos_por_categoria["semiotico"],
    )
    todos_los_ids = [m["id"] for m in lista_modulos_activa]

    if "modulos_seleccionados" not in st.session_state:
        st.session_state["modulos_seleccionados"] = []

    paso_actual = st.session_state["paso_actual"]
    tipo_sel = st.session_state["tipo_analisis"]

    c1 = (
        "active"
        if paso_actual == 1
        else ("completed" if paso_actual > 1 else "pending")
    )
    t1 = "active" if paso_actual == 1 else ""
    l1 = "completed" if paso_actual > 1 else ""

    c2 = (
        "active"
        if paso_actual == 2
        else ("completed" if paso_actual > 2 else "pending")
    )
    t2 = "active" if paso_actual == 2 else ""
    l2 = "completed" if paso_actual > 2 else ""

    c3 = (
        "active"
        if paso_actual == 3
        else ("completed" if paso_actual > 3 else "pending")
    )
    t3 = "active" if paso_actual == 3 else ""
    l3 = "completed" if paso_actual > 3 else ""

    c4 = (
        "active"
        if paso_actual == 4
        else ("completed" if paso_actual > 4 else "pending")
    )
    t4 = "active" if paso_actual == 4 else ""

    # Conteo total de módulos seleccionados
    total_modulos_activos = len(st.session_state["modulos_seleccionados"])
    if st.session_state["transversal_wcag"]:
        total_modulos_activos += 1
    if st.session_state["transversal_historicas"]:
        total_modulos_activos += 1

    tiempo_min = max(10, total_modulos_activos * 4)
    tiempo_max = max(15, total_modulos_activos * 6)

    puede_generar = (
        st.session_state["imagen_cargada"]
        and (st.session_state["tipo_analisis"] is not None)
        and (total_modulos_activos > 0)
    )

    paso2_habilitado = paso_actual >= 2
    paso3_habilitado = paso_actual >= 3
    clase_disabled_p2 = "" if paso2_habilitado else "disabled-step"
    clase_disabled_p3 = "" if paso3_habilitado else "disabled-step"
    clase_btn_generar_dis = "" if puede_generar else "btn-disabled"

    sel_semiotico = "selected" if tipo_sel == "semiotico" else ""
    sel_ui_ux = "selected" if tipo_sel == "ui_ux" else ""
    sel_packaging = "selected" if tipo_sel == "packaging" else ""
    sel_tipografia = "selected" if tipo_sel == "tipografia" else ""
    sel_logotipo = "selected" if tipo_sel == "logotipo" else ""
    sel_afiche = "selected" if tipo_sel == "afiche" else ""

    todos_seleccionados = (
        all(
            mid in st.session_state["modulos_seleccionados"]
            for mid in todos_los_ids
        )
        if todos_los_ids
        else False
    )

    # Textos dinámicos del área de subida
    if st.session_state["imagen_cargada"]:
        nom_mostrado = st.session_state.get("nombre_imagen", "Archivo cargado")
        texto_subida_main = f"✓ {nom_mostrado}"
        texto_subida_sub = "Hacé clic o arrastrá para cambiar la imagen"
        texto_subida_btn = "Cambiar archivo"
    else:
        texto_subida_main = "Arrastrá una imagen aquí"
        texto_subida_sub = "PNG, JPG, WebP · hasta 20 MB"
        texto_subida_btn = "Seleccionar archivo"

    # 1. HTML de la tarjeta maestra
    html_modulos_cards = f"""
    <div class="module-card {'selected' if todos_seleccionados else ''} {clase_disabled_p3}" id="cardMod_master">
        <div class="custom-checkbox {'checked' if todos_seleccionados else ''}">
            <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
        </div>
        <div class="module-badge module-badge-master">★</div>
        <div class="module-texts-wrap">
            <span class="module-title">Análisis completo (Todos los módulos)</span>
            <span class="module-desc">Diagnóstico integral que abarca todos los 6 niveles semióticos y perceptivos.</span>
        </div>
    </div>
    """

    # 2. HTML de los módulos individuales (A a la F)
    letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    for idx, mod in enumerate(lista_modulos_activa):
        letra = letras[idx] if idx < len(letras) else str(idx + 1)
        is_checked = mod["id"] in st.session_state["modulos_seleccionados"]
        clase_card_sel = "selected" if is_checked else ""

        html_modulos_cards += f"""
        <div class="module-card {clase_card_sel} {clase_disabled_p3}" id="cardMod_{idx}">
            <div class="custom-checkbox {'checked' if is_checked else ''}">
                <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            </div>
            <div class="module-badge">{letra}</div>
            <div class="module-texts-wrap">
                <span class="module-title">Módulo {letra} — {mod['titulo']}</span>
                <span class="module-desc">{mod['desc']}</span>
            </div>
        </div>
        """

    st.markdown(
        """
        <script>
            if (!parent.document.getElementById('font-space-grotesk')) {
                const link = parent.document.createElement('link');
                link.id = 'font-space-grotesk';
                link.rel = 'stylesheet';
                link.href = 'https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap';
                parent.document.head.appendChild(link);
            }
        </script>

        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp, .stApp * {
            font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        }

        .stApp {
            background-color: #F8F9FA !important;
        }

        header[data-testid="stHeader"], header, .stAppHeader { 
            display: none !important; 
            height: 0px !important;
            visibility: hidden !important;
        }

        #MainMenu, footer { visibility: hidden; }

        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewBlockContainer"],
        div[data-testid="stMainBlockContainer"],
        section.main, .stMain, .main {
            padding: 0px !important;
            margin: 0px !important;
            min-height: auto !important;
            display: block !important;
            background-color: #F8F9FA !important;
        }

        .block-container, div[data-testid="block-container"] {
            max-width: 100% !important;
            width: 100% !important;
            padding: 0px !important;
            margin: 0px !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0px !important;
        }

        /* Ocultamiento de widgets auxiliares manteniendo vivos sus eventos */
        div.stButton, 
        div[data-testid="stElementContainer"]:has(div.stButton),
        div[data-testid="stFileUploader"] {
            position: fixed !important;
            top: -9999px !important;
            left: -9999px !important;
            width: 1px !important;
            height: 1px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Carga de SVGs
    img_logo = cargar_svg_base64("assets/iconos/logo_x.svg")
    icon_home = cargar_svg_base64("assets/iconos/home.svg")
    icon_note_add = cargar_svg_base64("assets/iconos/note_add.svg")
    icon_photo_lib = cargar_svg_base64("assets/iconos/photo_library.svg")
    icon_assessment = cargar_svg_base64("assets/iconos/assessment.svg")
    icon_settings = cargar_svg_base64("assets/iconos/settings.svg")
    icon_search = cargar_svg_base64("assets/iconos/search.svg")
    icon_frame = cargar_svg_base64("assets/iconos/frame.svg")

    icon_palette = cargar_svg_base64("assets/iconos/palette.svg")
    icon_touch = cargar_svg_base64("assets/iconos/touch_app.svg")
    icon_inbox = cargar_svg_base64("assets/iconos/all_inbox.svg")
    icon_font = cargar_svg_base64("assets/iconos/font_download.svg")
    icon_watermark = cargar_svg_base64("assets/iconos/branding_watermark.svg")
    icon_crop = cargar_svg_base64("assets/iconos/crop_original.svg")
    icon_access = cargar_svg_base64("assets/iconos/icon-access.svg")
    icon_star = cargar_svg_base64("assets/iconos/stars.svg")

    sidebar_html = obtener_sidebar_html(
        item_activo="nuevo",
        img_logo=img_logo,
        icon_home=icon_home,
        icon_note_add=icon_note_add,
        icon_photo_lib=icon_photo_lib,
        icon_assessment=icon_assessment,
        icon_settings=icon_settings,
    )

    wcag_checked = "checked" if st.session_state["transversal_wcag"] else ""
    hist_checked = (
        "checked" if st.session_state["transversal_historicas"] else ""
    )

    analizar_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Space Grotesk', sans-serif !important;
            }}

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background-color: #F8F9FA !important;
                width: 100% !important;
                min-height: 100% !important;
            }}

            .layout-container {{
                display: flex;
                width: 100%;
                min-height: 100%;
            }}

            .sidebar {{
                width: 240px;
                min-width: 240px;
                background-color: #FFFFFF;
                border-right: 1px solid #C4C6CF;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                box-sizing: border-box;
            }}

            .sidebar-brand {{
                display: flex;
                width: 100%;
                height: 76px;
                padding: 0 20px;
                align-items: center;
                gap: 12px;
                background-color: #FFFFFF;
                border-bottom: 1px solid #C4C6CF;
                box-sizing: border-box;
                cursor: pointer;
                user-select: none;
                transition: opacity 0.2s ease;
            }}

            .sidebar-brand:hover {{
                opacity: 0.8;
            }}

            .sidebar-logo-img {{
                width: 32px;
                height: 32px;
                min-width: 32px;
                min-height: 32px;
                display: block;
                flex-shrink: 0;
                filter: brightness(0);
            }}

            .sidebar-brand-text {{
                color: #111111;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 17px;
                font-weight: 700;
                line-height: normal;
                letter-spacing: 0.5px;
            }}

            .nav-label-wrap {{
                display: flex;
                width: 100%;
                padding: 20px 20px 4px 20px;
                flex-direction: column;
                align-items: flex-start;
                background-color: #FFFFFF;
                box-sizing: border-box;
            }}

            .menu-title {{
                color: #444748;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 10px;
                font-style: normal;
                font-weight: 700;
                line-height: normal;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin: 0;
                user-select: none;
            }}

            .nav-items-wrapper {{
                display: flex;
                flex-direction: column;
                width: 100%;
                padding: 0 16px 16px 16px;
                gap: 4px;
                box-sizing: border-box;
            }}

            .nav-item-btn {{
                display: flex;
                align-items: center;
                gap: 12px;
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: transparent;
                cursor: pointer;
                text-decoration: none;
                box-sizing: border-box;
                transition: background-color 0.15s ease;
            }}

            .nav-item-btn:hover {{
                background-color: #F3F4F6;
            }}

            .nav-item-btn.active {{
                background-color: #E6EDFF;
            }}

            .nav-icon-img {{
                width: 16px;
                height: 16px;
                min-width: 16px;
                min-height: 16px;
                display: block;
                flex-shrink: 0;
            }}

            .nav-item-text {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-style: normal;
                font-weight: 400;
                line-height: normal;
                color: #444748;
                flex: 1 0 0;
                text-align: left;
            }}

            .nav-item-btn.active .nav-item-text {{
                color: #0057FF;
                font-weight: 500;
            }}

            .main-content {{
                flex: 1;
                display: flex;
                flex-direction: column;
                background-color: #F8F9FA;
                min-width: 0;
            }}

            .topbar {{
                display: flex;
                width: 100%;
                height: 76px;
                padding: 0 24px;
                align-items: center;
                gap: 16px;
                background-color: #FFFFFF;
                border-bottom: 1px solid #C4C6CF;
                box-sizing: border-box;
            }}

            .search-box {{
                display: flex;
                width: 360px;
                height: 38px;
                padding: 0 16px;
                align-items: center;
                gap: 12px;
                flex-shrink: 0;
                border-radius: 8px;
                background-color: #F3F4F1;
                box-sizing: border-box;
            }}

            .search-icon {{
                width: 16px;
                height: 16px;
                min-width: 16px;
                min-height: 16px;
                display: block;
                flex-shrink: 0;
            }}

            .search-input {{
                border: none !important;
                background: transparent !important;
                outline: none !important;
                box-shadow: none !important;
                width: 100%;
                color: #444748;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 13px;
                flex: 1 0 0;
            }}

            .search-input::placeholder {{
                color: #444748;
                opacity: 1;
            }}

            .page-header {{
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                width: 100%;
                padding: 56px 48px 40px 48px;
                gap: 16px;
                background-color: #F4F4F2;
                box-sizing: border-box;
            }}

            .header-badge {{
                color: #0057FF;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 3px;
                text-transform: uppercase;
                margin: 0;
            }}

            .header-title {{
                color: #111111;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 44px;
                font-weight: 700;
                letter-spacing: -1px;
                margin: 0;
            }}

            .stepper-container {{
                display: flex;
                width: 100%;
                padding: 20px 48px;
                align-items: center;
                gap: 8px;
                background-color: #FFFFFF;
                box-sizing: border-box;
                border-bottom: none;
            }}

            .step-item {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .step-circle {{
                width: 24px;
                height: 24px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 600;
                color: #FFFFFF;
            }}

            .step-circle.completed {{ background-color: #2FA36B; }}
            .step-circle.active {{ background-color: #0057FF; }}
            .step-circle.pending {{ background-color: #E5E7EB; color: #444748; }}

            .step-text {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 13px;
                font-weight: 400;
                color: #111111;
            }}

            .step-text.active {{ color: #111111; font-weight: 700; }}

            .step-line {{
                width: 32px;
                height: 2px;
                background-color: #E5E7EB;
                margin: 0 4px;
            }}

            .step-line.completed {{ background-color: #2FA36B; }}

            .section-step-header {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 32px 48px 16px 48px;
                background-color: #FFFFFF;
            }}

            .section-step-header.spaced {{
                padding-top: 27px !important;
                padding-bottom: 0px !important;
            }}

            .section-step-title {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 16px;
                font-weight: 600;
                color: #111111;
                margin: 0;
            }}

            .upload-section-body {{
                display: flex;
                flex-direction: column;
                padding: 0 48px 0px 48px;
                background-color: #FFFFFF;
                width: 100%;
                box-sizing: border-box;
            }}

            .upload-box {{
                display: flex;
                width: 820px;
                height: 220px;
                padding: 40px 0;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                gap: 16px;
                border-radius: 12px;
                border: 2px dashed #C4C6CF;
                background-color: #FFFFFF;
                box-sizing: border-box;
                position: relative;
                transition: border-color 0.2s ease, background-color 0.2s ease;
                cursor: pointer;
            }}

            .upload-box:hover {{
                border-color: #0057FF;
                background-color: #F0F5FF;
            }}

            .upload-icon {{
                width: 56px;
                height: 56px;
                display: block;
                flex-shrink: 0;
            }}

            .upload-text-main {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 15px;
                font-weight: 500;
                color: #111111;
                text-align: center;
                margin: 0;
            }}

            .upload-text-sub {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 12.5px;
                font-weight: 400;
                color: #444748;
                text-align: center;
                margin: 0;
            }}

            .upload-btn {{
                display: flex;
                padding: 12px 20px;
                justify-content: center;
                align-items: center;
                gap: 8px;
                border-radius: 8px;
                background-color: #0057FF;
                color: #FFFFFF;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 13.5px;
                font-weight: 500;
                border: none;
                pointer-events: none;
            }}

            .analysis-grid-container {{
                display: flex;
                flex-direction: column;
                padding: 0px 48px 32px 48px;
                background-color: #FFFFFF;
                width: 100%;
                box-sizing: border-box;
            }}

            .analysis-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                width: 820px;
                margin-top: 19px;
            }}

            .analysis-card {{
                display: flex;
                flex-direction: column;
                padding: 16px;
                align-items: flex-start;
                gap: 12px;
                border-radius: 12px;
                border: 1.5px solid #C4C6CF;
                background-color: #FFFFFF;
                cursor: pointer;
                transition: all 0.2s ease;
                user-select: none;
                box-sizing: border-box;
                min-height: 140px;
            }}

            .analysis-card:hover {{ border-color: #0057FF; }}
            .analysis-card.selected {{ background-color: #F0F5FF; border: 1.5px solid #0057FF; }}
            .analysis-card.disabled-step, .module-card.disabled-step, .transversal-box.disabled-step {{
                opacity: 0.55;
                cursor: not-allowed !important;
                pointer-events: none;
            }}

            .card-icon-badge {{
                width: 36px;
                height: 36px;
                border-radius: 8px;
                background-color: #F3F4F6;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background-color 0.2s ease;
            }}

            .card-icon-img {{
                width: 18px;
                height: 18px;
                display: block;
                filter: brightness(0) opacity(0.7);
                transition: filter 0.2s ease;
            }}

            .analysis-card.selected .card-icon-badge {{ background-color: #0057FF; }}
            .analysis-card.selected .card-icon-img {{ filter: brightness(0) invert(1); }}

            .card-texts-wrap {{
                display: flex;
                flex-direction: column;
                gap: 4px;
                width: 100%;
            }}

            .card-title {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-weight: 600;
                color: #111111;
                margin: 0;
            }}

            .analysis-card.selected .card-title {{ color: #0057FF; }}

            .card-desc {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 12px;
                font-weight: 400;
                color: #5E6366;
                margin: 0;
                line-height: 1.35;
            }}

            .modules-section-container {{
                display: flex;
                flex-direction: column;
                padding: 0px 48px 32px 48px;
                background-color: #FFFFFF;
                width: 100%;
                box-sizing: border-box;
            }}

            .modules-subtitle {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 18px;
                font-weight: 700;
                color: #111111;
                margin: 16px 0 16px 0;
                letter-spacing: -0.2px;
            }}

            .modules-list {{
                display: flex;
                flex-direction: column;
                gap: 12px;
                width: 820px;
            }}

            .module-card {{
                display: flex;
                align-items: center;
                gap: 16px;
                width: 100%;
                padding: 16px 20px;
                border-radius: 12px;
                border: 1.5px solid #C4C6CF;
                background-color: #FFFFFF;
                cursor: pointer;
                transition: all 0.2s ease;
                user-select: none;
                box-sizing: border-box;
            }}

            .module-card:hover {{ border-color: #0057FF; }}
            .module-card.selected {{ background-color: #F0F5FF; border: 1.5px solid #0057FF; }}

            .custom-checkbox {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid #C4C6CF;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #FFFFFF;
                flex-shrink: 0;
                transition: all 0.2s ease;
            }}

            .custom-checkbox.checked {{ background-color: #0057FF; border-color: #0057FF; }}
            .custom-checkbox svg {{ width: 14px; height: 14px; fill: #FFFFFF; display: none; }}
            .custom-checkbox.checked svg {{ display: block; }}

            .module-badge {{
                width: 32px;
                height: 32px;
                border-radius: 8px;
                background-color: #0057FF;
                color: #FFFFFF;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-weight: 700;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }}

            .module-badge-master {{ background-color: #111111 !important; font-size: 16px !important; }}
            .module-card.selected .module-badge-master {{ background-color: #0057FF !important; }}

            .module-texts-wrap {{
                display: flex;
                flex-direction: column;
                gap: 2px;
                flex: 1;
            }}

            .module-title {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-weight: 600;
                color: #111111;
            }}

            .module-card.selected .module-title {{ color: #0057FF; }}
            .module-desc {{ font-family: 'Space Grotesk', sans-serif !important; font-size: 12.5px; color: #5E6366; }}

            .transversal-box {{
                display: flex;
                flex-direction: column;
                width: 820px;
                padding: 24px;
                gap: 16px;
                border-radius: 12px;
                background-color: #F4F4F2;
                margin-top: 16px;
                box-sizing: border-box;
            }}

            .transversal-title {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-weight: 700;
                color: #111111;
                margin: 0;
            }}

            .transversal-row {{ display: flex; align-items: center; gap: 10px; cursor: pointer; user-select: none; }}
            .transversal-icon {{ width: 20px; height: 20px; min-width: 20px; min-height: 20px; display: block; }}
            .transversal-text {{ font-family: 'Space Grotesk', sans-serif !important; font-size: 13.5px; font-weight: 500; color: #444748; }}

            .action-footer-container {{
                display: flex;
                width: 820px;
                padding: 20px 24px;
                justify-content: space-between;
                align-items: center;
                border-radius: 12px;
                border: 1.5px solid #C4C6CF;
                background-color: #FFFFFF;
                margin-top: 24px;
                margin-bottom: 8px;
                box-sizing: border-box;
            }}

            .btn-generar-analisis {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 24px;
                border-radius: 8px;
                background-color: #0057FF;
                color: #FFFFFF;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-weight: 600;
                border: none;
                cursor: pointer;
                transition: all 0.2s ease;
            }}

            .btn-generar-analisis:hover {{ opacity: 0.9; }}
            .btn-generar-analisis.btn-disabled {{
                background-color: #E5E7EB !important;
                color: #9CA3AF !important;
                cursor: not-allowed !important;
                pointer-events: none;
            }}

            .btn-generar-icon {{
                width: 18px;
                height: 18px;
                display: block;
                filter: brightness(0) invert(1);
            }}

            .btn-generar-analisis.btn-disabled .btn-generar-icon {{ filter: brightness(0) opacity(0.3); }}
            .action-footer-info {{ font-family: 'Space Grotesk', sans-serif !important; font-size: 13.5px; font-weight: 500; color: #111111; }}

            .footer-container {{
                display: flex;
                width: 100%;
                padding: 20px 48px;
                justify-content: space-between;
                align-items: center;
                background: #FFFFFF;
                border-top: 1px solid #C4C6CF;
                margin-top: auto;
                box-sizing: border-box;
            }}

            .footer-text {{ color: #444748; font-size: 12px; font-weight: 400; margin: 0; }}
            .footer-links {{ display: flex; gap: 20px; }}
            .footer-link {{ color: #0057FF; font-size: 12px; font-weight: 500; text-decoration: none; }}
            .footer-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="layout-container notranslate" translate="no">
            {sidebar_html}

            <main class="main-content" id="mainContent">
                <header class="topbar">
                    <div class="search-box">
                        <img src="{icon_search}" class="search-icon" alt="Buscar">
                        <input type="text" class="search-input" placeholder="Buscar análisis, reportes...">
                    </div>
                </header>

                <section class="page-header">
                    <span class="header-badge">DIAGNÓSTICO VISUAL ASISTIDO POR IA</span>
                    <h1 class="header-title">Nuevo análisis</h1>
                </section>

                <div class="stepper-container">
                    <div class="step-item">
                        <div class="step-circle {c1}">1</div>
                        <span class="step-text {t1}">Subir</span>
                    </div>
                    <div class="step-line {l1}"></div>
                    <div class="step-item">
                        <div class="step-circle {c2}">2</div>
                        <span class="step-text {t2}">Categoría</span>
                    </div>
                    <div class="step-line {l2}"></div>
                    <div class="step-item">
                        <div class="step-circle {c3}">3</div>
                        <span class="step-text {t3}">Módulos</span>
                    </div>
                    <div class="step-line {l3}"></div>
                    <div class="step-item">
                        <div class="step-circle {c4}">4</div>
                        <span class="step-text {t4}">Reporte</span>
                    </div>
                </div>

                <!-- PASO 1 -->
                <div class="section-step-header">
                    <div class="step-circle {c1}">1</div>
                    <h2 class="section-step-title">Subir imagen</h2>
                </div>

                <div class="upload-section-body">
                    <div class="upload-box" id="btnSubirBox">
                        <img src="{icon_frame}" class="upload-icon" alt="Upload">
                        <p class="upload-text-main" id="uploadTextMain">{texto_subida_main}</p>
                        <p class="upload-text-sub">{texto_subida_sub}</p>
                        <button class="upload-btn">{texto_subida_btn}</button>
                    </div>
                </div>

                <!-- PASO 2 -->
                <div class="section-step-header spaced">
                    <div class="step-circle {c2}">2</div>
                    <h2 class="section-step-title">Categoría de análisis</h2>
                </div>

                <div class="analysis-grid-container">
                    <div class="analysis-grid">
                        <div class="analysis-card {sel_semiotico} {clase_disabled_p2}" id="cardSemiotico">
                            <div class="card-icon-badge">
                                <img src="{icon_palette}" class="card-icon-img" alt="Semiótico">
                            </div>
                            <div class="card-texts-wrap">
                                <h3 class="card-title">Semiótico</h3>
                                <p class="card-desc">Sistema de marca completo</p>
                            </div>
                        </div>

                        <div class="analysis-card {sel_ui_ux} {clase_disabled_p2}" id="cardUiUx">
                            <div class="card-icon-badge">
                                <img src="{icon_touch}" class="card-icon-img" alt="UX/UI">
                            </div>
                            <div class="card-texts-wrap">
                                <h3 class="card-title">UX/UI</h3>
                                <p class="card-desc">Interfaces y experiencia digital</p>
                            </div>
                        </div>

                        <div class="analysis-card {sel_packaging} {clase_disabled_p2}" id="cardPackaging">
                            <div class="card-icon-badge">
                                <img src="{icon_inbox}" class="card-icon-img" alt="Packaging">
                            </div>
                            <div class="card-texts-wrap">
                                <h3 class="card-title">Packaging</h3>
                                <p class="card-desc">Empaque o envase</p>
                            </div>
                        </div>

                        <div class="analysis-card {sel_tipografia} {clase_disabled_p2}" id="cardTipografia">
                            <div class="card-icon-badge">
                                <img src="{icon_font}" class="card-icon-img" alt="Tipografía">
                            </div>
                            <div class="card-texts-wrap">
                                <h3 class="card-title">Tipografía</h3>
                                <p class="card-desc">Familias tipográficas y lettering</p>
                            </div>
                        </div>

                        <div class="analysis-card {sel_logotipo} {clase_disabled_p2}" id="cardLogotipo">
                            <div class="card-icon-badge">
                                <img src="{icon_watermark}" class="card-icon-img" alt="Logotipo">
                            </div>
                            <div class="card-texts-wrap">
                                <h3 class="card-title">Logotipo</h3>
                                <p class="card-desc">Marca e isotipo</p>
                            </div>
                        </div>

                        <div class="analysis-card {sel_afiche} {clase_disabled_p2}" id="cardAfiche">
                            <div class="card-icon-badge">
                                <img src="{icon_crop}" class="card-icon-img" alt="Afiche">
                            </div>
                            <div class="card-texts-wrap">
                                <h3 class="card-title">Afiche</h3>
                                <p class="card-desc">Poster o pieza gráfica</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- PASO 3 -->
                <div class="section-step-header spaced">
                    <div class="step-circle {c3}">3</div>
                    <h2 class="section-step-title">Módulos de análisis</h2>
                </div>

                <div class="modules-section-container">
                    <h3 class="modules-subtitle">Módulos de análisis disponibles</h3>
                    <div class="modules-list">
                        {html_modulos_cards}
                    </div>

                    <div class="transversal-box {clase_disabled_p3}">
                        <h4 class="transversal-title">Módulos transversales — activos en todas las categorías</h4>
                        
                        <div class="transversal-row" id="rowTransversalWcag">
                            <div class="custom-checkbox {wcag_checked}">
                                <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                            </div>
                            <img src="{icon_access}" class="transversal-icon" alt="Accesibilidad">
                            <span class="transversal-text">Detector de accesibilidad WCAG 2.1</span>
                        </div>

                        <div class="transversal-row" id="rowTransversalHistoricas">
                            <div class="custom-checkbox {hist_checked}">
                                <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                            </div>
                            <span class="transversal-text">Referencias históricas</span>
                        </div>
                    </div>

                    <div class="action-footer-container">
                        <button class="btn-generar-analisis {clase_btn_generar_dis}" id="btnGenerarAnalisis">
                            <img src="{icon_star}" class="btn-generar-icon" alt="Star">
                            <span>Generar análisis</span>
                        </button>
                        <span class="action-footer-info">{total_modulos_activos} módulos seleccionados · tiempo estimado {tiempo_min}–{tiempo_max} s</span>
                    </div>
                </div>

                <footer class="footer-container notranslate" translate="no">
                    <p class="footer-text">© 2026 Indexal - Análisis visual asistido por IA - Todos los derechos reservados</p>
                    <div class="footer-links">
                        <a href="javascript:void(0)" class="footer-link">Términos y condiciones</a>
                        <a href="javascript:void(0)" class="footer-link">Política de privacidad</a>
                    </div>
                </footer>
            </main>
        </div>

        <script>
            const parentDoc = window.parent.document;
            const paso2Permitido = {'true' if paso2_habilitado else 'false'};
            const paso3Permitido = {'true' if paso3_habilitado else 'false'};
            const puedeGenerar = {'true' if puede_generar else 'false'};
            
            function irAHome() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 0) allButtons[0].click();
            }}
            document.getElementById('btnSidebarLogo').addEventListener('click', irAHome);
            document.getElementById('btnMenuInicio').addEventListener('click', irAHome);

            document.getElementById('btnMenuGaleria').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 1) allButtons[1].click();
            }});

            document.getElementById('btnMenuReportes').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 2) allButtons[2].click();
            }});

            // ----------------------------------------------------
            // CONEXIÓN DIRECTA Y ROBUSTA DE SUBIDA
            // ----------------------------------------------------
            const uploadBox = document.getElementById('btnSubirBox');
            
            // 1. Click clásico para abrir el explorador de archivos
            uploadBox.addEventListener('click', function() {{
                const fileInput = parentDoc.querySelector('div[data-testid="stFileUploader"] input[type="file"]');
                if (fileInput) fileInput.click();
            }});

            // 2. Feedback visual y prevención al arrastrar sobre la caja
            ['dragenter', 'dragover'].forEach(eventName => {{
                uploadBox.addEventListener(eventName, function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    uploadBox.style.borderColor = '#0057FF';
                    uploadBox.style.backgroundColor = '#F0F5FF';
                }});
            }});

            ['dragleave', 'dragend'].forEach(eventName => {{
                uploadBox.addEventListener(eventName, function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    uploadBox.style.borderColor = '#C4C6CF';
                    uploadBox.style.backgroundColor = '#FFFFFF';
                }});
            }});

            // 3. Captura del archivo al soltarlo (Drop)
            uploadBox.addEventListener('drop', function(e) {{
                e.preventDefault();
                e.stopPropagation();
                uploadBox.style.borderColor = '#C4C6CF';
                uploadBox.style.backgroundColor = '#FFFFFF';

                const dt = e.dataTransfer;
                const files = dt ? dt.files : null;

                if (files && files.length > 0) {{
                    const fileInput = parentDoc.querySelector('div[data-testid="stFileUploader"] input[type="file"]');
                    if (fileInput) {{
                        // Transferir archivo al input file nativo de Streamlit
                        const dataTransferObj = new DataTransfer();
                        dataTransferObj.items.add(files[0]);
                        fileInput.files = dataTransferObj.files;

                        // Disparar evento para que Streamlit detecte el archivo
                        fileInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            }});

            // Categorías (Paso 2)
            if (paso2Permitido) {{
                document.getElementById('cardSemiotico').addEventListener('click', function() {{
                    const allButtons = parentDoc.querySelectorAll('div.stButton button');
                    if (allButtons.length > 3) allButtons[3].click();
                }});
                document.getElementById('cardUiUx').addEventListener('click', function() {{
                    const allButtons = parentDoc.querySelectorAll('div.stButton button');
                    if (allButtons.length > 4) allButtons[4].click();
                }});
                document.getElementById('cardPackaging').addEventListener('click', function() {{
                    const allButtons = parentDoc.querySelectorAll('div.stButton button');
                    if (allButtons.length > 5) allButtons[5].click();
                }});
                document.getElementById('cardTipografia').addEventListener('click', function() {{
                    const allButtons = parentDoc.querySelectorAll('div.stButton button');
                    if (allButtons.length > 6) allButtons[6].click();
                }});
                document.getElementById('cardLogotipo').addEventListener('click', function() {{
                    const allButtons = parentDoc.querySelectorAll('div.stButton button');
                    if (allButtons.length > 7) allButtons[7].click();
                }});
                document.getElementById('cardAfiche').addEventListener('click', function() {{
                    const allButtons = parentDoc.querySelectorAll('div.stButton button');
                    if (allButtons.length > 8) allButtons[8].click();
                }});
            }}

            // Módulos (Paso 3)
            if (paso3Permitido) {{
                const elMaster = document.getElementById('cardMod_master');
                if (elMaster) {{
                    elMaster.addEventListener('click', function() {{
                        const allButtons = parentDoc.querySelectorAll('div.stButton button');
                        if (allButtons.length > 10) allButtons[10].click();
                    }});
                }}

                { "".join([f"""
                const el_{i} = document.getElementById('cardMod_{i}');
                if (el_{i}) {{
                    el_{i}.addEventListener('click', function() {{
                        const allButtons = parentDoc.querySelectorAll('div.stButton button');
                        if (allButtons.length > {11 + i}) allButtons[{11 + i}].click();
                    }});
                }}
                """ for i in range(len(lista_modulos_activa))]) }

                const elWcag = document.getElementById('rowTransversalWcag');
                if (elWcag) {{
                    elWcag.addEventListener('click', function() {{
                        const allButtons = parentDoc.querySelectorAll('div.stButton button');
                        if (allButtons.length > {11 + len(lista_modulos_activa)}) allButtons[{11 + len(lista_modulos_activa)}].click();
                    }});
                }}

                const elHist = document.getElementById('rowTransversalHistoricas');
                if (elHist) {{
                    elHist.addEventListener('click', function() {{
                        const allButtons = parentDoc.querySelectorAll('div.stButton button');
                        if (allButtons.length > {12 + len(lista_modulos_activa)}) allButtons[{12 + len(lista_modulos_activa)}].click();
                    }});
                }}
            }}

            // Generar Análisis
            if (puedeGenerar) {{
                const btnGen = document.getElementById('btnGenerarAnalisis');
                if (btnGen) {{
                    btnGen.addEventListener('click', function() {{
                        const allButtons = parentDoc.querySelectorAll('div.stButton button');
                        if (allButtons.length > {13 + len(lista_modulos_activa)}) allButtons[{13 + len(lista_modulos_activa)}].click();
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """

    components.html(analizar_html, height=2030, scrolling=False)

    # -------------------------------------------------------------------------
    # RECEPTOR NATIVO DE ARCHIVO (OCULTO VISUALMENTE, SIN BASE64 NI LOOPS)
    # -------------------------------------------------------------------------
    archivo_subido = st.file_uploader(
        "hidden_uploader",
        type=["png", "jpg", "jpeg", "webp"],
        key="uploader_nativo_indexal",
        label_visibility="collapsed",
    )

    if archivo_subido is not None:
        # Guardado físico único e instantáneo
        if not st.session_state["imagen_cargada"] or st.session_state.get("nombre_imagen") != archivo_subido.name:
            carpeta_destino = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "imagenes"))
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino, exist_ok=True)

            nombre_guardado = f"{int(time.time())}_{archivo_subido.name}"
            ruta_guardado = os.path.join(carpeta_destino, nombre_guardado)

            with open(ruta_guardado, "wb") as f:
                f.write(archivo_subido.getbuffer())

            st.session_state["imagen_cargada"] = True
            st.session_state["nombre_imagen"] = archivo_subido.name
            st.session_state["archivo_guardado_path"] = nombre_guardado
            st.session_state["paso_actual"] = max(st.session_state["paso_actual"], 2)
            st.rerun()

    # Botones ocultos de navegación y estado
    botones_modulos_count = len(lista_modulos_activa)
    columnas_totales = st.columns(14 + botones_modulos_count)

    # 1. Navegación del Menú Lateral (0, 1, 2)
    with columnas_totales[0]:
        if st.button("\u200b", key="btn_hidden_analizar_home"):
            st.session_state["pantalla_actual"] = "home"
            st.rerun()
    with columnas_totales[1]:
        if st.button("\u200b", key="btn_hidden_analizar_galeria"):
            st.session_state["pantalla_actual"] = "galeria"
            st.rerun()
    with columnas_totales[2]:
        if st.button("\u200b", key="btn_hidden_analizar_reportes"):
            st.session_state["pantalla_actual"] = "reportes"
            st.rerun()

    # 2. Selección de Categorías (Paso 2: 3 a 8)
    with columnas_totales[3]:
        if st.button("\u200b", key="btn_tipo_semiotico"):
            if st.session_state["paso_actual"] >= 2:
                st.session_state["tipo_analisis"] = "semiotico"
                st.session_state["paso_actual"] = max(
                    st.session_state["paso_actual"], 3
                )
                st.rerun()
    with columnas_totales[4]:
        if st.button("\u200b", key="btn_tipo_ui_ux"):
            if st.session_state["paso_actual"] >= 2:
                st.session_state["tipo_analisis"] = "ui_ux"
                st.session_state["paso_actual"] = max(
                    st.session_state["paso_actual"], 3
                )
                st.rerun()
    with columnas_totales[5]:
        if st.button("\u200b", key="btn_tipo_packaging"):
            if st.session_state["paso_actual"] >= 2:
                st.session_state["tipo_analisis"] = "packaging"
                st.session_state["paso_actual"] = max(
                    st.session_state["paso_actual"], 3
                )
                st.rerun()
    with columnas_totales[6]:
        if st.button("\u200b", key="btn_tipo_tipografia"):
            if st.session_state["paso_actual"] >= 2:
                st.session_state["tipo_analisis"] = "tipografia"
                st.session_state["paso_actual"] = max(
                    st.session_state["paso_actual"], 3
                )
                st.rerun()
    with columnas_totales[7]:
        if st.button("\u200b", key="btn_tipo_logotipo"):
            if st.session_state["paso_actual"] >= 2:
                st.session_state["tipo_analisis"] = "logotipo"
                st.session_state["paso_actual"] = max(
                    st.session_state["paso_actual"], 3
                )
                st.rerun()
    with columnas_totales[8]:
        if st.button("\u200b", key="btn_tipo_afiche"):
            if st.session_state["paso_actual"] >= 2:
                st.session_state["tipo_analisis"] = "afiche"
                st.session_state["paso_actual"] = max(
                    st.session_state["paso_actual"], 3
                )
                st.rerun()

    # 3. (Espacio reservado para mantener índices)
    with columnas_totales[9]:
        st.button("\u200b", key="btn_dummy_slot")

    # 4. Checkbox Maestro (Paso 3: 10)
    with columnas_totales[10]:
        if st.button("\u200b", key="btn_toggle_modulo_master"):
            if st.session_state["paso_actual"] >= 3:
                if todos_seleccionados:
                    st.session_state["modulos_seleccionados"] = []
                else:
                    st.session_state["modulos_seleccionados"] = todos_los_ids[:]
                st.rerun()

    # 5. Checkboxes individuales (Paso 3: 11 a 11 + N)
    for i, mod in enumerate(lista_modulos_activa):
        with columnas_totales[11 + i]:
            if st.button("\u200b", key=f"btn_toggle_modulo_{mod['id']}"):
                if st.session_state["paso_actual"] >= 3:
                    mod_id = mod["id"]
                    if mod_id in st.session_state["modulos_seleccionados"]:
                        st.session_state["modulos_seleccionados"].remove(mod_id)
                    else:
                        st.session_state["modulos_seleccionados"].append(mod_id)
                    st.rerun()

    # 6. Módulos transversales
    idx_transversal = 11 + botones_modulos_count
    with columnas_totales[idx_transversal]:
        if st.button("\u200b", key="btn_toggle_transversal_wcag"):
            if st.session_state["paso_actual"] >= 3:
                st.session_state["transversal_wcag"] = not st.session_state[
                    "transversal_wcag"
                ]
                st.rerun()

    with columnas_totales[idx_transversal + 1]:
        if st.button("\u200b", key="btn_toggle_transversal_hist"):
            if st.session_state["paso_actual"] >= 3:
                st.session_state["transversal_historicas"] = not (
                    st.session_state["transversal_historicas"]
                )
                st.rerun()

    # 7. Botón disparador de Generar Análisis -> Conexión con el Orquestador
    with columnas_totales[idx_transversal + 2]:
        if st.button("\u200b", key="btn_hidden_generar_analisis"):
            if puede_generar:
                st.session_state["paso_actual"] = 4

                nombre_archivo = st.session_state.get("archivo_guardado_path", "")
                carpeta_destino = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "imagenes"))
                ruta_completa_imagen = os.path.join(carpeta_destino, nombre_archivo)

                cat_str = st.session_state.get("tipo_analisis", "semiotico")
                cat_id = MAPA_CATEGORIA_A_ID.get(cat_str, 0)

                modulos_a_ejecutar = list(st.session_state.get("modulos_seleccionados", []))
                if st.session_state.get("transversal_wcag"):
                    modulos_a_ejecutar.append("transversal_wcag")
                if st.session_state.get("transversal_historicas"):
                    modulos_a_ejecutar.append("transversal_historicas")

                mapa_funciones = globals().get("MAPA_GLOBAL_FUNCIONES", {})
                master_json = compilar_datos_reporte(
                    imagen_path=ruta_completa_imagen,
                    mapa_global=mapa_funciones,
                    lista_cb_seleccionados=modulos_a_ejecutar,
                    categoria_id=cat_id,
                )

                st.session_state["ultimo_reporte_json"] = master_json

                nombre_img_original = st.session_state.get("nombre_imagen", "Analisis")
                nombre_limpio = os.path.splitext(nombre_img_original)[0]
                titulo_rep = master_json.get("metadata", {}).get("titulo_reporte", "Diagnóstico")

                nuevo_rep = {
                    "id": f"rep_{len(st.session_state.get('reportes_sesion', [])) + 1}",
                    "archivo": f"Diagnóstico_{nombre_limpio}_indexal.pdf",
                    "tipo": titulo_rep,
                    "modulos_analizados": total_modulos_activos,
                    "timestamp": time.time(),
                    "json_data": master_json,
                }

                if "reportes_sesion" not in st.session_state:
                    st.session_state["reportes_sesion"] = []
                st.session_state["reportes_sesion"].append(nuevo_rep)

                st.session_state["pantalla_actual"] = "reportes"
                st.rerun()

# -----------------------------------------------------------------
# PANTALLA 5: REPORTES
# -----------------------------------------------------------------

def render_reportes():
    # 1. Lista de reportes de la sesión
    if "reportes_sesion" not in st.session_state:
        st.session_state["reportes_sesion"] = []

    # 2. Renderizado del reporte con Jinja2 usando el Master JSON real
    ultimo_json = st.session_state.get("ultimo_reporte_json")
    
    if ultimo_json and "metadata" in ultimo_json and "bloques" in ultimo_json:
        try:
            contenido_template = renderizar_reporte_html(ultimo_json)
        except Exception as e:
            contenido_template = f"""
            <div style="padding: 30px; color: #DC2626; background: #FEF2F2; border-radius: 8px; font-family: sans-serif;">
                <h3 style="margin-top: 0;">Error al procesar la plantilla HTML:</h3>
                <pre>{e}</pre>
            </div>
            """
    else:
        contenido_template = """
        <div style="padding: 40px; text-align: center; color: #444748;">
            <h2 style="color: #111111; margin-bottom: 12px;">No hay análisis generado</h2>
            <p>Generá un análisis en la pestaña <b>Nuevo análisis</b> para visualizar el informe completo aquí.</p>
        </div>
        """

    # Inyección de estilos base
    st.markdown(
        """
        <script>
            if (!parent.document.getElementById('font-space-grotesk')) {
                const link = parent.document.createElement('link');
                link.id = 'font-space-grotesk';
                link.rel = 'stylesheet';
                link.href = 'https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap';
                parent.document.head.appendChild(link);
            }
        </script>

        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp, .stApp * {
            font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        }

        .stApp {
            background-color: #F8F9FA !important;
        }

        header[data-testid="stHeader"], header, .stAppHeader { 
            display: none !important; 
            height: 0px !important; 
            visibility: hidden !important;
        }

        #MainMenu, footer { visibility: hidden; }

        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewBlockContainer"],
        div[data-testid="stMainBlockContainer"],
        section.main, .stMain, .main {
            padding: 0px !important;
            margin: 0px !important;
            min-height: auto !important;
            display: block !important;
            background-color: #F8F9FA !important;
        }

        .block-container, div[data-testid="block-container"] {
            max-width: 100% !important;
            width: 100% !important;
            padding: 0px !important;
            margin: 0px !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0px !important;
        }

        div.stButton, div[data-testid="stElementContainer"]:has(div.stButton),
        div[data-testid="stDownloadButton"], div[data-testid="stElementContainer"]:has(div[data-testid="stDownloadButton"]) {
            display: none !important;
            visibility: hidden !important;
            position: absolute !important;
            top: -9999px !important;
            left: -9999px !important;
            width: 0px !important;
            height: 0px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            overflow: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 3. Carga de SVGs
    img_logo = cargar_svg_base64("assets/iconos/logo_x.svg")
    icon_home = cargar_svg_base64("assets/iconos/home.svg")
    icon_note_add = cargar_svg_base64("assets/iconos/note_add.svg")
    icon_photo_lib = cargar_svg_base64("assets/iconos/photo_library.svg")
    icon_assessment = cargar_svg_base64("assets/iconos/assessment.svg")
    icon_settings = cargar_svg_base64("assets/iconos/settings.svg")
    icon_print = cargar_svg_base64("assets/iconos/print.svg")
    icon_download = cargar_svg_base64("assets/iconos/download.svg")

    sidebar_html = obtener_sidebar_html(
        item_activo="reportes",
        img_logo=img_logo,
        icon_home=icon_home,
        icon_note_add=icon_note_add,
        icon_photo_lib=icon_photo_lib,
        icon_assessment=icon_assessment,
        icon_settings=icon_settings,
    )

    # 4. Verificación de reporte activo
    hay_reporte_activo = bool(ultimo_json and "metadata" in ultimo_json and "bloques" in ultimo_json)

    # 5. Mapeo dinámico de Categoría y Módulos
    if hay_reporte_activo:
        MAPA_CATEGORIAS = {
            "semiotico": "Semiótico",
            "ui_ux": "UX / UI",
            "packaging": "Packaging",
            "tipografia": "Tipografía",
            "logotipo": "Logotipo",
            "afiche": "Afiche",
        }
        tipo_elegido_key = st.session_state.get("tipo_analisis", "semiotico")
        categoria_txt = MAPA_CATEGORIAS.get(tipo_elegido_key, "Semiótico").upper()

        MAPA_LETRAS_MODULOS = {
            "composicion_visual": ("A", "Composición visual"),
            "paleta_cromatica": ("B", "Paleta cromática"),
            "iluminacion": ("C", "Iluminación"),
            "semiotica_imagen": ("D", "Semiótica de la imagen"),
            "retorica_visual": ("E", "Retórica visual"),
            "contexto_denotacion": ("F", "Contexto y denotación"),
        }

        modulos_sel = st.session_state.get("modulos_seleccionados", [])
        total_modulos_posibles = len(MAPA_LETRAS_MODULOS)

        if len(modulos_sel) == total_modulos_posibles:
            modulo_txt = "COMPLETO (MÓDULOS A–F)"
        elif len(modulos_sel) == 0:
            modulo_txt = "TRANSVERSALES"
        elif len(modulos_sel) == 1:
            mod_id = modulos_sel[0]
            letra, nombre = MAPA_LETRAS_MODULOS.get(
                mod_id, ("A", mod_id.replace("_", " ").title())
            )
            modulo_txt = f"{letra} — {nombre.upper()}"
        else:
            letras_activas = sorted(
                [
                    MAPA_LETRAS_MODULOS[m][0]
                    for m in modulos_sel
                    if m in MAPA_LETRAS_MODULOS
                ]
            )
            modulo_txt = f"MÓDULOS {', '.join(letras_activas)}"

        transversales_activos = []
        if st.session_state.get("transversal_wcag", False):
            transversales_activos.append("WCAG")
        if st.session_state.get("transversal_historicas", False):
            transversales_activos.append("HISTÓRICO")

        if transversales_activos and len(modulos_sel) < total_modulos_posibles:
            modulo_txt += f" + {'/'.join(transversales_activos)}"
    else:
        categoria_txt = "-"
        modulo_txt = "-"

    def calcular_tiempo_relativo(timestamp):
        diff = int(time.time() - timestamp)
        if diff < 60:
            return "Hace un momento"
        elif diff < 3600:
            return f"Hace {diff // 60} min"
        else:
            return f"Hace {diff // 3600} h"

    # 6. Construcción del bloque de Reportes de la Sesión
    lista_reportes = st.session_state["reportes_sesion"]
    hay_reportes = len(lista_reportes) > 0

    if hay_reportes:
        html_items_sesion = ""
        for idx, rep in enumerate(lista_reportes):
            tiempo_relativo = calcular_tiempo_relativo(
                rep.get("timestamp", time.time())
            )
            html_items_sesion += f"""
            <div class="session-report-row">
                <div class="session-report-left">
                    <div class="session-file-badge">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                    </div>
                    <div class="session-file-info">
                        <span class="session-file-title">{rep['archivo']}</span>
                        <span class="session-file-desc">{rep['tipo']} · {rep['modulos_analizados']} módulos · {tiempo_relativo}</span>
                    </div>
                </div>
                <button class="session-download-btn" id="btnDownloadRow_{idx}">
                    <img src="{icon_download}" class="session-download-icon" alt="Descargar">
                </button>
            </div>
            """

        html_seccion_historial = f"""
        <div class="session-history-container">
            <h3 class="session-history-title">Reportes de esta sesión</h3>
            <p class="session-history-subtitle">Los PDF generados quedan disponibles solo mientras esta pestaña esté activa — no hay base de datos ni login.</p>
            <div class="session-reports-list">
                {html_items_sesion}
            </div>
        </div>
        """
    else:
        html_seccion_historial = ""

    pdf_bytes_actual = None
    nombre_pdf_actual = "Diagnostico_indexal.pdf"
    pdf_generado_exitosamente = False
    
    if ultimo_json and "metadata" in ultimo_json:
        try:
            ruta_temporal_pdf = os.path.join("assets", "reporte_temp.pdf")
            generar_reporte_pdf(ultimo_json, ruta_temporal_pdf)
            with open(ruta_temporal_pdf, "rb") as f:
                pdf_bytes_actual = f.read()
            nom_img = os.path.splitext(os.path.basename(ultimo_json.get("metadata", {}).get("imagen_path", "Analisis")))[0]
            nombre_pdf_actual = f"Diagnostico_{nom_img}_indexal.pdf"
            pdf_generado_exitosamente = True
        except Exception as e:
            print(f"Error generando PDF para descarga: {e}")
            pdf_generado_exitosamente = False

    reportes_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Space Grotesk', sans-serif !important;
            }}

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background-color: #F8F9FA !important;
                width: 100% !important;
                min-height: 100vh !important;
            }}

            .layout-container {{
                display: flex;
                width: 100%;
                min-height: 100vh;
            }}

            .sidebar {{
                width: 240px;
                min-width: 240px;
                background-color: #FFFFFF;
                border-right: 1px solid #C4C6CF;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                box-sizing: border-box;
                align-self: stretch;
            }}

            .sidebar-brand {{
                display: flex;
                width: 100%;
                height: 76px;
                padding: 0 20px;
                align-items: center;
                gap: 12px;
                background-color: #FFFFFF;
                border-bottom: 1px solid #C4C6CF;
                box-sizing: border-box;
                cursor: pointer;
                user-select: none;
                transition: opacity 0.2s ease;
            }}

            .sidebar-brand:hover {{ opacity: 0.8; }}

            .sidebar-logo-img {{
                width: 32px;
                height: 32px;
                min-width: 32px;
                min-height: 32px;
                display: block;
                flex-shrink: 0;
                filter: brightness(0);
            }}

            .sidebar-brand-text {{
                color: #111111;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 17px;
                font-weight: 700;
                line-height: normal;
                letter-spacing: 0.5px;
            }}

            .nav-label-wrap {{
                display: flex;
                width: 100%;
                padding: 20px 20px 4px 20px;
                flex-direction: column;
                align-items: flex-start;
                background-color: #FFFFFF;
                box-sizing: border-box;
            }}

            .menu-title {{
                color: #444748;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 10px;
                font-style: normal;
                font-weight: 700;
                line-height: normal;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin: 0;
                user-select: none;
            }}

            .nav-items-wrapper {{
                display: flex;
                flex-direction: column;
                width: 100%;
                padding: 0 16px 16px 16px;
                gap: 4px;
                box-sizing: border-box;
            }}

            .nav-item-btn {{
                display: flex;
                align-items: center;
                gap: 12px;
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: transparent;
                cursor: pointer;
                text-decoration: none;
                box-sizing: border-box;
                transition: background-color 0.15s ease;
            }}

            .nav-item-btn:hover {{ background-color: #F3F4F6; }}
            .nav-item-btn.active {{ background-color: #E6EDFF; }}

            .nav-icon-img {{
                width: 16px;
                height: 16px;
                min-width: 16px;
                min-height: 16px;
                display: block;
                flex-shrink: 0;
            }}

            .nav-item-text {{
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 14px;
                font-weight: 400;
                line-height: normal;
                color: #444748;
                flex: 1 0 0;
                text-align: left;
            }}

            .nav-item-btn.active .nav-item-text {{
                color: #0057FF;
                font-weight: 500;
            }}

            .main-content {{
                flex: 1;
                display: flex;
                flex-direction: column;
                background-color: #F8F9FA;
                min-width: 0;
                min-height: 100vh;
            }}

            .top-stepper-bar {{
                display: flex;
                width: 100%;
                padding: 24px 48px 12px 48px;
                align-items: center;
                background-color: #F8F9FA;
                box-sizing: border-box;
            }}

            .stepper-container {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .step-item {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .step-circle {{
                width: 22px;
                height: 22px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                font-weight: 700;
                color: #FFFFFF;
            }}

            .step-circle.completed {{ background-color: #2FA36B; }}
            .step-circle.active {{ background-color: #0057FF; }}

            .step-text {{
                font-size: 13px;
                font-weight: 500;
                color: #111111;
            }}

            .step-text.active {{
                font-weight: 700;
                color: #111111;
            }}

            .step-line {{
                width: 28px;
                height: 2px;
                margin: 0 4px;
            }}

            .step-line.completed {{ background-color: #2FA36B; }}

            .report-main-header {{
                display: flex;
                width: 100%;
                padding: 16px 48px 24px 48px;
                justify-content: space-between;
                align-items: flex-end;
                background-color: #F8F9FA;
                box-sizing: border-box;
            }}

            .header-info-wrap {{
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                gap: 6px;
            }}

            .breadcrumb-text {{
                font-size: 12.5px;
                font-weight: 500;
                color: #5E6366;
                margin: 0;
            }}

            .report-heading {{
                color: #111111;
                font-size: 32px;
                font-weight: 700;
                line-height: normal;
                letter-spacing: -0.8px;
                margin: 2px 0 6px 0;
            }}

            .report-meta-row {{
                display: flex;
                align-items: center;
                gap: 20px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                color: #5E6366;
                text-transform: uppercase;
            }}

            .report-meta-val {{
                color: #0057FF;
                font-weight: 700;
            }}

            .btn-export-pdf {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 22px;
                border-radius: 8px;
                background-color: #080D1A;
                color: #FFFFFF;
                font-size: 13.5px;
                font-weight: 600;
                border: none;
                cursor: pointer;
                transition: opacity 0.2s ease, transform 0.1s ease;
                user-select: none;
            }}

            .btn-export-pdf:hover {{ opacity: 0.9; }}
            .btn-export-pdf:active {{ transform: scale(0.98); }}

            .btn-export-icon {{
                width: 16px;
                height: 16px;
                display: block;
                filter: brightness(0) invert(1);
            }}

            .btn-export-pdf.disabled {{
                background-color: #E5E7EB !important;
                color: #9CA3AF !important;
                cursor: not-allowed !important;
                pointer-events: none !important;
            }}

            .btn-export-pdf.disabled .btn-export-icon {{
                filter: brightness(0) opacity(0.3) !important;
            }}

            .report-sheet-container {{
                display: flex;
                padding: 0 48px 24px 48px;
                width: 100%;
                box-sizing: border-box;
            }}

            .report-sheet-card {{
                width: 100%;
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1.5px solid #C4C6CF;
                padding: 32px;
                box-sizing: border-box;
                overflow-x: auto;
            }}

            .feedback-section-container {{
                display: flex;
                padding: 0 48px 24px 48px;
                width: 100%;
                box-sizing: border-box;
            }}

            .feedback-card {{
                width: 100%;
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1.5px solid #C4C6CF;
                padding: 24px 28px;
                display: flex;
                flex-direction: column;
                gap: 16px;
                box-sizing: border-box;
            }}

            .feedback-header {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .feedback-icon {{
                width: 18px;
                height: 18px;
                fill: #111111;
                display: block;
                flex-shrink: 0;
            }}

            .feedback-title {{
                font-size: 15px;
                font-weight: 700;
                color: #111111;
                margin: 0;
            }}

            .feedback-badge {{
                font-size: 10px;
                font-weight: 700;
                color: #5E6366;
                background-color: #ECEEEF;
                padding: 2px 6px;
                border-radius: 4px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }}

            .feedback-subtitle {{
                font-size: 13px;
                color: #444748;
                margin: -6px 0 0 0;
                font-weight: 400;
            }}

            .feedback-textarea {{
                width: 100%;
                min-height: 80px;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                background-color: #F4F4F2;
                padding: 12px 14px;
                font-size: 13.5px;
                color: #111111;
                resize: vertical;
                outline: none;
                box-sizing: border-box;
                font-family: 'Space Grotesk', sans-serif !important;
            }}

            .feedback-textarea:focus {{
                border-color: #0057FF;
                background-color: #FFFFFF;
            }}

            .feedback-textarea::placeholder {{
                color: #8C9093;
            }}

            .feedback-row-inputs {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}

            .feedback-email-input {{
                width: 260px;
                height: 38px;
                border-radius: 8px;
                border: 1px solid #C4C6CF;
                background-color: #FFFFFF;
                padding: 0 12px;
                font-size: 13px;
                color: #111111;
                outline: none;
                box-sizing: border-box;
                font-family: 'Space Grotesk', sans-serif !important;
            }}

            .feedback-email-input:focus {{
                border-color: #0057FF;
            }}

            .feedback-email-input::placeholder {{
                color: #8C9093;
            }}

            .feedback-email-hint {{
                font-size: 12px;
                color: #8C9093;
                margin: 0;
            }}

            .btn-send-feedback {{
                width: fit-content;
                padding: 10px 20px;
                border-radius: 8px;
                background-color: #080D1A;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                border: none;
                cursor: pointer;
                transition: opacity 0.2s ease;
            }}

            .btn-send-feedback:hover {{ opacity: 0.85; }}

            .session-history-container {{
                display: flex;
                flex-direction: column;
                padding: 0 48px 24px 48px;
                width: 100%;
                box-sizing: border-box;
                gap: 8px;
            }}

            .session-history-title {{
                font-size: 18px;
                font-weight: 700;
                color: #111111;
                margin: 0;
                letter-spacing: -0.3px;
            }}

            .session-history-subtitle {{
                font-size: 13px;
                color: #5E6366;
                margin: 0 0 8px 0;
                font-weight: 400;
            }}

            .session-reports-list {{
                display: flex;
                flex-direction: column;
                gap: 12px;
                width: 100%;
            }}

            .session-report-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 16px 20px;
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1.5px solid #C4C6CF;
                box-sizing: border-box;
                transition: border-color 0.2s ease;
            }}

            .session-report-row:hover {{
                border-color: #0057FF;
            }}

            .session-report-left {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}

            .session-file-badge {{
                width: 36px;
                height: 36px;
                border-radius: 8px;
                background-color: #F4F4F2;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }}

            .session-file-badge svg {{
                width: 18px;
                height: 18px;
                fill: #5E6366;
            }}

            .session-file-info {{
                display: flex;
                flex-direction: column;
                gap: 2px;
            }}

            .session-file-title {{
                font-size: 14px;
                font-weight: 600;
                color: #111111;
            }}

            .session-file-desc {{
                font-size: 12.5px;
                color: #5E6366;
            }}

            .session-download-btn {{
                width: 36px;
                height: 36px;
                border-radius: 8px;
                background-color: #F4F4F2;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background-color 0.2s ease;
            }}

            .session-download-btn:hover {{
                background-color: #E6EDFF;
            }}

            .session-download-icon {{
                width: 18px;
                height: 18px;
                display: block;
                filter: brightness(0) opacity(0.65);
                transition: filter 0.2s ease;
            }}

            .footer-container {{
                display: flex;
                width: 100%;
                padding: 20px 48px;
                justify-content: space-between;
                align-items: center;
                background: #FFFFFF;
                border-top: 1px solid #C4C6CF;
                margin-top: auto;
                box-sizing: border-box;
            }}

            .footer-text {{
                color: #444748;
                font-size: 12px;
                font-weight: 400;
                margin: 0;
            }}

            .footer-links {{ display: flex; gap: 20px; }}

            .footer-link {{
                color: #0057FF;
                font-size: 12px;
                font-weight: 500;
                text-decoration: none;
            }}

            .footer-link:hover {{ text-decoration: underline; }}
        
            /* --- MODALES FLOTANTES POP-UP --- */
            .modal-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(17, 17, 17, 0.45);
                backdrop-filter: blur(2px);
                display: flex;
                align-items: flex-start;
                justify-content: center;
                z-index: 999999;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.2s ease, visibility 0.2s ease;
            }}

            .modal-overlay.active {{
                opacity: 1;
                visibility: visible;
            }}

            .popup-card {{
                position: relative;
                width: 360px;
                max-width: 90%;
                border-radius: 16px;
                padding: 28px 24px 24px 24px;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                box-sizing: border-box;
                transform: scale(0.95);
                transition: transform 0.2s ease;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            }}

            .modal-overlay.active .popup-card {{
                transform: scale(1);
            }}

            .popup-card.success {{
                background-color: #E6F7ED;
                border: 1.5px solid #2FA36B;
            }}

            .popup-card.error {{
                background-color: #FDF0F2;
                border: 1.5px solid #C5445B;
            }}

            .popup-close-btn {{
                position: absolute;
                top: 14px;
                right: 14px;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background-color: rgba(0, 0, 0, 0.04);
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background-color 0.2s ease;
            }}

            .popup-close-btn:hover {{
                background-color: rgba(0, 0, 0, 0.08);
            }}

            .popup-close-btn svg {{
                width: 12px;
                height: 12px;
                fill: #444748;
            }}

            .popup-icon-circle {{
                width: 44px;
                height: 44px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 14px;
            }}

            .popup-icon-circle.success {{
                background-color: #2FA36B;
            }}

            .popup-icon-circle.error {{
                background-color: #C5445B;
            }}

            .popup-icon-circle svg {{
                width: 22px;
                height: 22px;
                fill: #FFFFFF;
            }}

            .popup-title {{
                font-size: 15px;
                font-weight: 700;
                color: #111111;
                margin: 0 0 10px 0;
                letter-spacing: -0.2px;
            }}

            .popup-desc {{
                font-size: 12.5px;
                line-height: 1.45;
                color: #5E6366;
                margin: 0;
            }}

            .popup-desc b {{
                color: #111111;
                word-break: break-all;
            }}

            .btn-popup-retry {{
                margin-top: 16px;
                width: 100%;
                padding: 10px 16px;
                border-radius: 8px;
                background-color: #C5445B;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                border: none;
                cursor: pointer;
                transition: opacity 0.2s ease;
            }}

            .btn-popup-retry:hover {{
                opacity: 0.9;
            }}

        </style>
    </head>
    <body>
        <div class="layout-container notranslate" translate="no">
            {sidebar_html}

            <main class="main-content">
                <div class="top-stepper-bar">
                    <div class="stepper-container">
                        <div class="step-item">
                            <div class="step-circle completed">1</div>
                            <span class="step-text">Subir</span>
                        </div>
                        <div class="step-line completed"></div>
                        <div class="step-item">
                            <div class="step-circle completed">2</div>
                            <span class="step-text">Categoría</span>
                        </div>
                        <div class="step-line completed"></div>
                        <div class="step-item">
                            <div class="step-circle completed">3</div>
                            <span class="step-text">Módulos</span>
                        </div>
                        <div class="step-line completed"></div>
                        <div class="step-item">
                            <div class="step-circle active">4</div>
                            <span class="step-text active">Reporte</span>
                        </div>
                    </div>
                </div>

                <section class="report-main-header">
                    <div class="header-info-wrap">
                        <p class="breadcrumb-text">Nuevo análisis · 04 Reporte</p>
                        <h1 class="report-heading">Reporte de análisis semiótico</h1>
                        <div class="report-meta-row">
                            <span>CATEGORÍA: <span class="report-meta-val">{categoria_txt}</span></span>
                            <span>MÓDULO DE ANÁLISIS: <span class="report-meta-val">{modulo_txt}</span></span>
                        </div>
                    </div>
                    <button class="btn-export-pdf {'disabled' if not hay_reporte_activo else ''}" id="btnExportarPdf">
                        <img src="{icon_print}" class="btn-export-icon" alt="Imprimir">
                        <span>Exportar a PDF</span>
                    </button>
                </section>

                <div class="report-sheet-container">
                    <div class="report-sheet-card">
                        {contenido_template}
                    </div>
                </div>

                <div class="feedback-section-container">
                    <div class="feedback-card">
                        <div class="feedback-header">
                            <svg class="feedback-icon" viewBox="0 0 24 24">
                                <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                            </svg>
                            <h3 class="feedback-title">Comentarios y sugerencias</h3>
                            <span class="feedback-badge">OPCIONAL</span>
                        </div>
                        <p class="feedback-subtitle">¿Tenés algún comentario, corrección o sugerencia sobre este análisis? Contanos</p>
                        <textarea class="feedback-textarea" id="txtComentario" placeholder="Escribí tu comentario acá..."></textarea>

                        <div class="feedback-row-inputs">
                            <input type="email" class="feedback-email-input" id="txtEmailFeedback" placeholder="tu@email.com">
                            <p class="feedback-email-hint">Email opcional — solo si querés que te respondamos.</p>
                        </div>

                        <button class="btn-send-feedback" id="btnEnviarComentario">
                            Enviar comentario
                        </button>
                    </div>
                </div>

                {html_seccion_historial}

                <footer class="footer-container notranslate" translate="no">
                    <p class="footer-text">© 2026 Indexal - Análisis visual asistido por IA - Todos los derechos reservados</p>
                    <div class="footer-links">
                        <a href="javascript:void(0)" class="footer-link">Términos y condiciones</a>
                        <a href="javascript:void(0)" class="footer-link">Política de privacidad</a>
                    </div>
                </footer>
            </main>
        </div>

        <!-- OVERLAY MODAL ÉXITO -->
        <div class="modal-overlay" id="modalExito">
            <div class="popup-card success">
                <button class="popup-close-btn" id="btnCloseExito">
                    <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                </button>
                <div class="popup-icon-circle success">
                    <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                </div>
                <h4 class="popup-title">PDF generado y descargado</h4>
                <p class="popup-desc">
                    <b>{nombre_pdf_actual}</b> se guardó en tu carpeta de Descargas y quedó disponible en "Reportes de esta sesión".
                </p>
            </div>
        </div>

        <!-- OVERLAY MODAL ERROR -->
        <div class="modal-overlay" id="modalError">
            <div class="popup-card error">
                <button class="popup-close-btn" id="btnCloseError">
                    <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                </button>
                <div class="popup-icon-circle error">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                </div>
                <h4 class="popup-title">Falla en generación del PDF</h4>
                <p class="popup-desc">
                    Ocurrió un error al exportar el reporte. Tus datos de análisis siguen disponibles.
                </p>
                <button class="btn-popup-retry" id="btnReintentarExport">
                    Reintentar exportación
                </button>
            </div>
        </div>

        <!-- OVERLAY MODAL FEEDBACK ENVIADO -->
        <div class="modal-overlay" id="modalFeedbackOk">
            <div class="popup-card success">
                <button class="popup-close-btn" id="btnCloseFeedback">
                    <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                </button>
                <div class="popup-icon-circle success">
                    <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                </div>
                <h4 class="popup-title">¡Gracias por tu comentario!</h4>
                <p class="popup-desc">
                    Tu aporte nos ayuda a mejorar Indexal. Si dejaste tu email, te responderemos a la brevedad.
                </p>
            </div>
        </div>

        <script>
            const parentDoc = window.parent.document;
            
            function irAHome() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 0) allButtons[0].click();
            }}
            document.getElementById('btnSidebarLogo').addEventListener('click', irAHome);
            document.getElementById('btnMenuInicio').addEventListener('click', irAHome);

            document.getElementById('btnMenuNuevo').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 1) allButtons[1].click();
            }});

            document.getElementById('btnMenuGaleria').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 2) allButtons[2].click();
            }});

            const hayReporte = {'true' if hay_reporte_activo else 'false'};
            const pdfExitoso = {'true' if pdf_generado_exitosamente else 'false'};
            
            const btnExp = document.getElementById('btnExportarPdf');
            const modalExito = document.getElementById('modalExito');
            const modalError = document.getElementById('modalError');
            const modalFeedbackOk = document.getElementById('modalFeedbackOk');

            function cerrarModales() {{
                if (modalExito) modalExito.classList.remove('active');
                if (modalError) modalError.classList.remove('active');
                if (modalFeedbackOk) modalFeedbackOk.classList.remove('active');
            }}

            const btnCerrarOk = document.getElementById('btnCloseExito');
            if (btnCerrarOk) btnCerrarOk.addEventListener('click', cerrarModales);

            const btnCerrarErr = document.getElementById('btnCloseError');
            if (btnCerrarErr) btnCerrarErr.addEventListener('click', cerrarModales);

            const btnCerrarFeed = document.getElementById('btnCloseFeedback');
            if (btnCerrarFeed) btnCerrarFeed.addEventListener('click', cerrarModales);

            function posicionarModal(modalElem) {{
                if (!modalElem) return;
                
                try {{
                    // 1. Obtener la posición del iframe respecto a la pantalla visible del padre
                    let iframeOffsetTop = 0;
                    if (window.frameElement) {{
                        const rect = window.frameElement.getBoundingClientRect();
                        iframeOffsetTop = rect.top; // Distancia desde el borde superior de la pantalla hasta donde empieza el iframe
                    }}

                    // 2. Altura de la ventana visible del navegador
                    const ventanaVisibleAlto = window.parent.innerHeight || window.innerHeight || 800;
                    const centroPantalla = ventanaVisibleAlto / 2;

                    // 3. La posición exacta dentro del iframe donde está mirando el usuario:
                    // (Scroll actual respecto al iframe = Centro de la pantalla visible - inicio del iframe)
                    const scrollActualEnIframe = (window.parent.scrollY || window.pageYOffset || 0) - (window.frameElement ? window.frameElement.offsetTop : 0);
                    
                    // Cálculo de marginTop compensado
                    let posFinal = -iframeOffsetTop + centroPantalla - 140;

                    // Si da negativo o falla la lectura entre ventanas cruzadas, fallback inteligente
                    if (isNaN(posFinal) || posFinal < 40) {{
                        const scrollTopParent = window.parent.scrollY || document.documentElement.scrollTop || 0;
                        posFinal = Math.max(40, scrollTopParent + 200);
                    }}

                    const card = modalElem.querySelector('.popup-card');
                    if (card) {{
                        card.style.marginTop = Math.max(40, Math.round(posFinal)) + 'px';
                    }}
                }} catch (e) {{
                    // Fallback de seguridad en caso de restricción de iframe
                    const card = modalElem.querySelector('.popup-card');
                    if (card) {{
                        card.style.marginTop = '250px';
                    }}
                }}

                modalElem.classList.add('active');
            }}

            function ejecutarExportacion() {{
                cerrarModales();
                if (!hayReporte) return;

                if (pdfExitoso) {{
                    const dlBtn = parentDoc.querySelector('div[data-testid="stDownloadButton"] button');
                    if (dlBtn) dlBtn.click();
                    posicionarModal(modalExito);
                }} else {{
                    posicionarModal(modalError);
                }}
            }}

            if (btnExp && hayReporte) {{
                btnExp.addEventListener('click', ejecutarExportacion);
            }}

            const btnReintentar = document.getElementById('btnReintentarExport');
            if (btnReintentar) {{
                btnReintentar.addEventListener('click', ejecutarExportacion);
            }}

            document.getElementById('btnEnviarComentario').addEventListener('click', function() {{
                const comment = document.getElementById('txtComentario').value;
                if (comment.trim().length > 0) {{
                    document.getElementById('txtComentario').value = '';
                    document.getElementById('txtEmailFeedback').value = '';
                    posicionarModal(modalFeedbackOk);
                }}
            }});

            // Descargas de las filas de la sesión
            { "".join([f"""
            const btnDown_{i} = document.getElementById('btnDownloadRow_{i}');
            if (btnDown_{i}) {{
                btnDown_{i}.addEventListener('click', function() {{
                    const dlBtns = parentDoc.querySelectorAll('div.stDownloadButton button');
                    if (dlBtns.length > {1 + i}) dlBtns[{1 + i}].click();
                }});
            }}
            """ for i in range(len(lista_reportes))]) }
        </script>
    </body>
    </html>
    """

    # Cálculo proporcional adaptativo según contenido real
    if not hay_reporte_activo:
        component_height = 890 + (len(lista_reportes) * 80)
    else:
        # Base estructural: Stepper (70px) + Header (140px) + Feedback (310px) + Footer (70px) + Espaciados (160px)
        altura_base = 750
        
        # Tabla de alturas según la carga visual y textual de cada módulo
        ALTURAS_POR_MODULO = {
            "composicion_visual": 1000,  # NO TOCAR VALOR
            "paleta_cromatica": 900,     # NO TOCAR VALOR
            "iluminacion": 1450,          # NO TOCAR VALOR
            "semiotica_imagen": 1200,     # NO TOCAR VALOR
            "retorica_visual": 1300,      # NO TOCAR VALOR
            "contexto_denotacion": 1350,  # Nivel literal y contexto
            "transversal_wcag": 600,     # Tabla de contraste de accesibilidad
            "transversal_historicas": 600 # Referencias y movimientos históricos
        }
        
        # Sumamos la altura individual de los módulos que realmente se ejecutaron
        modulos_ejecutados = st.session_state.get("modulos_seleccionados", [])
        altura_bloques_acumulada = 0
        
        for mod_id in modulos_ejecutados:
            altura_bloques_acumulada += ALTURAS_POR_MODULO.get(mod_id, 850)
            
        if st.session_state.get("transversal_wcag"):
            altura_bloques_acumulada += ALTURAS_POR_MODULO["transversal_wcag"]
        if st.session_state.get("transversal_historicas"):
            altura_bloques_acumulada += ALTURAS_POR_MODULO["transversal_historicas"]
            
        # Si por alguna razón no se detectaron IDs en session_state, usamos la cantidad de bloques en el JSON
        if altura_bloques_acumulada == 0:
            cant_bloques = len(ultimo_json.get("bloques", []))
            altura_bloques_acumulada = cant_bloques * 850

        total_items = len(modulos_ejecutados)
        # Factor de escala según cantidad real de bloques en pantalla
        if total_items <= 1:
            factor_escala = 1.0     # 100% para 1 módulo individual
        elif total_items == 2:
            factor_escala = 0.75    # NO TOCAR DESC: 25%
        elif total_items == 3:
            factor_escala = 0.65    # NO TOCAR DESC: 35%
        elif total_items == 4:
            factor_escala = 0.60    # NO TOCAR DESC: 40%
        else:
            factor_escala = 0.57  # NO TOCAR DESC: 43%

        altura_bloques_ajustada = int(altura_bloques_acumulada * factor_escala)
        altura_historial = len(lista_reportes) * 80
        component_height = altura_base + altura_bloques_ajustada + altura_historial

    components.html(reportes_html, height=component_height, scrolling=False)

    # 1. Download Button invisible para el botón principal "Exportar a PDF"
    st.download_button(
        label="dl_main_pdf",
        data=pdf_bytes_actual or b"",
        file_name=nombre_pdf_actual,
        mime="application/pdf",
        key="btn_dl_main_pdf"
    )

    # 2. Download Buttons invisibles para el historial de reportes
    for idx, rep in enumerate(lista_reportes):
        pdf_bytes_rep = b""
        rep_json = rep.get("json_data")
        if rep_json:
            try:
                ruta_temp = os.path.join("assets", f"temp_{rep['id']}.pdf")
                generar_reporte_pdf(rep_json, ruta_temp)
                with open(ruta_temp, "rb") as f:
                    pdf_bytes_rep = f.read()
            except Exception:
                pass

        st.download_button(
            label=f"dl_rep_{rep['id']}",
            data=pdf_bytes_rep,
            file_name=rep["archivo"],
            mime="application/pdf",
            key=f"btn_dl_history_{rep['id']}"
        )

    # 3. Botones de navegación interna
    cols = st.columns(4)
    with cols[0]:
        if st.button("\u200b", key="btn_hidden_rep_home"):
            st.session_state["pantalla_actual"] = "home"
            st.rerun()
    with cols[1]:
        if st.button("\u200b", key="btn_hidden_rep_nuevo"):
            st.session_state["pantalla_actual"] = "analizar"
            st.rerun()
    with cols[2]:
        if st.button("\u200b", key="btn_hidden_rep_galeria"):
            st.session_state["pantalla_actual"] = "galeria"
            st.rerun()

# -----------------------------------------------------------------
# CONTROLADOR PRINCIPAL DE VISTAS
# -----------------------------------------------------------------
pantalla = st.session_state.get("pantalla_actual", "splash")

if pantalla == "splash":
    render_splash()
elif pantalla == "home":
    render_home()
elif pantalla == "galeria":
    render_galeria()
elif pantalla == "analizar":
    render_analizar()
elif pantalla == "reportes":
    render_reportes()