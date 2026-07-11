# main.py
import os
import sys
import subprocess

def verificar_e_instalar_dependencias():
    """
    Revisa el archivo requirements.txt e instala automáticamente
    cualquier dependencia que falte en el entorno virtual activo.
    """
    ruta_requirements = "requirements.txt"
    
    if not os.path.exists(ruta_requirements):
        print("⚠️  Advertencia: No se encontró el archivo 'requirements.txt' en la raíz.")
        return

    print("🔍 Verificando dependencias locales...")
    try:
        # Ejecuta 'pip install -r requirements.txt' de forma silenciosa
        # usando el mismo ejecutable de Python del entorno virtual activo
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", ruta_requirements],
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
        print("✅ Entorno virtual actualizado y alineado con requirements.txt.")
    except Exception as e:
        print(f"⚠️  No se pudo verificar la auto-instalación. Detalle: {e}")


