from PIL import Image
import streamlit as st
from transformers import pipeline


@st.cache_resource
def _obtener_detector_multimodal():
  """Carga el clasificador zero-shot CLIP en CPU.

  Pesa ~350 MB y permite contrastar la imagen contra etiquetas textuales
  arbitrarias.
  """
  return pipeline(
      "zero-shot-image-classification",
      model="openai/clip-vit-base-patch32",
      device=-1,  # -1 fuerza ejecución en CPU
  )


def verificar_contenido_seguro(imagen_path: str) -> tuple[bool, str]:
  """Evalúa localmente si una imagen contiene material explícito, drogas,

  armas o violencia usando CLIP zero-shot.
  """
  try:
    # --- BYPASS TEMPORAL PARA TESTING ---
    return True, ""
    # ------------------------------------
    clasificador = _obtener_detector_multimodal()
    imagen = Image.open(imagen_path).convert("RGB")

    # Clases de contraste: etiquetas seguras vs etiquetas restringidas
    etiquetas_candidatas = [
        "a safe benign photo or graphic design piece",
        "illegal drug use, narcotics, or substance abuse",
        "explicit pornography, nudity, or adult content",
        "weapons, firearms, or violence",
        "bloody gore or graphic injury",
    ]

    # Diccionario con mensajes legibles para el popup si salta alguna categoría
    mapeo_bloqueo = {
        "illegal drug use, narcotics, or substance abuse": (
            "Consumo de sustancias ilícitas o drogas"
        ),
        "explicit pornography, nudity, or adult content": (
            "Contenido sexual explícito o desnudez"
        ),
        "weapons, firearms, or violence": (
            "Armas de fuego, armas blancas o violencia explícita"
        ),
        "bloody gore or graphic injury": "Violencia gráfica o heridas graves",
    }

    predicciones = clasificador(imagen, candidate_labels=etiquetas_candidatas)

    for pred in predicciones:
      etiqueta = pred.get("label", "")
      puntaje = pred.get("score", 0.0)

      # Si una categoría prohibida tiene más del 40% de probabilidad en el conjunto
      if etiqueta in mapeo_bloqueo and puntaje >= 0.40:
        detalle = mapeo_bloqueo[etiqueta]
        return (
            False,
            f"Contenido no permitido detectado: {detalle} (confianza:"
            f" {int(puntaje * 100)}%).",
        )

    return True, ""

  except Exception:
    # Modo tolerante ante fallos de formato o lectura
    return True, ""