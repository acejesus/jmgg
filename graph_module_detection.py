"""
================================================================================================
DETECCIÓN DE MÓDULOS USANDO ANÁLISIS DE GRAFOS
================================================================================================
Este módulo implementa estrategias de detección de módulos basadas en la estructura del grafo,
reemplazando las estrategias anteriores que asumían líneas continuas.

PROBLEMA RESUELTO:
- Las líneas ahora están divididas en segmentos en el grafo
- Las horizontales en módulos X están divididas en 2 (nodo grado 6)
- Las diagonales en módulos X están divididas en 2 (nodo grado 6)
- Las estrategias anteriores (líneas continuas) no funcionan

NUEVA ESTRATEGIA:
- Detectar módulos X por nodos de alto grado (5-6)
- Reconstruir diagonales completas siguiendo segmentos colineales
- Filtrar horizontales divididas (no definen módulos)
- Usar extremos de diagonales reconstruidas para definir alturas

Autor: Claude Code
Versión: 1.0
================================================================================================
"""

import networkx as nx
import numpy as np
import math
from typing import List, Tuple, Dict, Set, Optional

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
    """
    Crea un grafo de NetworkX desde una lista de líneas.

    Args:
        lineas: Lista de tuplas de la forma (x1, y1, z1, x2, y2, z2)
                o lista de pares de puntos [(p1, p2), ...]

    Returns:
        nx.Graph: Grafo con nodos en posiciones y aristas conectando líneas
    """
    G = nx.Graph()

    for linea in lineas:
        if len(linea) == 6:
            # Formato (x1, y1, z1, x2, y2, z2)
            x1, y1, z1, x2, y2, z2 = linea
            p1 = (x1, y1, z1)
            p2 = (x2, y2, z2)
        elif len(linea) == 2:
            # Formato [(p1, p2), ...]
            p1, p2 = linea
        else:
            raise ValueError(f"Formato de línea no reconocido: {linea}")

        G.add_node(p1, pos=p1)
        G.add_node(p2, pos=p2)
        G.add_edge(p1, p2)

    return G


# ================================================================================================
# DETECCIÓN DE MÓDULOS X POR NODOS DE ALTO GRADO
# ================================================================================================

