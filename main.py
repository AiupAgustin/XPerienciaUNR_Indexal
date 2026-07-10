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


# Importamos el módulo_a después de asegurar las librerías
verificar_e_instalar_dependencias()
print("\n--------------------------------------------------------")
from core.modulos import modulo_a
print("--------------------------------------------------------\n")

def ejecutar_test_local():
    print("🚀 [INDEXAL] Iniciando prueba de procesamiento local...\n")

    ruta_imagen = "prueba.jpg" 
    
    if not os.path.exists(ruta_imagen):
        print(f"❌ ERROR: No se encontró el archivo '{ruta_imagen}' en la raíz del proyecto.")
        print("Por favor, guardá una imagen cualquiera con ese nombre al lado de main.py.")
        return

    try:
        print(f"📂 Abriendo '{ruta_imagen}' y extrayendo sus bytes...")
        with open(ruta_imagen, "rb") as archivo:
            imagen_bytes = archivo.read()

        # --------------------------------------------------------
        # ÍTEM 1: NIVEL DENOTATIVO
        # --------------------------------------------------------
        print("⚙️  Procesando Ítem 1: Nivel Denotativo...")
        informe_denotativo = modulo_a.procesar_nivel_denotativo(imagen_bytes)
        print(informe_denotativo)

        print("\n" + "="*56 + "\n")

        # --------------------------------------------------------
        # ÍTEM 2: NIVEL CONNOTATIVO (Recibe el informe anterior y los bytes)
        # --------------------------------------------------------
        print("🧠 Procesando Ítem 2: Nivel Connotativo...")
        informe_connotativo = modulo_a.procesar_nivel_connotativo(informe_denotativo, imagen_bytes)
        print(informe_connotativo)

        # desde aca una linea de = y despues el item 3

        print("\n" + "="*56 + "\n")

        # --------------------------------------------------------
        # ÍTEM 3: EXTRACCIÓN DE PALETA CROMÁTICA
        # --------------------------------------------------------
        print("⚙️  Procesando Ítem 3: Extracción de Paleta Cromática...")
        informe_cromatico = modulo_a.extraer_paleta_cromatica(imagen_bytes, cantidad_colores=5)
        print(informe_cromatico)

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado en el test: {str(e)}")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado en el test: {str(e)}")

if __name__ == "__main__":
    ejecutar_test_local()