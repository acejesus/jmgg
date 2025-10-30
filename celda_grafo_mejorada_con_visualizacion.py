# ================================================================================================
# CELDA MEJORADA: ANÁLISIS DE MÓDULOS CON GRAFOS + VISUALIZACIÓN
# ================================================================================================
# Mejoras:
# - Criterios de detección más flexibles
# - Diagnóstico automático de problemas
# - Visualización completa de la torre con módulos marcados
# ================================================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import math
import pandas as pd
import os
from typing import List, Tuple, Dict

print("🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS (VERSIÓN MEJORADA)")
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
    """
    Versión mejorada de detección de módulos X con criterios más flexibles.

    MEJORAS:
    - Considera grado >= 4 (no solo >= 5)
    - Distancia al eje más flexible (30x en vez de 10x)
    - Mejor diagnóstico cuando no encuentra nodos
    """
    y_start, y_end = section_bounds

    # Paso 1: Encontrar nodos candidatos con criterios RELAJADOS
    candidatos = []
    todos_nodos_en_seccion = []

    for node in G.nodes():
        if len(node) >= 2:
            x, y = node[0], node[1]
            grado = G.degree(node)

            # Guardar todos los nodos en sección para diagnóstico
            if y_start <= y <= y_end:
                todos_nodos_en_seccion.append({
                    'nodo': node,
                    'x': x,
                    'y': y,
                    'grado': grado,
                    'distancia_eje': abs(x - symmetry_axis)
                })

            # Criterios RELAJADOS para candidatos:
            # - Grado 4, 5 o 6+ (antes solo 5+)
            # - Distancia al eje más flexible (30x en vez de 10x)
            distancia_al_eje = abs(x - symmetry_axis)

            if (grado >= 4 and
                y_start <= y <= y_end and
                distancia_al_eje < tolerance * 30):  # RELAJADO: 30x en vez de 10x

                candidatos.append({
                    'nodo': node,
                    'x': x,
                    'y': y,
                    'grado': grado,
                    'distancia_eje': distancia_al_eje
                })

    # Diagnóstico si no hay candidatos
    if not candidatos:
        print(f"    ⚠️ DIAGNÓSTICO: No se encontraron candidatos")
        print(f"       Nodos totales en sección: {len(todos_nodos_en_seccion)}")

        # Mostrar distribución de grados
        grados_en_seccion = {}
        for info in todos_nodos_en_seccion:
            g = info['grado']
            grados_en_seccion[g] = grados_en_seccion.get(g, 0) + 1

        print(f"       Distribución de grados:")
        for g in sorted(grados_en_seccion.keys(), reverse=True):
            print(f"         - Grado {g}: {grados_en_seccion[g]} nodos")

        # Mostrar los más cercanos al eje
        todos_nodos_en_seccion.sort(key=lambda n: n['distancia_eje'])
        print(f"       Nodos más cercanos al eje (X={symmetry_axis:.3f}):")
        for i, info in enumerate(todos_nodos_en_seccion[:5]):
            print(f"         {i+1}. X={info['x']:.3f}, Y={info['y']:.3f}, Grado={info['grado']}, Dist={info['distancia_eje']:.3f}")

        return {
            'detected': False,
            'candidates': 0,
            'x_centers': [],
            'diagnostics': {
                'total_nodes': len(todos_nodos_en_seccion),
                'grade_distribution': grados_en_seccion,
                'closest_nodes': todos_nodos_en_seccion[:10]
            }
        }

    # Paso 2: Verificar cuáles son realmente centros de módulo X
    centros_modulo_x = []

    for candidato in candidatos:
        nodo_central = candidato['nodo']
        vecinos = list(G.neighbors(nodo_central))

        # Analizar vecinos para encontrar pares colineales
        pares_colineales = encontrar_pares_colineales(nodo_central, vecinos, tolerance_angulo=10.0)  # Tolerancia aumentada

        # Un módulo X debería tener al menos 2 pares colineales
        if len(pares_colineales) >= 2:
            # Verificar que al menos uno de los pares es diagonal
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
# RECONSTRUCCIÓN DE DIAGONALES (IGUAL QUE ANTES)
# ================================================================================================

