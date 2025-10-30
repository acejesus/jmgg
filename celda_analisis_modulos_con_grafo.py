# ================================================================================================
# CELDA DE ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS - LISTA PARA COLAB
# ================================================================================================
# INSTRUCCIONES:
# 1. Copia esta celda COMPLETA en tu notebook de Colab
# 2. Col

ócala DESPUÉS de la celda de preprocesamiento y visualización
# 3. Ejecuta para analizar módulos usando la nueva estrategia basada en grafos
# ================================================================================================

import networkx as nx
import numpy as np
import math
import pandas as pd
import os
from typing import List, Tuple, Dict

print("🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS")
print("="*60)

# ================================================================================================
# COPIAR TODAS LAS FUNCIONES DEL MÓDULO graph_module_detection.py
# ================================================================================================
# (Por simplicidad en Colab, copiamos las funciones directamente aquí)

# [NOTA: En producción, importarías: from graph_module_detection import *]

# Funciones auxiliares (copiadas del módulo)

def distancia_euclidiana(p1: Tuple, p2: Tuple) -> float:
    """Calcula la distancia euclidiana entre dos puntos."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def angulo_entre_vectores(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calcula el ángulo en grados entre dos vectores."""
    cos_angulo = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
    cos_angulo = np.clip(cos_angulo, -1.0, 1.0)
    return math.degrees(math.acos(abs(cos_angulo)))


def son_colineales(p1: Tuple, p2: Tuple, p3: Tuple, tolerancia_angulo: float = 5.0) -> bool:
    """Verifica si tres puntos son colineales."""
    v1 = np.array([p2[i] - p1[i] for i in range(min(len(p1), len(p2)))])
    v2 = np.array([p3[i] - p2[i] for i in range(min(len(p2), len(p3)))])

    if np.linalg.norm(v1) < 1e-10 or np.linalg.norm(v2) < 1e-10:
        return False

    angulo = angulo_entre_vectores(v1, v2)
    return angulo < tolerancia_angulo


def es_horizontal(edge, tolerance=0.01):
    """Determina si una arista es horizontal."""
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        return abs(n1[1] - n2[1]) < tolerance
    return False


# [INCLUIR AQUÍ TODAS LAS FUNCIONES DEL MÓDULO graph_module_detection.py]
# Por brevedad, aquí solo muestro las funciones clave. En la versión completa,
# copiarías todas las funciones del archivo graph_module_detection.py

# ================================================================================================
# CARGA DE DATOS DESDE CSV
# ================================================================================================

print("\n📁 CARGANDO DATOS...")

# Rutas
data_folder = '/content/tower_data'

# Cargar oriented_lines
oriented_lines_csv = os.path.join(data_folder, 'oriented_lines.csv')
df_lines = pd.read_csv(oriented_lines_csv)
oriented_lines = [(row['x1'], row['y1'], row['z1'], row['x2'], row['y2'], row['z2'])
                  for _, row in df_lines.iterrows()]

# Cargar sections
sections_csv = os.path.join(data_folder, 'sections.csv')
df_sections = pd.read_csv(sections_csv)

# Convertir DataFrame de sections a lista de diccionarios
sections = []
for _, row in df_sections.iterrows():
    sections.append({
        'altura_inicio': row['altura_inicio'],
        'altura_fin': row['altura_fin'],
        'altura_tramo': row['altura_tramo'],
        'tipo': row['tipo']
    })

# Obtener symmetry_axis (debería estar en algún archivo o calcularlo)
# Por ahora, asumamos que está en una variable o calcularlo del modelo
try:
    # Intentar cargar desde archivo si existe
    symmetry_axis_file = os.path.join(data_folder, 'symmetry_axis.txt')
    if os.path.exists(symmetry_axis_file):
        with open(symmetry_axis_file, 'r') as f:
            symmetry_axis = float(f.read().strip())
    else:
        # Calcular como punto medio del ancho del modelo
        all_x = [line[0] for line in oriented_lines] + [line[3] for line in oriented_lines]
        symmetry_axis = (min(all_x) + max(all_x)) / 2
except:
    # Valor por defecto si no se puede calcular
    symmetry_axis = 0.0

print(f"✅ Datos cargados:")
print(f"   • Líneas orientadas: {len(oriented_lines)}")
print(f"   • Secciones: {len(sections)}")
print(f"   • Eje de simetría: X = {symmetry_axis:.3f}")

# ================================================================================================
# CREAR GRAFO DESDE LÍNEAS
# ================================================================================================

print("\n🔧 CREANDO GRAFO...")

G = crear_grafo_desde_lineas(oriented_lines)

print(f"✅ Grafo creado:")
print(f"   • Nodos: {G.number_of_nodes()}")
print(f"   • Aristas: {G.number_of_edges()}")

