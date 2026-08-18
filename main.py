
#streamlit run main.py

import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Indexal", 
    page_icon="assets/iconos/logo_x.svg", 
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
    try:
        with open("assets/iconos/logo_x.svg", "rb") as f:
            svg_b64 = base64.b64encode(f.read()).decode("utf-8")
        img_src = f"data:image/svg+xml;base64,{svg_b64}"
    except Exception:
        img_src = ""

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
            pass
    with col2:
        if st.button("Explorar galería", use_container_width=True, type="secondary"):
            st.session_state["pantalla_actual"] = "galeria"
            st.rerun()

# -----------------------------------------------------------------
# PANTALLA 3: GALERÍA DE IMÁGENES ANALIZADAS 
# -----------------------------------------------------------------

def render_galeria():
    st.markdown(
        """
        <!-- Inyección directa de Google Fonts al head del documento -->
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

        /* 1. Forzar tipografía global en todo el árbol de Streamlit */
        html, body, [class*="css"], .stApp, .stApp * {
            font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        }

        .stApp {
            background-color: #EAEAE8 !important;
        }

        /* 2. Eliminar header y márgenes superiores de Streamlit */
        header[data-testid="stHeader"],
        header,
        .stAppHeader { 
            display: none !important; 
            height: 0px !important;
            visibility: hidden !important;
        }

        #MainMenu, footer { visibility: hidden; }

        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewBlockContainer"],
        div[data-testid="stMainBlockContainer"],
        section.main,
        .stMain,
        .main {
            padding: 0px !important;
            margin: 0px !important;
            min-height: auto !important;
            display: block !important;
            background-color: #EAEAE8 !important;
        }

        .block-container,
        div[data-testid="block-container"] {
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

        /* 3. OCULTAR BOTONES NATIVOS DISPARADORES DE STREAMLIT */
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
    """,
        unsafe_allow_html=True,
    )

    # 1. FUNCIÓN AUXILIAR PARA LEER Y CONVERTIR SVG A BASE64
    def cargar_svg_base64(ruta_relativa):
        try:
            with open(ruta_relativa, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64}"
        except Exception:
            return ""

    img_logo = cargar_svg_base64("assets/iconos/logo_x.svg")
    icon_chart_src = cargar_svg_base64("assets/iconos/icon-nav-chart.svg")
    icon_doc_src = cargar_svg_base64("assets/iconos/icon-nav-doc.svg")
    icon_arrow_src = cargar_svg_base64("assets/iconos/vector.svg")
    icon_flag_src = cargar_svg_base64("assets/iconos/icon-flag.svg")
    icon_eye_off_src = cargar_svg_base64("assets/iconos/visibility_off.svg")

    # Mock data para maquetar
    INFORMES_MOCK = [
        {
            "id": "inf_01",
            "categoria": "SEMIÓTICO",
            "titulo": "Sistema de identidad · Estudio Norma",
            "descripcion": (
                "Sistema de identidad completo con aplicaciones en distintos"
                " soportes"
            ),
            "tag": "Semiótico",
            "modulo": "Módulo A · Semiótico",
            "color_placeholder": "#E6C2B4",
        },
        {
            "id": "inf_02",
            "categoria": "UI / UX",
            "titulo": "Interfaz móvil · App de salud",
            "descripcion": (
                "Pantalla principal con sistema de navegación y visualización"
                " de datos"
            ),
            "tag": "Semiótico",
            "modulo": "Módulo A · Semiótico",
            "color_placeholder": "#6B7280",
        },
        {
            "id": "inf_03",
            "categoria": "PACKAGING",
            "titulo": "Colección orgánica · Vitamins",
            "descripcion": (
                "Packaging minimalista con código cromático funcional para"
                " línea premium"
            ),
            "tag": "Semiótico",
            "modulo": "Módulo A · Semiótico",
            "color_placeholder": "#36635C",
        },
        {
            "id": "inf_04",
            "categoria": "TIPOGRAFÍA",
            "titulo": "Sistema tipográfico · Editorial",
            "descripcion": (
                "Jerarquía tipográfica para publicación impresa y digital"
            ),
            "tag": "Semiótico",
            "modulo": "Módulo A · Semiótico",
            "color_placeholder": "#C8C4B7",
        },
        {
            "id": "inf_05",
            "categoria": "LOGOTIPO",
            "titulo": "Identidad de marca · Kaia",
            "descripcion": (
                "Construcción de isotipo y aplicaciones sobre fondo oscuro"
            ),
            "tag": "Semiótico",
            "modulo": "Módulo A · Semiótico",
            "color_placeholder": "#282B30",
        },
        {
            "id": "inf_06",
            "categoria": "AFICHES",
            "titulo": "Campaña gráfica · Festival Sur",
            "descripcion": "Serie de afiches con sistema modular de retícula",
            "tag": "Semiótico",
            "modulo": "Módulo A · Semiótico",
            "color_placeholder": "#D8A75F",
        },
    ]

    cant_semiotico = 1
    cant_logotipo = 1
    cant_afiches = 1
    cant_packaging = 1
    cant_tipografia = 1
    cant_uiux = 1

    # 2. HTML + CSS + JS DE LA CABECERA
    header_component = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

            * {{ box-sizing: border-box; }}

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background-color: #EAEAE8 !important;
                width: 100% !important;
                overflow: hidden !important;
                user-select: none;
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
                font-family: 'Orbitron', sans-serif;
                font-size: 17px;
                font-weight: 700;
                line-height: 21px;
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
                font-family: 'Space Grotesk', sans-serif;
                font-size: 13.5px;
                font-weight: 400;
                line-height: 17px;
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
            }}

            .hero-text-block {{
                display: flex;
                flex-direction: column;
            }}

            .hero-badge {{
                color: #0057FF;
                font-family: 'Orbitron', sans-serif;
                font-size: 14px;
                font-weight: 700;
                line-height: 18px;
                letter-spacing: 4.2px;
                margin: 0;
            }}

            .hero-title {{
                color: #111111;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 64px;
                font-weight: 700;
                line-height: 64px;
                letter-spacing: -1.6px;
                margin-top: 16px;
                margin-bottom: 0;
            }}

            .hero-subtitle {{
                color: #444748;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 15px;
                font-weight: 400;
                line-height: 19px;
                letter-spacing: 0.8px;
                margin-top: 16px;
                margin-bottom: 0;
            }}

            /* BOTÓN ANALIZAR MI IMAGEN */
            .hero-btn-action {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 28px;
                background-color: #0057FF;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                text-decoration: none;
                transition: background-color 0.2s ease, transform 0.1s ease;
            }}

            .hero-btn-action:hover {{ background-color: #0046D5; }}
            .hero-btn-action:active {{ transform: scale(0.98); }}

            .hero-btn-text {{
                color: #FFFFFF;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 16.5px;
                font-weight: 700;
                line-height: 21px;
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
            }}

            .filter-pill-active {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                height: 33px;
                padding: 8px 16px;
                background-color: #0057FF;
                border-radius: 999px;
                color: #FFFFFF;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 13px;
                font-weight: 700;
                line-height: 17px;
                cursor: pointer;
                border: none;
                user-select: none;
                transition: background-color 0.2s ease;
                flex-shrink: 0;
            }}

            .filter-pill-active:hover {{ background-color: #0046D5; }}

            .filter-pill-inactive {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                height: 33px;
                padding: 8px 16px;
                background-color: #FFFFFF;
                border: 1px solid #C4C6CF;
                border-radius: 999px;
                cursor: pointer;
                user-select: none;
                transition: background-color 0.2s ease, border-color 0.2s ease;
                flex-shrink: 0;
            }}

            .filter-pill-inactive:hover {{
                background-color: #F8F9FA;
                border-color: #A8ACB4;
            }}

            .filter-pill-label {{
                color: #111111;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 13px;
                font-weight: 500;
                line-height: 17px;
            }}

            .filter-pill-count {{
                color: #444748;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 12px;
                font-weight: 400;
                line-height: 15px;
            }}
        </style>

        <div class="navbar-container">
            <div class="navbar-brand" id="btnLogoHome">
                <img src="{img_logo}" class="navbar-logo-img" alt="Indexal">
                <span class="navbar-brand-text" translate="no">INDEXAL</span>
            </div>
            <div class="navbar-nav">
                <div class="nav-item">
                    <img src="{icon_chart_src}" class="nav-icon" alt="Análisis">
                    <span translate="no">Análisis</span>
                </div>
                <div class="nav-item">
                    <img src="{icon_doc_src}" class="nav-icon" alt="Reportes">
                    <span translate="no">Reportes</span>
                </div>
            </div>
        </div>

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

        <div class="filters-bar-container">
            <button class="filter-pill-active" translate="no">Todo</button>
            <button class="filter-pill-inactive">
                <span class="filter-pill-label" translate="no">Semiótico</span>
                <span class="filter-pill-count" translate="no">{cant_semiotico}</span>
            </button>
            <button class="filter-pill-inactive">
                <span class="filter-pill-label" translate="no">Logotipo</span>
                <span class="filter-pill-count" translate="no">{cant_logotipo}</span>
            </button>
            <button class="filter-pill-inactive">
                <span class="filter-pill-label" translate="no">Afiches</span>
                <span class="filter-pill-count" translate="no">{cant_afiches}</span>
            </button>
            <button class="filter-pill-inactive">
                <span class="filter-pill-label" translate="no">Packaging</span>
                <span class="filter-pill-count" translate="no">{cant_packaging}</span>
            </button>
            <button class="filter-pill-inactive">
                <span class="filter-pill-label" translate="no">Tipografía</span>
                <span class="filter-pill-count" translate="no">{cant_tipografia}</span>
            </button>
            <button class="filter-pill-inactive">
                <span class="filter-pill-label" translate="no">UI/UX</span>
                <span class="filter-pill-count" translate="no">{cant_uiux}</span>
            </button>
        </div>

        <script>
            const parentDoc = window.parent.document;
            
            document.getElementById('btnLogoHome').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 0) {{
                    allButtons[0].click();
                }}
            }});

            document.getElementById('btnAnalizarImagen').addEventListener('click', function() {{
                const allButtons = parentDoc.querySelectorAll('div.stButton button');
                if (allButtons.length > 1) {{
                    allButtons[1].click();
                }}
            }});
        </script>
    """

    components.html(header_component, height=522)

    # 3. DISPARADORES OCULTOS
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("\u200b", key="btn_hidden_nav_home"):
            st.session_state["pantalla_actual"] = "home"
            st.rerun()
    with col_btn2:
        if st.button("\u200b", key="btn_hidden_analizar"):
            st.session_state["pantalla_actual"] = "analizar"
            st.rerun()

    # 4. CONSTRUCCIÓN DE CARDS DINÁMICAS (Con translate="no")
    cards_html = ""
    for item in INFORMES_MOCK:
        cards_html += (
            f'<div class="card-item notranslate" translate="no">'
            f'<div class="card-image-area" style="background-color: {item["color_placeholder"]};"></div>'
            f'<div class="card-body">'
            f'<div class="card-category-row">'
            f'<img src="{icon_flag_src}" class="card-flag-icon" alt="">'
            f'<span class="card-category-text" translate="no">{item["categoria"]}</span>'
            f"</div>"
            f'<h3 class="card-title" translate="no">{item["titulo"]}</h3>'
            f'<p class="card-desc" translate="no">{item["descripcion"]}</p>'
            f'<div class="card-footer-row">'
            f'<div class="card-tag" translate="no">{item["tag"]}</div>'
            f'<span class="card-module-text" translate="no">{item["modulo"]}</span>'
            f'<button class="card-visibility-btn">'
            f'<img src="{icon_eye_off_src}" class="card-eye-icon" alt="">'
            f"</button>"
            f"</div>"
            f"</div>"
            f"</div>"
        )

    # 5. CONTENEDOR PRINCIPAL DE LA GRILLA DE GALERÍA (CON IFRAME AISLADO)
    import math

    filas = math.ceil(len(INFORMES_MOCK) / 3)
    altura_grilla = (filas * 358) + 88 + 65

    galeria_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Space Grotesk', sans-serif !important;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background-color: #EAEAE8 !important;
                width: 100% !important;
                overflow: hidden !important;
            }}

            .galeria-section-container {{
                width: 100%;
                background-color: #EAEAE8;
                padding: 24px 48px 40px 48px; /* Mantiene los 48px exactos de ambos laterales igual que el hero */
                display: flex;
                justify-content: flex-start; /* Alinea el contenido desde el inicio izquierdo */
            }}

            .galeria-grid {{
                display: flex;
                justify-content: space-between; /* Distribuye las 3 tarjetas de punta a punta exactamente como el hero */
                flex-wrap: wrap;
                gap: 20px;
                width: 100%;
            }}

            .card-item {{
                background-color: #FFFFFF;
                border-radius: 12px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                cursor: pointer;
                /* El ancho se adapta de forma fluida y proporcional para cubrir perfectamente el espacio entre los 48px de cada lateral */
                width: calc((100% - 56px) / 3); /* Resta los dos espacios de separación de 28px y divide en 3 */
                max-width: 397px; /* Respeta el tope exacto de Figma */
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }}

            .card-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            }}

            .card-image-area {{
                width: 100%;
                height: 220px;
                display: block;
            }}

            .card-body {{
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                align-self: stretch;
                padding: 16px;
                gap: 8px;
                background-color: #FFFFFF;
                box-sizing: border-box;
                max-width: 397px;
            }}

            .card-category-row {{
                display: flex;
                align-items: center;
                gap: 8px;
                height: 13px;
                width: 100%;
            }}

            .card-flag-icon {{
                width: 11px;
                height: 11px;
                display: block;
            }}

            .card-category-text {{
                color: #0057FF;
                font-size: 10.5px;
                font-weight: 700;
                letter-spacing: 0.6px;
                text-transform: uppercase;
                line-height: normal;
            }}

            .card-title {{
                color: #111111;
                font-size: 15px;
                font-weight: 700;
                line-height: 19px;
                letter-spacing: -0.2px;
                margin: 0;
                width: 100%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            .card-desc {{
                color: #444748;
                font-size: 12px;
                font-weight: 400;
                line-height: 15px;
                margin: 0;
                width: 100%;
                max-width: 365px;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                height: 30px;
                text-overflow: ellipsis;
            }}

            .card-footer-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                margin-top: 0px;
            }}

            .card-tag {{
                background-color: #F3F4F1;
                border-radius: 4px;
                padding: 4px 8px;
                color: #444748;
                font-size: 11px;
                font-weight: 400;
                line-height: 14px;
            }}

            .card-module-text {{
                color: #444748;
                font-size: 11px;
                font-weight: 400;
                line-height: 14px;
                text-align: center;
                flex-grow: 1;
            }}

            .card-visibility-btn {{
                background-color: #F3F4F1;
                border: none;
                border-radius: 6px;
                width: 26px;
                height: 26px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                padding: 0;
            }}

            .card-eye-icon {{
                width: 14px;
                height: 14px;
                display: block;
            }}

            /* ESTILOS EXACTOS DEL FOOTER SEGÚN FIGMA */
            .footer-container {{
                display: flex;
                width: 100%;
                padding: 20px 48px;
                justify-content: space-between;
                align-items: center;
                background: #FFFFFF;
                border-top: 1px solid #C4C6CF;
                box-sizing: border-box;
            }}

            .footer-text {{
                color: #444748;
                font-size: 12px;
                font-weight: 400;
                line-height: normal;
                margin: 0;
            }}

            .footer-links {{
                display: flex;
                gap: 20px;
            }}

            .footer-link {{
                color: #0057FF;
                font-size: 12px;
                font-weight: 500;
                line-height: normal;
                text-decoration: none;
            }}

            .footer-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="galeria-section-container notranslate" translate="no">
            <div class="galeria-grid" translate="no">
                {cards_html}
            </div>
        </div>
        <footer class="footer-container notranslate" translate="no">
            <p class="footer-text">© 2026 Indexal - Análisis visual asistido por IA - Todos los derechos reservados</p>
            <div class="footer-links">
                <a href="javascript:void(0)" class="footer-link">Términos y condiciones</a>
                <a href="javascript:void(0)" class="footer-link">Política de privacidad</a>
            </div>
        </footer>
    </body>
    </html>
    """

    components.html(galeria_html, height=altura_grilla)

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