# ================================================================================================
# CELDA AUTOCONTENIDA - ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS
# ================================================================================================
# Esta celda incluye TODAS las funciones necesarias - no requiere archivos externos
# ================================================================================================

import networkx as nx
import numpy as np
import math
import pandas as pd
import os
from typing import List, Tuple, Dict

print("🚀 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS (AUTOCONTENIDO)")
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


def detectar_modulos_x_por_nodos(G: nx.Graph, section_bounds: Tuple,
                                 symmetry_axis: float, tolerance: float = 0.05) -> Dict:
    """Detecta módulos X buscando nodos de alto grado cerca del eje de simetría."""
    y_start, y_end = section_bounds
    candidatos = []

    for node in G.nodes():
        if len(node) >= 2:
            x, y = node[0], node[1]
            grado = G.degree(node)
            distancia_al_eje = abs(x - symmetry_axis)

            if (grado >= 5 and
                y_start <= y <= y_end and
                distancia_al_eje < tolerance * 10):

                candidatos.append({
                    'nodo': node,
                    'x': x,
                    'y': y,
                    'grado': grado,
                    'distancia_eje': distancia_al_eje
                })

    if not candidatos:
        return {'detected': False, 'candidates': 0, 'x_centers': [], 'num_x_modules': 0}

    centros_modulo_x = []

    for candidato in candidatos:
        nodo_central = candidato['nodo']
        vecinos = list(G.neighbors(nodo_central))

        pares_colineales = []
        for i, v1 in enumerate(vecinos):
            for j, v2 in enumerate(vecinos[i+1:], i+1):
                if son_colineales(v1, nodo_central, v2, 5.0):
                    pares_colineales.append((v1, v2))

        if len(pares_colineales) >= 2:
            tiene_diagonales = False
            for v1, v2 in pares_colineales:
                if not es_horizontal((v1, v2), tolerance):
                    tiene_diagonales = True
                    break

            if tiene_diagonales:
                centros_modulo_x.append(candidato)

    return {
        'detected': len(centros_modulo_x) > 0,
        'candidates': len(candidatos),
        'x_centers': centros_modulo_x,
        'num_x_modules': len(centros_modulo_x)
    }


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

    # Por simplicidad, retornar info básica de cada segmento
    diagonales = []
    for seg in segmentos_diagonales:
        n1, n2 = seg
        diagonales.append({
            'segmentos': [seg],
            'extremo_inicio': n1,
            'extremo_fin': n2,
            'y_min': min(n1[1], n2[1]),
            'y_max': max(n1[1], n2[1]),
            'num_segmentos': 1
        })

    return diagonales


def obtener_horizontales_de_grafo(G: nx.Graph, section_bounds: Tuple,
                                  tolerance: float = 0.01) -> List[Tuple]:
    """Obtiene horizontales del grafo."""
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


def filtrar_horizontales_divididas(horizontales: List[Tuple], G: nx.Graph,
                                  tolerance: float = 0.05) -> List[Tuple]:
    """Filtra horizontales divididas en módulos X."""
    horizontales_validas = []

    for horizontal in horizontales:
        x1, y1, z1, x2, y2, z2 = horizontal
        p1 = (x1, y1, z1)
        p2 = (x2, y2, z2)
        es_dividida = False

        for punto in [p1, p2]:
            if punto in G.nodes():
                grado = G.degree(punto)
                if grado >= 5:
                    vecinos = list(G.neighbors(punto))
                    pares_colineales = []
                    for i, v1 in enumerate(vecinos):
                        for j, v2 in enumerate(vecinos[i+1:], i+1):
                            if son_colineales(v1, punto, v2, 5.0):
                                pares_colineales.append((v1, v2))

                    if len(pares_colineales) >= 2:
                        for v1, v2 in pares_colineales:
                            if not es_horizontal((v1, v2), tolerance):
                                es_dividida = True
                                break
                    if es_dividida:
                        break

        if not es_dividida:
            horizontales_validas.append(horizontal)

    return horizontales_validas