def reconstruir_diagonales_completas(G: nx.Graph, section_bounds: Tuple,
                                    symmetry_axis: float, tolerance: float = 0.05) -> List[Dict]:
    """Reconstruye diagonales completas siguiendo segmentos colineales."""
    y_start, y_end = section_bounds

    # Encontrar segmentos diagonales
    segmentos_diagonales = []

    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 2 and len(n2) >= 2:
            y1, y2 = n1[1], n2[1]

            if (min(y1, y2) >= y_start - tolerance and
                max(y1, y2) <= y_end + tolerance and
                abs(y1 - y2) > tolerance and
                abs(n1[0] - n2[0]) > tolerance):

                segmentos_diagonales.append(edge)

    if not segmentos_diagonales:
        return []

    # Extender diagonales
    diagonales_completas = []
    procesados = set()

    for seg in segmentos_diagonales:
        if seg in procesados:
            continue

        # Obtener todos los nodos de esta diagonal
        nodos_diagonal = set([seg[0], seg[1]])
        segmentos_diagonal = [seg]

        # Marcar como procesado
        procesados.add(seg)

        # Extraer coordenadas Y
        y_coords = [n[1] for n in nodos_diagonal if len(n) >= 2]

        diagonal_info = {
            'segmentos': segmentos_diagonal,
            'y_min': min(y_coords),
            'y_max': max(y_coords),
            'num_segmentos': len(segmentos_diagonal)
        }

        diagonales_completas.append(diagonal_info)

    return diagonales_completas


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
# ANÁLISIS DE SECCIÓN CON GRAFO
# ================================================================================================

