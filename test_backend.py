import os
import pprint

# Importamos subcapas desde su estructura de carpetas correspondiente
from core.dimensiones.dimension_semantica.iconica_peirce import analizar_semiotica_iconica
from core.dimensiones.dimension_semantica.simbolica import analizar_semiotica_simbolica
from core.dimensiones.dimension_semantica.indicial_materialidad import analizar_semiotica_indicial
from core.dimensiones.dimension_semantica.retorica_linguistica_barthes import analizar_retorica_barthes
from core.dimensiones.dimension_semantica.tipografica import analizar_tipografia

def probar_analisis(subcapa_a_probar: str = "todas"):
    """
    Ejecuta pruebas en el pipeline semiótico de Indexal.
    
    Parámetro subcapa_a_probar: 'iconica', 'simbolica' o 'todas'
    """
    # 1. Ruta a la imagen real de prueba
    ruta_imagen_prueba = r"C:\Users\Agus\Desktop\imagenes test Indexal\texto-publicitario-mcdonalds.jpg" 
    
    # 2. Categoría a evaluar ('afiche', 'logo', 'ui', 'general')
    categoria_prueba = "general"
    
    print("=" * 60)
    print(f"🧪 INICIANDO PRUEBA DE PIPELINE SEMIÓTICO")
    print(f"📷 Imagen: {ruta_imagen_prueba}")
    print(f"🏷️  Categoría: {categoria_prueba.upper()}")
    print(f"⚙️  Subcapa(s) seleccionada(s): {subcapa_a_probar.upper()}")
    print("=" * 60 + "\n")
    
    if not os.path.exists(ruta_imagen_prueba):
        print(f"❌ Error: No encontré ninguna imagen en '{ruta_imagen_prueba}'.")
        print("Por favor, colocá una imagen real y actualizá la ruta en el script.")
        return

    # 3. Ejecución Subcapa Icónica
    if subcapa_a_probar.lower() in ["iconica", "todas"]:
        print("🔍 --- Procesando Subcapa Icónica (Peirce) ---")
        resultado_iconico = analizar_semiotica_iconica(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO ICÓNICO ---")
        pprint.pprint(resultado_iconico)
        print("\n" + "-" * 40 + "\n")

    # 4. Ejecución Subcapa Simbólica
    if subcapa_a_probar.lower() in ["simbolica", "todas"]:
        print("🧠 --- Procesando Subcapa Simbólica (Peirce) ---")
        resultado_simbolico = analizar_semiotica_simbolica(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO SIMBÓLICO ---")
        pprint.pprint(resultado_simbolico)
        print("\n" + "-" * 40 + "\n")
    
    # 5. Ejecución Subcapa Indicial y Materialidad
    if subcapa_a_probar.lower() in ["indicial", "todas"]:
        print("🔬 --- Procesando Subcapa Indicial y Materialidad (Peirce) ---")
        resultado_indicial = analizar_semiotica_indicial(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO INDICIAL ---")
        pprint.pprint(resultado_indicial)
        print("\n" + "-" * 40 + "\n")
    
    # 6. Ejecución Subcapa Retórica y Lingüística (Barthes)
    if subcapa_a_probar.lower() in ["barthes", "todas"]:
        print("✍️ --- Procesando Subcapa Retórica y Lingüística (Barthes) ---")
        resultado_barthes = analizar_retorica_barthes(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO BARTHES ---")
        pprint.pprint(resultado_barthes)
        print("\n" + "-" * 40 + "\n")
    
    # 7. Ejecución Subcapa Tipográfica
    if subcapa_a_probar.lower() in ["tipografica", "todas"]:
        print("🔤 --- Procesando Subcapa Tipográfica ---")
        resultado_tipografia = analizar_tipografia(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO TIPOGRÁFICO ---")
        pprint.pprint(resultado_tipografia)
        print("\n" + "-" * 40 + "\n")


if __name__ == "__main__":
    # Opciones: "iconica", "simbolica", "indicial", "barthes", "tipografica" o "todas"
    SUBCAPA = "tipografica" 
    
    probar_analisis(subcapa_a_probar=SUBCAPA)