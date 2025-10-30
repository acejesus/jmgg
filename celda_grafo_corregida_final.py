# ================================================================================================
# CELDA FINAL: ANÁLISIS DE MÓDULOS CON GRAFOS (VERSIÓN CORREGIDA)
# ================================================================================================
# CORRECCIÓN:
# - Agrupa diagonales colineales para definir módulos X correctamente
# - Cada módulo X tiene 4 diagonales (2 pares colineales) -> 1 módulo
# - Visualización mejorada sin panel de texto
# ================================================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import math
import pandas as pd
import os
from typing import List, Tuple, Dict

print("🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS (VERSIÓN CORREGIDA)")
print("="*60)

# ================================================================================================
# FUNCIONES AUXILIARES
# ================================================================================================

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


def es_vertical(edge, tolerance=0.01):
    """Determina si una arista es vertical."""
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        return abs(n1[0] - n2[0]) < tolerance
    return False


def crear_grafo_desde_lineas(lineas: List[Tuple]) -> nx.Graph:
    """Crea un grafo de NetworkX desde una lista de líneas."""
    G = nx.Graph()

    for linea in lineas:
        if len(linea) == 6:
            x1, y1, z1, x2, y2, z2 = linea
            p1 = (x1, y1, z1)
            p2 = (x2, y2, z2)
        elif len(linea) == 2:
            p1, p2 = linea
        else:
            raise ValueError(f"Formato de línea no reconocido: {linea}")

        G.add_node(p1, pos=p1)
        G.add_node(p2, pos=p2)
        G.add_edge(p1, p2)

    return G


def encontrar_pares_colineales(nodo_central: Tuple, vecinos: List,
                               tolerance_angulo: float = 5.0) -> List[Tuple]:
    """Encuentra pares de vecinos que forman líneas colineales pasando por el nodo central."""
    pares = []

    for i, v1 in enumerate(vecinos):
        for j, v2 in enumerate(vecinos[i+1:], i+1):
            if son_colineales(v1, nodo_central, v2, tolerance_angulo):
                pares.append((v1, v2))

    return pares


# ================================================================================================
# DETECCIÓN MEJORADA DE MÓDULOS X
# ================================================================================================

def detectar_modulos_x_mejorado(G: nx.Graph, section_bounds: Tuple,
                                symmetry_axis: float, tolerance: float = 0.05) -> Dict:
    """Detecta módulos X buscando nodos de alto grado cerca del eje de simetría."""
    y_start, y_end = section_bounds

    # Encontrar nodos candidatos
    candidatos = []

    for node in G.nodes():
        if len(node) >= 2:
            x, y = node[0], node[1]
            grado = G.degree(node)

            distancia_al_eje = abs(x - symmetry_axis)

            if (grado >= 4 and
                y_start <= y <= y_end and
                distancia_al_eje < tolerance * 30):

                candidatos.append({
                    'nodo': node,
                    'x': x,
                    'y': y,
                    'grado': grado,
                    'distancia_eje': distancia_al_eje
                })

    if not candidatos:
        return {
            'detected': False,
            'candidates': 0,
            'x_centers': []
        }

    # Verificar cuáles son realmente centros de módulo X
    centros_modulo_x = []

    for candidato in candidatos:
        nodo_central = candidato['nodo']
        vecinos = list(G.neighbors(nodo_central))

        pares_colineales = encontrar_pares_colineales(nodo_central, vecinos, tolerance_angulo=10.0)

        if len(pares_colineales) >= 2:
            tiene_diagonales = False
            for v1, v2 in pares_colineales:
                if not es_horizontal((v1, v2), tolerance):
                    tiene_diagonales = True
                    break

            if tiene_diagonales:
                candidato['pares_colineales'] = pares_colineales
                centros_modulo_x.append(candidato)

    return {
        'detected': len(centros_modulo_x) > 0,
        'candidates': len(candidatos),
        'x_centers': centros_modulo_x,
        'num_x_modules': len(centros_modulo_x)
    }


