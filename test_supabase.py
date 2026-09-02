import streamlit as st
from servicios.database import subir_imagen_galeria, guardar_analisis_en_galeria, obtener_items_galeria

st.title("Test completo Supabase")

# 1. Crear un archivo de imagen en bytes falso (1 pixel PNG)
fake_png_bytes = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00'
    b'\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)

st.write("### 1. Probando subida al Storage ('galeria_imagenes')...")
try:
    url = subir_imagen_galeria("test_pixel.png", fake_png_bytes)
    st.success(f"Subida a Storage OK! URL pública: {url}")
    
    st.write("### 2. Probando inserción en tabla 'galeria'...")
    res = guardar_analisis_en_galeria(
        titulo="Prueba Pixel",
        categoria="Semiótico",
        imagen_url=url,
        master_json={
            "categoria": "Semiótico",
            "filtro_key": "semiotico",
            "descripcion": "Tarjeta de prueba",
            "modulo": "MÓDULO A"
        }
    )
    st.success(f"Guardado en Base de Datos OK! Registro ID: {res.get('id')}")

    st.write("### 3. Leyendo registros de la galería...")
    items = obtener_items_galeria()
    st.write(f"Total registros en Supabase: {len(items)}")
    st.json(items)

except Exception as e:
    st.error(f"Fallo en la prueba: {e}")