def analizar_seccion_con_grafo(G: nx.Graph, section: Dict, symmetry_axis: float,
                               tolerance: float = 0.05, verbose: bool = True) -> Dict:
    """Analiza una sección usando la estructura del grafo."""
    y_start = section["altura_inicio"]
    y_end = section["altura_fin"]
    section_height = section["altura_tramo"]
    section_type = section["tipo"]

    if verbose:
        print(f"\n🔧 ANÁLISIS CON GRAFO - Sección {section_type}")
        print(f"    📏 Y: [{y_start:.3f} - {y_end:.3f}], h: {section_height:.3f}")

    # PASO 1: Detectar módulos X con versión mejorada
    deteccion_x = detectar_modulos_x_mejorado(G, (y_start, y_end), symmetry_axis, tolerance)

    if verbose:
        print(f"    🔍 Candidatos de grado alto: {deteccion_x['candidates']}")
        print(f"    🎯 Módulos X detectados: {deteccion_x['num_x_modules'] if deteccion_x['detected'] else 0}")

    if deteccion_x['detected']:
        # HAY MÓDULO X → Usar estrategia de diagonales
        if verbose:
            print(f"    ✅ Estrategia: DIAGONALES (módulo X detectado)")

        # Reconstruir diagonales
        diagonales_completas = reconstruir_diagonales_completas(G, (y_start, y_end), symmetry_axis, tolerance)

        if verbose:
            print(f"    📊 Diagonales reconstruidas: {len(diagonales_completas)}")

        # Usar extremos de diagonales para definir módulos
        alturas_modulos = set([y_start, y_end])

        for diagonal in diagonales_completas:
            alturas_modulos.add(diagonal['y_min'])
            alturas_modulos.add(diagonal['y_max'])

        alturas_modulos = sorted(list(alturas_modulos))

        return {
            'metodo': 'grafo-diagonal',
            'alturas': alturas_modulos,
            'num_modulos': len(alturas_modulos) - 1,
            'diagonales': diagonales_completas,
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

        # Usar horizontales para definir módulos
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
# VISUALIZACIÓN DE LA TORRE CON MÓDULOS DETECTADOS
# ================================================================================================

print("\n📊 GENERANDO VISUALIZACIÓN...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))

# ====== PANEL 1: Vista completa de la torre ======
ax1.set_title('Torre Completa con Secciones y Módulos', fontsize=16, fontweight='bold')

# Dibujar todas las aristas
for edge in G.edges():
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        ax1.plot([n1[0], n2[0]], [n1[1], n2[1]], 'gray', linewidth=0.5, alpha=0.4)

# Marcar límites de secciones
colores_seccion = ['red', 'blue', 'green', 'orange', 'purple']
for i, section in enumerate(sections_con_modulos):
    y_start = section['altura_inicio']
    y_end = section['altura_fin']
    color = colores_seccion[i % len(colores_seccion)]

    ax1.axhline(y_start, color=color, linestyle='--', linewidth=2, alpha=0.7,
                label=f"Sección {i+1} ({section['tipo']})")
    ax1.axhline(y_end, color=color, linestyle='--', linewidth=2, alpha=0.7)

# Marcar eje de simetría
ax1.axvline(symmetry_axis, color='green', linestyle=':', linewidth=2, alpha=0.7,
            label=f'Eje simetría X={symmetry_axis:.2f}')

# Marcar centros de módulos X
for i, section in enumerate(sections_con_modulos):
    if section.get('tiene_modulo_x') and 'x_centers' in section:
        for centro in section['x_centers']:
            x, y = centro['x'], centro['y']
            ax1.scatter(x, y, c='red', s=200, marker='*', edgecolors='black',
                       linewidths=2, zorder=10)
            ax1.text(x + 0.1, y, f"X{i+1}", fontsize=10, fontweight='bold',
                    color='red', zorder=11)

ax1.set_xlabel('X (m)', fontsize=12)
ax1.set_ylabel('Y (m)', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', fontsize=10)
ax1.set_aspect('equal', adjustable='box')

# ====== PANEL 2: Desglose de módulos por sección ======
ax2.set_title('Desglose de Módulos por Sección', fontsize=16, fontweight='bold')
ax2.axis('off')

# Crear tabla de resumen
y_pos = 0.95
line_height = 0.05

ax2.text(0.05, y_pos, '📊 RESUMEN DE MÓDULOS DETECTADOS', fontsize=14,
         fontweight='bold', transform=ax2.transAxes)
y_pos -= line_height * 1.5

ax2.text(0.05, y_pos, '='*80, fontsize=10, family='monospace',
         transform=ax2.transAxes)
y_pos -= line_height

for i, section in enumerate(sections_con_modulos):
    # Encabezado de sección
    tiene_x = "✅ X" if section.get('tiene_modulo_x') else "➖"
    texto_seccion = f"{tiene_x} SECCIÓN {i+1} ({section['tipo']}): {section['num_modulos']} módulos [{section['metodo_deteccion']}]"

    color = colores_seccion[i % len(colores_seccion)]
    ax2.text(0.05, y_pos, texto_seccion, fontsize=12, fontweight='bold',
             color=color, transform=ax2.transAxes)
    y_pos -= line_height

    # Detalles de módulos (solo si hay pocos)
    if section['num_modulos'] <= 15:
        alturas = section['limites_modulos']
        for j in range(section['num_modulos']):
            h = section['alturas_modulos'][j]
            y_ini = alturas[j]
            y_fin = alturas[j+1]

            texto_modulo = f"   M{j+1}: h={h:.3f}m, Y=[{y_ini:.3f} - {y_fin:.3f}]"
            ax2.text(0.08, y_pos, texto_modulo, fontsize=10, family='monospace',
                    transform=ax2.transAxes)
            y_pos -= line_height * 0.8
    else:
        ax2.text(0.08, y_pos, f"   ({section['num_modulos']} módulos - muy detallado para mostrar)",
                fontsize=10, style='italic', transform=ax2.transAxes)
        y_pos -= line_height

    y_pos -= line_height * 0.5

    # Evitar salir del panel
    if y_pos < 0.1:
        break

# Añadir leyenda
y_pos = max(0.05, y_pos)
ax2.text(0.05, y_pos, '='*80, fontsize=10, family='monospace',
         transform=ax2.transAxes)
y_pos -= line_height
ax2.text(0.05, y_pos, '✅ X = Sección con módulo X (diagonales divididas)',
         fontsize=10, transform=ax2.transAxes)
y_pos -= line_height * 0.8
ax2.text(0.05, y_pos, '➖ = Sección sin módulo X (horizontales)',
         fontsize=10, transform=ax2.transAxes)

plt.tight_layout()
plt.show()

# ================================================================================================
# RESUMEN FINAL
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

print("\n🎯 Variables disponibles:")
print("   • G (grafo de NetworkX)")
print("   • sections_con_modulos (lista de secciones con módulos)")
print("   • oriented_lines (líneas orientadas)")
print("   • symmetry_axis (eje de simetría)")