def analizar_seccion_con_grafo(G: nx.Graph, section: Dict, symmetry_axis: float,
                               tolerance: float = 0.05, verbose: bool = True) -> Dict:
    """Analiza una sección usando estructura de grafo."""
    y_start = section["altura_inicio"]
    y_end = section["altura_fin"]
    section_height = section["altura_tramo"]
    section_type = section["tipo"]

    if verbose:
        print(f"\n🔧 ANÁLISIS CON GRAFO - Sección {section_type}")
        print(f"    📏 Y: [{y_start:.3f} - {y_end:.3f}], h: {section_height:.3f}")

    deteccion_x = detectar_modulos_x_por_nodos(G, (y_start, y_end), symmetry_axis, tolerance)

    if verbose:
        print(f"    🔍 Candidatos de grado alto: {deteccion_x['candidates']}")
        print(f"    🎯 Módulos X detectados: {deteccion_x['num_x_modules']}")

    if deteccion_x['detected']:
        if verbose:
            print(f"    ✅ Estrategia: DIAGONALES (módulo X detectado)")

        diagonales_completas = reconstruir_diagonales_completas(G, (y_start, y_end), symmetry_axis, tolerance)

        if verbose:
            print(f"    📊 Diagonales reconstruidas: {len(diagonales_completas)}")

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
            'tiene_modulo_x': True
        }
    else:
        if verbose:
            print(f"    ➖ Estrategia: HORIZONTALES (sin módulo X)")

        horizontales = obtener_horizontales_de_grafo(G, (y_start, y_end), tolerance)

        if verbose:
            print(f"    📊 Horizontales encontradas: {len(horizontales)}")

        horizontales_validas = filtrar_horizontales_divididas(horizontales, G, tolerance)

        if verbose:
            print(f"    ✅ Horizontales válidas: {len(horizontales_validas)}")

        alturas_modulos = set([y_start, y_end])
        for horizontal in horizontales_validas:
            y_h = (horizontal[1] + horizontal[4]) / 2
            alturas_modulos.add(y_h)

        alturas_modulos = sorted(list(alturas_modulos))

        return {
            'metodo': 'grafo-horizontal',
            'alturas': alturas_modulos,
            'num_modulos': len(alturas_modulos) - 1,
            'horizontales': horizontales_validas,
            'tiene_modulo_x': False
        }


def analizar_todas_secciones_con_grafo(G: nx.Graph, sections: List[Dict],
                                       symmetry_axis: float, tolerance: float = 0.05) -> List[Dict]:
    """Analiza todas las secciones."""
    print("\n" + "="*60)
    print("🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS")
    print("="*60)

    sections_con_modulos = []

    for i, section in enumerate(sections):
        print(f"\n📍 SECCIÓN {i+1}/{len(sections)}")
        resultado = analizar_seccion_con_grafo(G, section, symmetry_axis, tolerance, verbose=True)

        section_actualizada = section.copy()
        section_actualizada['num_modulos'] = resultado['num_modulos']
        section_actualizada['limites_modulos'] = resultado['alturas']
        section_actualizada['metodo_deteccion'] = resultado['metodo']
        section_actualizada['tiene_modulo_x'] = resultado['tiene_modulo_x']

        alturas = resultado['alturas']
        section_actualizada['alturas_modulos'] = [
            round(alturas[i+1] - alturas[i], 3) for i in range(len(alturas) - 1)
        ]

        sections_con_modulos.append(section_actualizada)

        print(f"    🎉 RESULTADO: {resultado['num_modulos']} módulos [{resultado['metodo']}]")

    print("\n" + "="*60)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*60)

    total_modulos = sum(s['num_modulos'] for s in sections_con_modulos)
    print(f"\n📊 Total de módulos: {total_modulos}")

    return sections_con_modulos


# ================================================================================================
# EJECUTAR ANÁLISIS
# ================================================================================================

print("\n📁 CARGANDO DATOS...")

data_folder = '/content/tower_data'

# Cargar líneas
df_lines = pd.read_csv(os.path.join(data_folder, 'oriented_lines.csv'))
oriented_lines = [(row['x1'], row['y1'], row['z1'], row['x2'], row['y2'], row['z2'])
                  for _, row in df_lines.iterrows()]

# Cargar secciones
df_sections = pd.read_csv(os.path.join(data_folder, 'sections.csv'))
sections = []
for _, row in df_sections.iterrows():
    sections.append({
        'altura_inicio': row['altura_inicio'],
        'altura_fin': row['altura_fin'],
        'altura_tramo': row['altura_tramo'],
        'tipo': row['tipo']
    })

# Calcular eje de simetría
all_x = [line[0] for line in oriented_lines] + [line[3] for line in oriented_lines]
symmetry_axis = (min(all_x) + max(all_x)) / 2

print(f"✅ Líneas: {len(oriented_lines)}, Secciones: {len(sections)}, Eje: {symmetry_axis:.3f}")

# Crear grafo
print("\n🔧 Creando grafo...")
G = crear_grafo_desde_lineas(oriented_lines)
print(f"✅ Grafo: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

# Analizar
sections_con_modulos = analizar_todas_secciones_con_grafo(G, sections, symmetry_axis)

# Guardar
output_csv = os.path.join(data_folder, 'modulos_con_grafo.csv')
resultados = []
for i, section in enumerate(sections_con_modulos):
    limites = section.get('limites_modulos', [])
    for j, h in enumerate(section.get('alturas_modulos', [])):
        resultados.append({
            'Tramo': i+1,
            'Tipo': section['tipo'],
            'Modulo': j+1,
            'Altura': h,
            'Y_Inicio': limites[j] if j < len(limites) else None,
            'Y_Fin': limites[j+1] if j+1 < len(limites) else None,
            'Metodo': section['metodo_deteccion'],
            'Tiene_X': section.get('tiene_modulo_x', False)
        })

pd.DataFrame(resultados).to_csv(output_csv, index=False)
print(f"\n✅ Guardado en: {output_csv}")
print(f"\n📊 Variables: G, sections_con_modulos")