def detectar_modulos_x_por_nodos(G: nx.Graph, section_bounds: Tuple,
                                 symmetry_axis: float, tolerance: float = 0.05) -> Dict:
    """
    Detecta módulos X buscando nodos de alto grado cerca del eje de simetría.

    Patrón de módulo X:
    - Nodo central de grado 4-6 (cruce de diagonales + horizontales)
    - Ubicado cerca del eje de simetría
    - Conecta 2 pares de segmentos colineales (las diagonales)
    - Puede conectar horizontales divididas (que ignoramos)

    MEJORAS v1.1:
    - Considera grado >= 4 (no solo >= 5) para mayor flexibilidad
    - Distancia al eje más flexible (30x en vez de 10x)
    - Mejor diagnóstico cuando no encuentra nodos

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        symmetry_axis: Coordenada X del eje de simetría
        tolerance: Tolerancia para cálculos geométricos

    Returns:
        Dict con información del módulo X detectado
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

            # Criterios MEJORADOS para candidatos:
            # - Grado 4, 5 o 6+ (antes solo 5+)
            # - Distancia al eje más flexible (30x en vez de 10x)
            distancia_al_eje = abs(x - symmetry_axis)

            if (grado >= 4 and
                y_start <= y <= y_end and
                distancia_al_eje < tolerance * 30):  # MEJORADO: 30x en vez de 10x

                candidatos.append({
                    'nodo': node,
                    'x': x,
                    'y': y,
                    'grado': grado,
                    'distancia_eje': distancia_al_eje
                })

    # Diagnóstico mejorado si no hay candidatos
    if not candidatos:
        diagnostics = {
            'total_nodes': len(todos_nodos_en_seccion),
            'grade_distribution': {},
            'closest_nodes': []
        }

        # Distribución de grados
        for info in todos_nodos_en_seccion:
            g = info['grado']
            diagnostics['grade_distribution'][g] = diagnostics['grade_distribution'].get(g, 0) + 1

        # Nodos más cercanos al eje
        todos_nodos_en_seccion.sort(key=lambda n: n['distancia_eje'])
        diagnostics['closest_nodes'] = todos_nodos_en_seccion[:10]

        return {
            'detected': False,
            'candidates': 0,
            'x_centers': [],
            'diagnostics': diagnostics
        }

    # Paso 2: Para cada candidato, verificar si es realmente un centro de módulo X
    centros_modulo_x = []

    for candidato in candidatos:
        nodo_central = candidato['nodo']
        vecinos = list(G.neighbors(nodo_central))

        # Analizar vecinos para encontrar pares colineales (tolerancia aumentada)
        pares_colineales = encontrar_pares_colineales(nodo_central, vecinos, tolerance_angulo=10.0)  # MEJORADO: 10° en vez de 5°

        # Un módulo X debería tener al menos 2 pares colineales (las 2 diagonales)
        if len(pares_colineales) >= 2:
            # Verificar que al menos uno de los pares es diagonal (no horizontal)
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


def encontrar_pares_colineales(nodo_central: Tuple, vecinos: List,
                               tolerance_angulo: float = 5.0) -> List[Tuple]:
    """
    Encuentra pares de vecinos que forman líneas colineales pasando por el nodo central.

    Args:
        nodo_central: Nodo del grafo
        vecinos: Lista de vecinos del nodo
        tolerance_angulo: Tolerancia angular en grados

    Returns:
        Lista de tuplas (vecino1, vecino2) que son colineales con nodo_central
    """
    pares = []

    for i, v1 in enumerate(vecinos):
        for j, v2 in enumerate(vecinos[i+1:], i+1):
            # Verificar si v1-nodo_central-v2 son colineales
            if son_colineales(v1, nodo_central, v2, tolerance_angulo):
                pares.append((v1, v2))

    return pares


# ================================================================================================
# RECONSTRUCCIÓN DE DIAGONALES COMPLETAS
# ================================================================================================

def reconstruir_diagonales_completas(G: nx.Graph, section_bounds: Tuple,
                                    symmetry_axis: float, tolerance: float = 0.05) -> List[Dict]:
    """
    Reconstruye diagonales completas siguiendo segmentos colineales en el grafo.

    Esto es crítico para módulos X donde las diagonales están divididas en múltiples segmentos.

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        symmetry_axis: Coordenada X del eje de simetría
        tolerance: Tolerancia para cálculos geométricos

    Returns:
        Lista de diccionarios con información de cada diagonal completa
    """
    y_start, y_end = section_bounds

    # Paso 1: Encontrar todos los segmentos diagonales en la sección
    segmentos_diagonales = []

    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 2 and len(n2) >= 2:
            y1, y2 = n1[1], n2[1]

            # Verificar que está en la sección y NO es horizontal ni vertical
            if (min(y1, y2) >= y_start - tolerance and
                max(y1, y2) <= y_end + tolerance and
                abs(y1 - y2) > tolerance and  # No horizontal
                abs(n1[0] - n2[0]) > tolerance):  # No vertical

                segmentos_diagonales.append(edge)

    if not segmentos_diagonales:
        return []

    # Paso 2: Agrupar segmentos colineales
    diagonales_completas = []
    procesados = set()

    for seg_inicial in segmentos_diagonales:
        if seg_inicial in procesados:
            continue

        # Intentar extender esta diagonal en ambas direcciones
        diagonal_completa = extender_diagonal_bidireccional(
            G, seg_inicial, segmentos_diagonales, tolerance
        )

        diagonales_completas.append(diagonal_completa)
        procesados.update(diagonal_completa['segmentos'])

    return diagonales_completas


def extender_diagonal_bidireccional(G: nx.Graph, segmento_inicial: Tuple,
                                   todos_segmentos: List, tolerance: float = 0.05) -> Dict:
    """
    Extiende una diagonal en ambas direcciones siguiendo segmentos colineales conectados.

    Args:
        G: Grafo de NetworkX
        segmento_inicial: Tupla (nodo1, nodo2) del segmento inicial
        todos_segmentos: Lista de todos los segmentos diagonales
        tolerance: Tolerancia angular en grados

    Returns:
        Dict con información de la diagonal completa
    """
    n1, n2 = segmento_inicial

    # Extender desde n2 hacia adelante
    segmentos_adelante = [segmento_inicial]
    extremo_actual = n2

    while True:
        extendido = False

        for vecino in G.neighbors(extremo_actual):
            siguiente_seg = tuple(sorted([extremo_actual, vecino]))

            # Verificar que es un segmento diagonal y no está procesado
            if siguiente_seg in todos_segmentos or tuple(reversed(siguiente_seg)) in todos_segmentos:
                # Obtener el segmento anterior para verificar colinealidad
                if len(segmentos_adelante) >= 1:
                    seg_anterior = segmentos_adelante[-1]
                    n_prev = seg_anterior[0] if seg_anterior[1] == extremo_actual else seg_anterior[1]

                    # Verificar colinealidad
                    if son_colineales(n_prev, extremo_actual, vecino, tolerancia_angulo=5.0):
                        if siguiente_seg not in segmentos_adelante and tuple(reversed(siguiente_seg)) not in segmentos_adelante:
                            segmentos_adelante.append(siguiente_seg)
                            extremo_actual = vecino
                            extendido = True
                            break

        if not extendido:
            break

    # Extender desde n1 hacia atrás
    segmentos_atras = []
    extremo_actual = n1

    while True:
        extendido = False

        for vecino in G.neighbors(extremo_actual):
            siguiente_seg = tuple(sorted([extremo_actual, vecino]))

            if siguiente_seg in todos_segmentos or tuple(reversed(siguiente_seg)) in todos_segmentos:
                # El segmento original ya está en segmentos_adelante
                if siguiente_seg == segmento_inicial or tuple(reversed(siguiente_seg)) == segmento_inicial:
                    continue

                # Verificar colinealidad
                n_ref = segmento_inicial[1] if segmento_inicial[0] == extremo_actual else segmento_inicial[0]

                if son_colineales(vecino, extremo_actual, n_ref, tolerancia_angulo=5.0):
                    if siguiente_seg not in segmentos_atras and tuple(reversed(siguiente_seg)) not in segmentos_atras:
                        segmentos_atras.insert(0, siguiente_seg)
                        extremo_actual = vecino
                        extendido = True
                        break

        if not extendido:
            break

    # Combinar todos los segmentos
    todos_segmentos_diagonal = segmentos_atras + segmentos_adelante

    # Obtener extremos (simplificado para evitar errores de sintaxis)
    if segmentos_atras:
        # El extremo inicio es el nodo que NO está conectado a otro segmento de la lista
        primer_seg = segmentos_atras[0]
        if len(segmentos_atras) > 1:
            segundo_seg = segmentos_atras[1]
            # El extremo es el nodo del primer segmento que NO coincide con el segundo
            if primer_seg[1] == segundo_seg[0] or primer_seg[1] == segundo_seg[1]:
                extremo_inicio = primer_seg[0]
            else:
                extremo_inicio = primer_seg[1]
        else:
            # Solo hay un segmento atrás, el extremo es el que NO es n1
            extremo_inicio = primer_seg[0] if primer_seg[1] == n1 else primer_seg[1]
    else:
        extremo_inicio = n1

    if segmentos_adelante:
        # El extremo fin es el nodo que NO está conectado a otro segmento de la lista
        ultimo_seg = segmentos_adelante[-1]
        if len(segmentos_adelante) > 1:
            penultimo_seg = segmentos_adelante[-2]
            # El extremo es el nodo del último segmento que NO coincide con el penúltimo
            if ultimo_seg[0] == penultimo_seg[0] or ultimo_seg[0] == penultimo_seg[1]:
                extremo_fin = ultimo_seg[1]
            else:
                extremo_fin = ultimo_seg[0]
        else:
            # Solo hay un segmento adelante, el extremo es el que NO es n2
            extremo_fin = ultimo_seg[1] if ultimo_seg[0] == n2 else ultimo_seg[0]
    else:
        extremo_fin = n2

    # Calcular extremos reales
    nodos_en_diagonal = set()
    for seg in todos_segmentos_diagonal:
        nodos_en_diagonal.add(seg[0])
        nodos_en_diagonal.add(seg[1])

    nodos_lista = list(nodos_en_diagonal)
    y_coords = [n[1] for n in nodos_lista if len(n) >= 2]

    y_min = min(y_coords) if y_coords else extremo_inicio[1]
    y_max = max(y_coords) if y_coords else extremo_fin[1]

    # Encontrar nodos extremos por coordenada Y
    extremo_inicio_final = None
    extremo_fin_final = None

    for nodo in nodos_lista:
        if len(nodo) >= 2:
            if abs(nodo[1] - y_min) < 0.01:
                extremo_inicio_final = nodo
            if abs(nodo[1] - y_max) < 0.01:
                extremo_fin_final = nodo

    return {
        'segmentos': todos_segmentos_diagonal,
        'extremo_inicio': extremo_inicio_final or extremo_inicio,
        'extremo_fin': extremo_fin_final or extremo_fin,
        'y_min': y_min,
        'y_max': y_max,
        'num_segmentos': len(todos_segmentos_diagonal)
    }


# ================================================================================================
# FILTRADO DE HORIZONTALES DIVIDIDAS
# ================================================================================================

def obtener_horizontales_de_grafo(G: nx.Graph, section_bounds: Tuple,
                                  tolerance: float = 0.01) -> List[Tuple]:
    """
    Obtiene todas las horizontales del grafo en una sección específica.

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        tolerance: Tolerancia para determinar si es horizontal

    Returns:
        Lista de tuplas (x1, y1, z1, x2, y2, z2) de líneas horizontales
    """
    y_start, y_end = section_bounds
    horizontales = []

    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 3 and len(n2) >= 3:
            y1, y2 = n1[1], n2[1]
            y_avg = (y1 + y2) / 2

            # Verificar que es horizontal y está en la sección
            if abs(y1 - y2) < tolerance and y_start <= y_avg <= y_end:
                x1, y1, z1 = n1[0], n1[1], n1[2]
                x2, y2, z2 = n2[0], n2[1], n2[2]
                horizontales.append((x1, y1, z1, x2, y2, z2))

    return horizontales


def filtrar_horizontales_divididas(horizontales: List[Tuple], G: nx.Graph,
                                  tolerance: float = 0.05) -> List[Tuple]:
    """
    Filtra horizontales que están divididas en módulos X.

    Criterio: Si una horizontal conecta a un nodo de grado alto (5-6)
    con múltiples pares colineales, probablemente está dividida en un módulo X.

    Args:
        horizontales: Lista de líneas horizontales
        G: Grafo de NetworkX
        tolerance: Tolerancia para cálculos

    Returns:
        Lista de horizontales que NO están divididas
    """
    horizontales_validas = []

    for horizontal in horizontales:
        x1, y1, z1, x2, y2, z2 = horizontal
        p1 = (x1, y1, z1)
        p2 = (x2, y2, z2)

        # Verificar si alguno de los extremos es un nodo de alto grado en cruce de módulo X
        es_dividida = False

        for punto in [p1, p2]:
            if punto in G.nodes():
                grado = G.degree(punto)

                # Si conecta a un nodo de grado 5-6, verificar si es cruce de módulo X
                if grado >= 5:
                    vecinos = list(G.neighbors(punto))
                    pares_colineales = encontrar_pares_colineales(punto, vecinos, 5.0)

                    # Si tiene 2+ pares colineales Y al menos uno es diagonal,
                    # entonces este nodo es un cruce de módulo X
                    if len(pares_colineales) >= 2:
                        tiene_diagonales = False
                        for v1, v2 in pares_colineales:
                            if not es_horizontal((v1, v2), tolerance):
                                tiene_diagonales = True
                                break

                        if tiene_diagonales:
                            es_dividida = True
                            break

        if not es_dividida:
            horizontales_validas.append(horizontal)

    return horizontales_validas


# ================================================================================================
# ANÁLISIS COMPLETO DE SECCIÓN CON GRAFO
# ================================================================================================

def analizar_seccion_con_grafo(G: nx.Graph, section: Dict, symmetry_axis: float,
                               tolerance: float = 0.05, verbose: bool = True) -> Dict:
    """
    Analiza una sección usando la estructura del grafo.

    Estrategia:
    1. Detectar si hay módulos X por nodos de alto grado
    2. Si hay módulos X: usar diagonales reconstruidas
    3. Si no hay módulos X: usar horizontales filtradas

    Args:
        G: Grafo de NetworkX
        section: Diccionario con información de la sección
        symmetry_axis: Coordenada X del eje de simetría
        tolerance: Tolerancia para cálculos
        verbose: Mostrar información detallada

    Returns:
        Dict con resultados del análisis
    """
    y_start = section["altura_inicio"]
    y_end = section["altura_fin"]
    section_height = section["altura_tramo"]
    section_type = section["tipo"]

    if verbose:
        print(f"\n🔧 ANÁLISIS CON GRAFO - Sección {section_type}")
        print(f"    📏 Y: [{y_start:.3f} - {y_end:.3f}], h: {section_height:.3f}")

    # PASO 1: Detectar módulos X por nodos de alto grado
    deteccion_x = detectar_modulos_x_por_nodos(G, (y_start, y_end), symmetry_axis, tolerance)

    if verbose:
        print(f"    🔍 Candidatos de grado alto: {deteccion_x['candidates']}")
        print(f"    🎯 Módulos X detectados: {deteccion_x['num_x_modules'] if deteccion_x['detected'] else 0}")

    if deteccion_x['detected']:
        # HAY MÓDULO X → Usar estrategia de diagonales
        if verbose:
            print(f"    ✅ Estrategia: DIAGONALES (módulo X detectado)")

        # Reconstruir diagonales completas
        diagonales_completas = reconstruir_diagonales_completas(G, (y_start, y_end), symmetry_axis, tolerance)

        if verbose:
            print(f"    📊 Diagonales reconstruidas: {len(diagonales_completas)}")
            for i, diag in enumerate(diagonales_completas):
                print(f"        Diagonal {i+1}: {diag['num_segmentos']} segmentos, Y=[{diag['y_min']:.3f}-{diag['y_max']:.3f}]")

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
            'tiene_modulo_x': True
        }

    else:
        # NO HAY MÓDULO X → Usar estrategia de horizontales
        if verbose:
            print(f"    ➖ Estrategia: HORIZONTALES (sin módulo X)")

        # Obtener horizontales
        horizontales = obtener_horizontales_de_grafo(G, (y_start, y_end), tolerance)

        if verbose:
            print(f"    📊 Horizontales encontradas: {len(horizontales)}")

        # Filtrar horizontales divididas
        horizontales_validas = filtrar_horizontales_divididas(horizontales, G, tolerance)

        if verbose:
            print(f"    ✅ Horizontales válidas (no divididas): {len(horizontales_validas)}")

        # Usar horizontales para definir módulos
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
    """
    Analiza todas las secciones usando estrategias basadas en grafos.

    Args:
        G: Grafo de NetworkX
        sections: Lista de secciones a analizar
        symmetry_axis: Coordenada X del eje de simetría
        tolerance: Tolerancia para cálculos

    Returns:
        Lista de secciones con información de módulos detectados
    """
    print("\n" + "="*60)
    print("🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS")
    print("="*60)

    sections_con_modulos = []

    for i, section in enumerate(sections):
        print(f"\n📍 SECCIÓN {i+1}/{len(sections)}")

        # Analizar sección con grafo
        resultado = analizar_seccion_con_grafo(G, section, symmetry_axis, tolerance, verbose=True)

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

        sections_con_modulos.append(section_actualizada)

        # Mostrar resumen
        print(f"    🎉 RESULTADO: {resultado['num_modulos']} módulos [{resultado['metodo']}]")

        if resultado['num_modulos'] <= 10:
            for j in range(resultado['num_modulos']):
                h = section_actualizada['alturas_modulos'][j]
                y_ini = alturas[j]
                y_fin = alturas[j+1]
                prefix = "D" if 'diagonal' in resultado['metodo'] else "H"
                print(f"        {prefix}{j+1}: h={h:.3f}, Y=[{y_ini:.3f}-{y_fin:.3f}]")

    print("\n" + "="*60)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*60)

    total_modulos = sum(s['num_modulos'] for s in sections_con_modulos)
    metodos = {}
    for s in sections_con_modulos:
        metodo = s['metodo_deteccion']
        metodos[metodo] = metodos.get(metodo, 0) + 1

    print(f"\n📊 RESUMEN:")
    print(f"   • Total de módulos: {total_modulos}")
    print(f"   • Distribución de métodos:")
    for metodo, count in metodos.items():
        print(f"      - {metodo}: {count} secciones")

    return sections_con_modulos


if __name__ == "__main__":
    print("📦 Módulo de detección de módulos con grafos cargado correctamente")
    print("\n🎯 Funciones principales:")
    print("   • detectar_modulos_x_por_nodos() - Detectar módulos X por grado de nodos")
    print("   • reconstruir_diagonales_completas() - Reconstruir diagonales desde segmentos")
    print("   • filtrar_horizontales_divididas() - Filtrar horizontales en módulos X")
    print("   • analizar_seccion_con_grafo() - Analizar una sección completa")
    print("   • analizar_todas_secciones_con_grafo() - Analizar todas las secciones")
