import streamlit as st
from servicios.notificaciones import enviar_correo_feedback

print("Intentando enviar correo de prueba...")
ok, msg = enviar_correo_feedback(
    mensaje="Este es un mensaje de prueba para verificar la API de Resend.",
    contacto="test@indexal.com",
    categoria="Prueba directa"
)

print(f"\nResultado: {ok}")
print(f"Detalle: {msg}")