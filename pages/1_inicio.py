import streamlit as st

st.set_page_config(
    page_title="Indexal", 
    page_icon="assets/iconos/logo_x.svg", 
    layout="centered"
)

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