# ================================================================================================
# ANALIZAR TODAS LAS SECCIONES CON NUEVA ESTRATEGIA DE GRAFOS
# ================================================================================================

print("\n🚀 INICIANDO ANÁLISIS CON ESTRATEGIA DE GRAFOS...")

sections_con_modulos = analizar_todas_secciones_con_grafo(
    G,
    sections,
    symmetry_axis,
    tolerance=0.05
)

# ================================================================================================
# GUARDAR RESULTADOS
# ================================================================================================

print("\n💾 GUARDANDO RESULTADOS...")

# Crear DataFrame con resultados
resultados = []

for i, section in enumerate(sections_con_modulos):
    for j, altura_modulo in enumerate(section.get('alturas_modulos', [])):
        limites = section.get('limites_modulos', [])

        resultados.append({
            'Tramo': i + 1,
            'Tipo': section['tipo'],
            'Altura_Tramo': section['altura_tramo'],
            'Y_Inicio_Tramo': section['altura_inicio'],
            'Y_Fin_Tramo': section['altura_fin'],
            'Num_Modulos': section['num_modulos'],
            'Metodo_Deteccion': section['metodo_deteccion'],
            'Tiene_Modulo_X': section.get('tiene_modulo_x', False),
            'Modulo': j + 1,
            'Altura_Modulo': altura_modulo,
            'Y_Inicio_Modulo': limites[j] if j < len(limites) else None,
            'Y_Fin_Modulo': limites[j+1] if j+1 < len(limites) else None
        })

df_resultados = pd.DataFrame(resultados)

# Guardar a CSV
output_csv = os.path.join(data_folder, 'modulos_con_grafo.csv')
df_resultados.to_csv(output_csv, index=False)

print(f"✅ Resultados guardados en: {output_csv}")

# ================================================================================================
# MOSTRAR RESUMEN FINAL
# ================================================================================================

print("\n" + "="*60)
print("📊 RESUMEN FINAL")
print("="*60)

total_modulos = sum(s['num_modulos'] for s in sections_con_modulos)
secciones_con_x = sum(1 for s in sections_con_modulos if s.get('tiene_modulo_x', False))

print(f"\n✅ Total de módulos detectados: {total_modulos}")
print(f"✅ Secciones con módulo X: {secciones_con_x}/{len(sections)}")

print(f"\n📋 Detalle por sección:")
for i, section in enumerate(sections_con_modulos):
    tipo = section['tipo']
    num_mod = section['num_modulos']
    metodo = section['metodo_deteccion']
    tiene_x = "✅ X" if section.get('tiene_modulo_x', False) else "➖"

    print(f"   {tiene_x} Sección {i+1} ({tipo}): {num_mod} módulos [{metodo}]")

print("\n" + "="*60)
print("✅ ANÁLISIS CON ESTRATEGIA DE GRAFOS COMPLETADO")
print("="*60)

# ================================================================================================
# COMPARACIÓN CON MÉTODO ANTERIOR (si está disponible)
# ================================================================================================

try:
    # Intentar cargar resultados del método anterior si existe
    old_results_csv = os.path.join(data_folder, 'modulos_torre_universal.csv')

    if os.path.exists(old_results_csv):
        df_old = pd.read_csv(old_results_csv)

        # Agrupar por tramo
        old_modules_per_section = df_old.groupby('Tramo')['Modulo'].max().tolist()
        new_modules_per_section = [s['num_modulos'] for s in sections_con_modulos]

        print("\n📊 COMPARACIÓN: Método Anterior vs. Estrategia de Grafos")
        print("="*60)

        for i in range(len(sections_con_modulos)):
            old_count = old_modules_per_section[i] if i < len(old_modules_per_section) else 0
            new_count = new_modules_per_section[i]
            diff = new_count - old_count

            if diff > 0:
                symbol = "📈"
            elif diff < 0:
                symbol = "📉"
            else:
                symbol = "➡️"

            print(f"   {symbol} Sección {i+1}: {old_count} → {new_count} módulos (diff: {diff:+d})")

        print("\n💡 Interpretación:")
        if sum(new_modules_per_section) > sum(old_modules_per_section):
            print("   ✅ La estrategia de grafos detectó MÁS módulos (mejor granularidad)")
        elif sum(new_modules_per_section) < sum(old_modules_per_section):
            print("   ℹ️ La estrategia de grafos detectó MENOS módulos (mejor consolidación)")
        else:
            print("   ➡️ Ambos métodos detectaron la misma cantidad de módulos")

except Exception as e:
    print(f"\n💡 No se pudo comparar con método anterior: {e}")

print("\n🎯 Datos finales disponibles en:")
print(f"   • sections_con_modulos (variable Python)")
print(f"   • {output_csv} (archivo CSV)")
print(f"   • df_resultados (DataFrame de pandas)")

# ================================================================================================
# FIN DE LA CELDA DE ANÁLISIS
# ================================================================================================