# ================================================================================================
# RECONSTRUCCIÓN DE DIAGONALES (AGRUPADAS POR ALTURA)
# ================================================================================================

def obtener_alturas_de_diagonales(G: nx.Graph, section_bounds: Tuple,
                                   symmetry_axis: float, tolerance: float = 0.05) -> List[float]:
    """
    Obtiene las alturas Y únicas donde cambian las diagonales en módulos X.

    CORRECCIÓN CLAVE:
    - Cada módulo X tiene 4 diagonales (2 pares colineales)
    - Las diagonales comparten extremos Y (superior e inferior del módulo)
    - Agrupa por coordenadas Y para encontrar límites de módulos
    """
    y_start, y_end = section_bounds

    # Encontrar todos los segmentos diagonales
    alturas_y = set()

    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 2 and len(n2) >= 2:
            y1, y2 = n1[1], n2[1]
            x1, x2 = n1[0], n2[0]

            # Verificar que es diagonal (no horizontal ni vertical)
            if (y_start <= min(y1, y2) and max(y1, y2) <= y_end and
                abs(y1 - y2) > tolerance and  # No horizontal
                abs(x1 - x2) > tolerance):    # No vertical

                # Agregar ambos extremos Y
                alturas_y.add(y1)
                alturas_y.add(y2)

    return sorted(list(alturas_y))


# ================================================================================================
# FILTRADO DE HORIZONTALES
# ================================================================================================

def obtener_horizontales_de_grafo(G: nx.Graph, section_bounds: Tuple,
                                  tolerance: float = 0.01) -> List[Tuple]:
    """Obtiene todas las horizontales del grafo en una sección."""
    y_start, y_end = section_bounds
    horizontales = []

    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 3 and len(n2) >= 3:
            y1, y2 = n1[1], n2[1]
            y_avg = (y1 + y2) / 2

            if abs(y1 - y2) < tolerance and y_start <= y_avg <= y_end:
                x1, y1, z1 = n1[0], n1[1], n1[2]
                x2, y2, z2 = n2[0], n2[1], n2[2]
                horizontales.append((x1, y1, z1, x2, y2, z2))

    return horizontales


# ================================================================================================
# ANÁLISIS DE SECCIÓN CON GRAFO (CORREGIDO)
# ================================================================================================

def analizar_seccion_con_grafo(G: nx.Graph, section: Dict, symmetry_axis: float,
                               tolerance: float = 0.05, verbose: bool = True) -> Dict:
    """Analiza una sección usando la estructura del grafo (VERSIÓN CORREGIDA)."""
    y_start = section["altura_inicio"]
    y_end = section["altura_fin"]
    section_height = section["altura_tramo"]
    section_type = section["tipo"]

    if verbose:
        print(f"\n🔧 ANÁLISIS CON GRAFO - Sección {section_type}")
        print(f"    📏 Y: [{y_start:.3f} - {y_end:.3f}], h: {section_height:.3f}")

    # PASO 1: Detectar módulos X
    deteccion_x = detectar_modulos_x_mejorado(G, (y_start, y_end), symmetry_axis, tolerance)

    if verbose:
        print(f"    🔍 Candidatos de grado alto: {deteccion_x['candidates']}")
        print(f"    🎯 Módulos X detectados: {deteccion_x['num_x_modules'] if deteccion_x['detected'] else 0}")

    if deteccion_x['detected']:
        # HAY MÓDULO X → Usar alturas Y de diagonales (CORREGIDO)
        if verbose:
            print(f"    ✅ Estrategia: DIAGONALES (módulo X detectado)")

        # Obtener alturas únicas de diagonales
        alturas_diagonales = obtener_alturas_de_diagonales(G, (y_start, y_end), symmetry_axis, tolerance)

        if verbose:
            print(f"    📊 Alturas Y de diagonales: {len(alturas_diagonales)}")

        # Agregar límites de sección
        alturas_modulos = sorted(list(set([y_start, y_end] + alturas_diagonales)))

        # CORRECCIÓN: Agrupar alturas muy cercanas (mismo módulo)
        alturas_agrupadas = [alturas_modulos[0]]
        for h in alturas_modulos[1:]:
            if abs(h - alturas_agrupadas[-1]) > tolerance * 2:  # Si están separadas más de 0.1
                alturas_agrupadas.append(h)

        return {
            'metodo': 'grafo-diagonal',
            'alturas': alturas_agrupadas,
            'num_modulos': len(alturas_agrupadas) - 1,
            'tiene_modulo_x': True,
            'x_centers': deteccion_x['x_centers']
        }

    else:
        # NO HAY MÓDULO X → Usar estrategia de horizontales
        if verbose:
            print(f"    ➖ Estrategia: HORIZONTALES (sin módulo X)")

        horizontales = obtener_horizontales_de_grafo(G, (y_start, y_end), tolerance)

        if verbose:
            print(f"    📊 Horizontales encontradas: {len(horizontales)}")

        alturas_modulos = set([y_start, y_end])

        for horizontal in horizontales:
            y_h = (horizontal[1] + horizontal[4]) / 2
            alturas_modulos.add(y_h)

        alturas_modulos = sorted(list(alturas_modulos))

        return {
            'metodo': 'grafo-horizontal',
            'alturas': alturas_modulos,
            'num_modulos': len(alturas_modulos) - 1,
            'horizontales': horizontales,
            'tiene_modulo_x': False
        }


