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
        st.button("Analizar imagen", use_container_width=True, type="primary")
    with col2:
        st.button("Explorar galería", use_container_width=True, type="secondary")


# -----------------------------------------------------------------
# CONTROLADOR PRINCIPAL DE VISTAS
# -----------------------------------------------------------------
if st.session_state.get("pantalla_actual", "splash") == "splash":
    render_splash()
else:
    render_home()