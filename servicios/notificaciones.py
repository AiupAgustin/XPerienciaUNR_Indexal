import streamlit as st
import requests

def enviar_correo_feedback(
    mensaje: str,
    contacto: str = "No especificado",
    categoria: str = "Sugerencia general"
) -> tuple[bool, str]:
    """
    Función fachada para enviar notificaciones de feedback.
    Actualmente usa la API de Resend vía HTTP requests.
    Si en el futuro cambia el proveedor (Gmail SMTP, SendGrid, etc.),
    solo se modifica este bloque sin alterar el resto de la aplicación.
    """
    api_key = st.secrets.get("RESEND_API_KEY")
    destinatario = st.secrets.get("FEEDBACK_RECIPIENT_EMAIL")

    if not api_key or not destinatario:
        return False, "Faltan credenciales de correo en secrets.toml (RESEND_API_KEY o FEEDBACK_RECIPIENT_EMAIL)."

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Armamos el contenido en texto plano y HTML limpio
    cuerpo_texto = f"""
Nueva sugerencia recibida en Indexal:
--------------------------------------------------
Categoría: {categoria}
Contacto del remitente: {contacto}

Mensaje:
{mensaje}
--------------------------------------------------
"""

    payload = {
        "from": "Indexal App <onboarding@resend.dev>",
        "to": [destinatario],
        "subject": f"[Indexal Feedback] {categoria}",
        "text": cuerpo_texto
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=8)
        data = response.json()

        if response.status_code in (200, 201):
            return True, "¡Gracias! Tu sugerencia fue enviada con éxito."
        else:
            # Resend suele devolver el detalle del error en 'message'
            error_msg = data.get("message", "Error desconocido al procesar el envío.")
            return False, f"No se pudo enviar el correo: {error_msg}"

    except requests.exceptions.Timeout:
        return False, "Tiempo de espera agotado al conectar con el servidor de correo."
    except Exception as e:
        return False, f"Fallo de conexión al enviar el correo: {str(e)}"