# ================================================================================================
# CARGA DE DATOS DESDE CSV
# ================================================================================================

print("\n📁 CARGANDO DATOS...")

data_folder = '/content/tower_data'

# Cargar oriented_lines
oriented_lines_csv = os.path.join(data_folder, 'oriented_lines.csv')
df_lines = pd.read_csv(oriented_lines_csv)
oriented_lines = [(row['x1'], row['y1'], row['z1'], row['x2'], row['y2'], row['z2'])
                  for _, row in df_lines.iterrows()]

# Cargar sections
sections_csv = os.path.join(data_folder, 'sections.csv')
df_sections = pd.read_csv(sections_csv)
sections = []
for _, row in df_sections.iterrows():
    sections.append({
        'altura_inicio': row['altura_inicio'],
        'altura_fin': row['altura_fin'],
        'altura_tramo': row['altura_tramo'],
        'tipo': row['tipo']
    })

# Calcular symmetry_axis
all_x = [line[0] for line in oriented_lines] + [line[3] for line in oriented_lines]
symmetry_axis = (min(all_x) + max(all_x)) / 2

print(f"✅ Datos cargados:")
print(f"   • Líneas orientadas: {len(oriented_lines)}")
print(f"   • Secciones: {len(sections)}")
print(f"   • Eje de simetría: X = {symmetry_axis:.3f}")

# ================================================================================================
# CREAR GRAFO
# ================================================================================================

print("\n🔧 CREANDO GRAFO...")

G = crear_grafo_desde_lineas(oriented_lines)

print(f"✅ Grafo creado:")
print(f"   • Nodos: {G.number_of_nodes()}")
print(f"   • Aristas: {G.number_of_edges()}")

# ================================================================================================
# ANALIZAR TODAS LAS SECCIONES
# ================================================================================================

print("\n" + "="*60)
print("🚀 INICIANDO ANÁLISIS CON ESTRATEGIA DE GRAFOS...")
print("="*60)

sections_con_modulos = []

for i, section in enumerate(sections):
    print(f"\n📍 SECCIÓN {i+1}/{len(sections)}")

    resultado = analizar_seccion_con_grafo(G, section, symmetry_axis, tolerance=0.05, verbose=True)

    # Crear sección actualizada
    section_actualizada = section.copy()
    section_actualizada['num_modulos'] = resultado['num_modulos']
    section_actualizada['limites_modulos'] = resultado['alturas']
    section_actualizada['metodo_deteccion'] = resultado['metodo']
    section_actualizada['tiene_modulo_x'] = resultado['tiene_modulo_x']

    # Calcular alturas de módulos
    alturas = resultado['alturas']
    section_actualizada['alturas_modulos'] = [
        round(alturas[i+1] - alturas[i], 3) for i in range(len(alturas) - 1)
    ]

    # Guardar centros de X si existen
    if 'x_centers' in resultado:
        section_actualizada['x_centers'] = resultado['x_centers']

    sections_con_modulos.append(section_actualizada)

    print(f"    🎉 RESULTADO: {resultado['num_modulos']} módulos [{resultado['metodo']}]")

