#archivo unicamente para testear la dimension pragmatica

import os
import pprint

# Importamos las subcapas de la Dimensión Pragmática
from core.dimensiones.dimension_pragmatica.semiotica_agentiva import analizar_semiotica_agentiva
from core.dimensiones.dimension_pragmatica.atencion_predictiva import analizar_atencion_predictiva
from core.dimensiones.dimension_pragmatica.secuencia_narrativa import analizar_secuencia_narrativa
from core.dimensiones.dimension_pragmatica.auditoria_de_sesgos import analizar_auditoria_sesgos
from core.dimensiones.dimension_pragmatica.inclusion_tecnica import analizar_inclusion_tecnica

def probar_analisis_pragmatico(subcapa_a_probar: str = "todas"):
    """
    Ejecuta pruebas en el pipeline de la Dimensión Pragmática de Indexal.
    
    Parámetro subcapa_a_probar: 'agentiva', 'atencion', 'narrativa', 'sesgos', 'inclusion' o 'todas'
    """
    # 1. Ruta a la imagen real de prueba
    ruta_imagen_prueba = r"C:\Users\Agus\Desktop\imagenes test Indexal\test_eco.jfif"
    
    # 2. Categoría a evaluar ('afiche', 'logo', 'ui', 'general')
    categoria_prueba = "general"
    
    print("=" * 60)
    print(f"🧪 INICIANDO PRUEBA DE PIPELINE PRAGMÁTICO")
    print(f"📷 Imagen: {ruta_imagen_prueba}")
    print(f"🏷️  Categoría: {categoria_prueba.upper()}")
    print(f"⚙️  Subcapa(s) seleccionada(s): {subcapa_a_probar.upper()}")
    print("=" * 60 + "\n")
    
    if not os.path.exists(ruta_imagen_prueba):
        print(f"❌ Error: No encontré ninguna imagen en '{ruta_imagen_prueba}'.")
        print("Por favor, colocá una imagen real y actualizá la ruta en el script.")
        return

    # 3. Ejecución Subcapa Semiótica Agentiva
    if subcapa_a_probar.lower() in ["agentiva", "todas"]:
        print("🎯 --- Procesando Subcapa Semiótica Agentiva ---")
        resultado_agentivo = analizar_semiotica_agentiva(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO AGENTIVO ---")
        pprint.pprint(resultado_agentivo)
        print("\n" + "-" * 40 + "\n")

    # 4. Ejecución Subcapa Atención Predictiva
    if subcapa_a_probar.lower() in ["atencion", "todas"]:
        print("👁️ --- Procesando Subcapa Atención Predictiva ---")
        resultado_atencion = analizar_atencion_predictiva(ruta_imagen_prueba)
        print("\n--- RESULTADO ATENCIÓN PREDICTIVA ---")
        pprint.pprint(resultado_atencion)
        print("\n" + "-" * 40 + "\n")

    # 5. Ejecución Subcapa Secuencia Narrativa
    if subcapa_a_probar.lower() in ["narrativa", "todas"]:
        print("🎬 --- Procesando Subcapa Secuencia Narrativa ---")
        resultado_narrativa = analizar_secuencia_narrativa(ruta_imagen_prueba)
        print("\n--- RESULTADO SECUENCIA NARRATIVA ---")
        pprint.pprint(resultado_narrativa)
        print("\n" + "-" * 40 + "\n")
    
    # 6. Ejecución Subcapa Auditoría de Sesgos
    if subcapa_a_probar.lower() in ["sesgos", "todas"]:
        print("🛡️ --- Procesando Subcapa Auditoría de Sesgos ---")
        resultado_sesgos = analizar_auditoria_sesgos(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO AUDITORÍA DE SESGOS ---")
        pprint.pprint(resultado_sesgos)
        print("\n" + "-" * 40 + "\n")

    # 7. Ejecución Subcapa Inclusión Técnica
    if subcapa_a_probar.lower() in ["inclusion", "todas"]:
        print("♿ --- Procesando Subcapa Inclusión Técnica ---")
        resultado_inclusion = analizar_inclusion_tecnica(ruta_imagen_prueba, categoria=categoria_prueba)
        print("\n--- RESULTADO INCLUSIÓN TÉCNICA ---")
        pprint.pprint(resultado_inclusion)
        print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    # Opciones: "agentiva", "atencion", "narrativa", "sesgos", "inclusion" o "todas"
    SUBCAPA = "narrativa" 
    
    probar_analisis_pragmatico(subcapa_a_probar=SUBCAPA)