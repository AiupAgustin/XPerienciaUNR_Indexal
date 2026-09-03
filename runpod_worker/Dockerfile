FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema necesarias para procesamiento de imágenes y video
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python y rueda precompilada de flash-attn
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "transformers==4.44.2" \
    "accelerate==0.33.0" \
    torchvision \
    runpod \
    pillow \
    sentencepiece \
    protobuf \
    decord && \
    pip install --no-cache-dir https://github.com/Dao-AILab/flash-attention/releases/download/v2.5.8/flash_attn-2.5.8+cu122torch2.2cxx11abiFALSE-cp310-cp310-linux_x86_64.whl

# Copiar el código del handler
COPY handler.py .

# Comando de inicio para RunPod Serverless
CMD ["python", "-u", "handler.py"]