print("\n" + "="*60)
print("✅ ANÁLISIS COMPLETADO")
print("="*60)

# ================================================================================================
# VISUALIZACIÓN MEJORADA (SIN PANEL DE TEXTO)
# ================================================================================================

print("\n📊 GENERANDO VISUALIZACIÓN...")

fig, ax = plt.subplots(1, 1, figsize=(14, 16))

ax.set_title('Torre con Secciones y Módulos Detectados', fontsize=18, fontweight='bold', pad=20)

# Dibujar todas las aristas en gris claro
for edge in G.edges():
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        ax.plot([n1[0], n2[0]], [n1[1], n2[1]], 'gray', linewidth=0.5, alpha=0.3)

# Colores para secciones
colores_seccion = ['red', 'blue', 'green', 'orange', 'purple']

# Marcar límites de secciones con líneas más gruesas
for i, section in enumerate(sections_con_modulos):
    y_start = section['altura_inicio']
    y_end = section['altura_fin']
    color = colores_seccion[i % len(colores_seccion)]

    # Línea de inicio de sección (más gruesa)
    ax.axhline(y_start, color=color, linestyle='--', linewidth=3, alpha=0.8,
               label=f"Sección {i+1}: {section['tipo']} ({section['num_modulos']} mód)")

    # Línea de fin de sección
    if i == len(sections_con_modulos) - 1:  # Solo para la última sección
        ax.axhline(y_end, color=color, linestyle='--', linewidth=3, alpha=0.8)

# Marcar alturas de módulos con líneas más finas
for i, section in enumerate(sections_con_modulos):
    alturas = section['limites_modulos']
    color = colores_seccion[i % len(colores_seccion)]

    # Líneas intermedias de módulos (más finas)
    for j, altura in enumerate(alturas[1:-1], 1):  # Excluir primera y última (ya dibujadas)
        ax.axhline(altura, color=color, linestyle=':', linewidth=1.5, alpha=0.6)

        # Etiqueta de altura en el lado derecho
        ax.text(max(all_x) + 0.3, altura, f'Y={altura:.1f}',
                fontsize=9, color=color, va='center')

# Marcar eje de simetría
ax.axvline(symmetry_axis, color='green', linestyle=':', linewidth=2.5, alpha=0.7,
           label=f'Eje simetría X={symmetry_axis:.2f}', zorder=5)

# Marcar centros de módulos X con estrellas rojas
for i, section in enumerate(sections_con_modulos):
    if section.get('tiene_modulo_x') and 'x_centers' in section:
        for centro in section['x_centers']:
            x, y = centro['x'], centro['y']
            ax.scatter(x, y, c='red', s=300, marker='*', edgecolors='black',
                      linewidths=2, zorder=10)

# Configuración de ejes
ax.set_xlabel('X (m)', fontsize=14, fontweight='bold')
ax.set_ylabel('Y (m)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.2)
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax.set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.show()

# ================================================================================================
# RESUMEN FINAL (SOLO TEXTO)
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

    print(f"\n   {tiene_x} Sección {i+1} ({tipo}): {num_mod} módulos [{metodo}]")

    # Mostrar alturas de cada módulo
    if num_mod <= 20:
        alturas = section['limites_modulos']
        for j in range(num_mod):
            h = section['alturas_modulos'][j]
            y_ini = alturas[j]
            y_fin = alturas[j+1]
            print(f"       M{j+1}: h={h:.3f}m, Y=[{y_ini:.3f} - {y_fin:.3f}]")

print("\n" + "="*60)
print("✅ ANÁLISIS CON ESTRATEGIA DE GRAFOS COMPLETADO")
print("="*60)
