# ================================================================================================
# ANÁLISIS DE MÓDULOS CON GRAFOS - VERSIÓN 2.4 (Limpieza de Grafos Integrada)
# ================================================================================================
# CORRECCIONES PRINCIPALES:
# 1. Limpieza de grafos: contracción de nodos, combinación de aristas colineales
# 2. Agrupa segmentos colineales para formar líneas continuas
# 3. Verifica CONECTIVIDAD FÍSICA: segmentos deben compartir nodos
# 4. Verifica que las horizontales vayan de lado a lado (contorno izquierdo → contorno derecho)
# 5. Filtra horizontales internas que no definen límites de módulos
# 6. Aplica la misma lógica a diagonales en módulos X
# ================================================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import math
import pandas as pd
import os
from typing import List, Tuple, Dict, Set

print("🎯 ANÁLISIS DE MÓDULOS - VERSIÓN 2.4 (Limpieza de Grafos)")
print("="*60)

# ================================================================================================
# FUNCIONES AUXILIARES BÁSICAS
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
# FUNCIONES DE LIMPIEZA DE GRAFOS
# ================================================================================================

def crear_grafo_desde_lineas_v2(lineas: List[Tuple]) -> nx.Graph:
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


def contraccion_dinamica_nodos(G: nx.Graph, tolerancia: float = 0.01) -> nx.Graph:
    """
    Contrae nodos que están muy cerca entre sí.

    Esto resuelve errores de precisión del DXF donde puntos que deberían
    ser el mismo están ligeramente desplazados.
    """
    G_limpio = G.copy()
    nodos = list(G_limpio.nodes())

    coords = np.array(nodos)
    if len(coords) > 0:
        tamaño = max(coords.max(axis=0) - coords.min(axis=0))
        tolerancia_abs = tolerancia * tamaño
    else:
        tolerancia_abs = tolerancia

    procesados = set()

    for i, nodo1 in enumerate(nodos):
        if nodo1 in procesados or nodo1 not in G_limpio:
            continue

        grupo = [nodo1]

        for j, nodo2 in enumerate(nodos[i+1:], i+1):
            if nodo2 in procesados or nodo2 not in G_limpio:
                continue

            if distancia_euclidiana(nodo1, nodo2) < tolerancia_abs:
                grupo.append(nodo2)
                procesados.add(nodo2)

        if len(grupo) > 1:
            centroide = tuple(np.mean([list(n) for n in grupo], axis=0))

            for nodo in grupo:
                vecinos = list(G_limpio.neighbors(nodo))
                for vecino in vecinos:
                    if vecino not in grupo:
                        G_limpio.add_edge(centroide, vecino)
                G_limpio.remove_node(nodo)

            G_limpio.add_node(centroide, pos=centroide)

    return G_limpio


def combinacion_aristas(G: nx.Graph, tolerancia_angulo: float = 2.0) -> nx.Graph:
    """
    Combina aristas adyacentes que forman una línea recta.

    CRÍTICO: Esto une segmentos divididos de diagonales y horizontales,
    permitiendo detectar correctamente módulos X.
    """
    G_limpio = G.copy()
    cambios = True

    while cambios:
        cambios = False
        nodos_grado_2 = [n for n in G_limpio.nodes() if G_limpio.degree(n) == 2]

        for nodo in nodos_grado_2:
            vecinos = list(G_limpio.neighbors(nodo))
            if len(vecinos) == 2:
                v1, v2 = vecinos

                if son_colineales(v1, nodo, v2, tolerancia_angulo):
                    G_limpio.add_edge(v1, v2)
                    G_limpio.remove_node(nodo)
                    cambios = True
                    break

    return G_limpio


def eliminacion_aristas_redundantes(G: nx.Graph, tolerancia_longitud: float = 0.005) -> nx.Graph:
    """
    Elimina aristas cortas que están cubiertas por aristas más largas.
    """
    G_limpio = G.copy()

    nodos = np.array(list(G_limpio.nodes()))
    if len(nodos) > 0:
        tamaño = max(nodos.max(axis=0) - nodos.min(axis=0))
        longitud_min = tolerancia_longitud * tamaño
    else:
        longitud_min = tolerancia_longitud

    aristas_con_longitud = []
    for e in G_limpio.edges():
        longitud = distancia_euclidiana(e[0], e[1])
        aristas_con_longitud.append((e, longitud))

    aristas_con_longitud.sort(key=lambda x: x[1])

    for arista, longitud in aristas_con_longitud:
        if longitud < longitud_min and G_limpio.has_edge(*arista):
            G_temp = G_limpio.copy()
            G_temp.remove_edge(*arista)

            if nx.is_connected(G_temp):
                G_limpio.remove_edge(*arista)

    G_limpio.remove_nodes_from(list(nx.isolates(G_limpio)))

    return G_limpio


def limpiar_grafo_completo(G: nx.Graph, verbose: bool = False) -> nx.Graph:
    """
    Aplica todas las etapas de limpieza al grafo.

    Pipeline:
    1. Contracción de nodos cercanos (errores de precisión)
    2. Combinación de aristas colineales (une segmentos divididos)
    3. Eliminación de aristas redundantes (simplifica)

    Returns:
        Grafo limpio y simplificado
    """
    if verbose:
        print(f"\n🧹 LIMPIEZA DE GRAFO")
        print(f"   Nodos iniciales: {G.number_of_nodes()}, Aristas iniciales: {G.number_of_edges()}")

    # Paso 1: Contraer nodos cercanos
    G = contraccion_dinamica_nodos(G, tolerancia=0.01)
    if verbose:
        print(f"   Después de contracción: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

    # Paso 2: Combinar aristas colineales (CRÍTICO para módulos X)
    G = combinacion_aristas(G, tolerancia_angulo=2.0)
    if verbose:
        print(f"   Después de combinación: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

    # Paso 3: Eliminar redundancias
    G = eliminacion_aristas_redundantes(G, tolerancia_longitud=0.005)
    if verbose:
        print(f"   Después de limpieza: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

    return G


# ================================================================================================
# FUNCIONES DE AGRUPACIÓN DE LÍNEAS COLINEALES (NUEVO)
# ================================================================================================

def segmentos_son_colineales(seg1: Tuple[Tuple, Tuple], seg2: Tuple[Tuple, Tuple],
                            tolerancia_angulo: float = 2.0,
                            tolerancia_y: float = 0.01,
                            tolerancia_x: float = 0.01) -> bool:
    """
    Verifica si dos segmentos son colineales (están en la misma línea recta).

    CORRECCIÓN CRÍTICA:
    - Para horizontales: Verifica que ambos estén en la misma altura Y
    - Para verticales: Verifica que ambos estén en la misma coordenada X
    - Para diagonales: Usa verificación de ángulos

    Args:
        seg1: Tupla (punto1, punto2) del primer segmento
        seg2: Tupla (punto1, punto2) del segundo segmento
        tolerancia_angulo: Tolerancia en grados para considerar colineales
        tolerancia_y: Tolerancia en Y para horizontales
        tolerancia_x: Tolerancia en X para verticales

    Returns:
        True si los segmentos son colineales
    """
    p1_1, p1_2 = seg1
    p2_1, p2_2 = seg2

    # Extraer coordenadas
    x1_1, y1_1 = p1_1[0], p1_1[1]
    x1_2, y1_2 = p1_2[0], p1_2[1]
    x2_1, y2_1 = p2_1[0], p2_1[1]
    x2_2, y2_2 = p2_2[0], p2_2[1]

    # Caso 1: HORIZONTALES (verificación directa por altura Y)
    seg1_es_horizontal = abs(y1_1 - y1_2) < tolerancia_y
    seg2_es_horizontal = abs(y2_1 - y2_2) < tolerancia_y

    if seg1_es_horizontal and seg2_es_horizontal:
        # Ambos son horizontales, verificar que estén en la misma altura Y
        y1_avg = (y1_1 + y1_2) / 2
        y2_avg = (y2_1 + y2_2) / 2
        return abs(y1_avg - y2_avg) < tolerancia_y

    # Caso 2: VERTICALES (verificación directa por coordenada X)
    seg1_es_vertical = abs(x1_1 - x1_2) < tolerancia_x
    seg2_es_vertical = abs(x2_1 - x2_2) < tolerancia_x

    if seg1_es_vertical and seg2_es_vertical:
        # Ambos son verticales, verificar que estén en la misma coordenada X
        x1_avg = (x1_1 + x1_2) / 2
        x2_avg = (x2_1 + x2_2) / 2
        return abs(x1_avg - x2_avg) < tolerancia_x

    # Caso 3: DIAGONALES (verificación por ángulos - método original)
    # Verificar que los 4 puntos sean colineales
    if son_colineales(p1_1, p1_2, p2_1, tolerancia_angulo) and \
       son_colineales(p1_1, p1_2, p2_2, tolerancia_angulo):
        return True

    return False


def agrupar_segmentos_colineales(G: nx.Graph, section_bounds: Tuple,
                                tipo: str = 'horizontal',
                                tolerance_direccion: float = 0.01,
                                tolerance_colineal: float = 2.0,
                                verbose: bool = False) -> List[Dict]:
    """
    Agrupa segmentos colineales del grafo para formar líneas continuas.

    CORRECCIÓN: Usa múltiples pasadas para asegurar que todos los segmentos
    colineales se agrupen, incluso si están conectados transitivamente.

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        tipo: 'horizontal', 'vertical' o 'diagonal'
        tolerance_direccion: Tolerancia para clasificar la dirección
        tolerance_colineal: Tolerancia en grados para considerar colineales
        verbose: Imprimir información de debug

    Returns:
        Lista de grupos de segmentos colineales con información de extensión
    """
    y_start, y_end = section_bounds

    # Filtrar segmentos según el tipo
    segmentos = []
    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 2 and len(n2) >= 2:
            y1, y2 = n1[1], n2[1]
            x1, x2 = n1[0], n2[0]
            y_avg = (y1 + y2) / 2

            # Verificar que está en la sección
            if not (y_start <= y_avg <= y_end):
                continue

            # Clasificar según tipo
            if tipo == 'horizontal':
                if abs(y1 - y2) < tolerance_direccion:
                    segmentos.append((n1, n2))
            elif tipo == 'vertical':
                if abs(x1 - x2) < tolerance_direccion:
                    segmentos.append((n1, n2))
            elif tipo == 'diagonal':
                if abs(y1 - y2) > tolerance_direccion and abs(x1 - x2) > tolerance_direccion:
                    segmentos.append((n1, n2))

    if not segmentos:
        return []

    # Agrupar segmentos colineales usando Union-Find simplificado
    # Crear grupos iniciales (cada segmento en su propio grupo)
    grupos_indices = list(range(len(segmentos)))

    def find_grupo(i):
        """Encuentra el grupo raíz de un segmento."""
        while grupos_indices[i] != i:
            grupos_indices[i] = grupos_indices[grupos_indices[i]]  # Compresión de ruta
            i = grupos_indices[i]
        return i

    def union_grupos(i, j):
        """Une dos grupos."""
        raiz_i = find_grupo(i)
        raiz_j = find_grupo(j)
        if raiz_i != raiz_j:
            grupos_indices[raiz_j] = raiz_i

    # Encontrar todos los pares de segmentos colineales
    pares_colineales = 0
    for i in range(len(segmentos)):
        for j in range(i + 1, len(segmentos)):
            if segmentos_son_colineales(segmentos[i], segmentos[j],
                                       tolerance_colineal,
                                       tolerance_direccion,  # tolerance_y
                                       tolerance_direccion): # tolerance_x
                union_grupos(i, j)
                pares_colineales += 1

    if verbose and pares_colineales > 0:
        print(f"       [DEBUG] Pares colineales encontrados: {pares_colineales}")

    # Organizar segmentos en grupos
    grupos_dict = {}
    for i in range(len(segmentos)):
        raiz = find_grupo(i)
        if raiz not in grupos_dict:
            grupos_dict[raiz] = []
        grupos_dict[raiz].append(segmentos[i])

    # Calcular información de cada grupo
    grupos = []
    for grupo_segs in grupos_dict.values():
        todos_los_puntos = []
        for seg in grupo_segs:
            todos_los_puntos.extend([seg[0], seg[1]])

        # Calcular extensión en X e Y
        x_coords = [p[0] for p in todos_los_puntos]
        y_coords = [p[1] for p in todos_los_puntos]

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        y_avg = sum(y_coords) / len(y_coords)

        grupos.append({
            'segmentos': grupo_segs,
            'num_segmentos': len(grupo_segs),
            'x_min': x_min,
            'x_max': x_max,
            'extension_x': x_max - x_min,
            'y_min': y_min,
            'y_max': y_max,
            'y_avg': y_avg,
            'puntos': todos_los_puntos
        })

    return grupos


def verificar_conectividad_grupo(grupo_segs: List[Tuple[Tuple, Tuple]]) -> bool:
    """
    Verifica si los segmentos de un grupo están conectados físicamente (comparten nodos).

    CORRECCIÓN CRÍTICA V2.3:
    - Solo acepta grupos donde los segmentos forman una cadena continua
    - Rechaza horizontales colineales pero NO conectadas físicamente
    - Ejemplo válido: seg1=(A→B) y seg2=(B→C) comparten nodo B
    - Ejemplo inválido: seg1=(A→B) y seg2=(C→D) no comparten nodos

    Args:
        grupo_segs: Lista de segmentos (tuplas de puntos)

    Returns:
        True si todos los segmentos están conectados formando una cadena
    """
    if len(grupo_segs) <= 1:
        return True  # Un solo segmento siempre está "conectado"

    # Construir grafo de conectividad entre segmentos
    # Usar BFS/DFS para verificar que todos son alcanzables desde el primero
    segmentos_conectados = set([0])  # Empezar con el primer segmento
    cambios = True

    while cambios:
        cambios = False
        for i in segmentos_conectados.copy():
            seg_i = grupo_segs[i]
            nodos_i = set([seg_i[0], seg_i[1]])

            for j in range(len(grupo_segs)):
                if j not in segmentos_conectados:
                    seg_j = grupo_segs[j]
                    nodos_j = set([seg_j[0], seg_j[1]])

                    # Verificar si comparten algún nodo
                    if nodos_i & nodos_j:  # Intersección no vacía
                        segmentos_conectados.add(j)
                        cambios = True

    # Verificar que todos los segmentos estén conectados
    return len(segmentos_conectados) == len(grupo_segs)


def calcular_contornos_en_altura(G: nx.Graph, y_altura: float,
                                 symmetry_axis: float,
                                 tolerance_y: float = 0.1) -> Tuple[float, float]:
    """
    Calcula los límites izquierdo y derecho del contorno en una altura Y específica.

    CORRECCIÓN CLAVE:
    - En torres decrecientes, el contorno cambia con la altura Y
    - Busca nodos y aristas cerca de la altura especificada
    - Retorna los extremos X más alejados del eje de simetría

    Args:
        G: Grafo de NetworkX
        y_altura: Altura Y donde calcular los contornos
        symmetry_axis: Coordenada X del eje de simetría
        tolerance_y: Tolerancia en Y para considerar nodos/aristas

    Returns:
        (limite_izq, limite_der): Coordenadas X de los contornos
    """
    x_izq_min = float('inf')
    x_der_max = float('-inf')

    # Buscar nodos cercanos a esta altura
    for node in G.nodes():
        if len(node) >= 2:
            x, y = node[0], node[1]

            if abs(y - y_altura) < tolerance_y:
                if x < symmetry_axis:
                    x_izq_min = min(x_izq_min, x)
                else:
                    x_der_max = max(x_der_max, x)

    # Buscar aristas que intersectan esta altura
    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 2 and len(n2) >= 2:
            y1, y2 = n1[1], n2[1]
            x1, x2 = n1[0], n2[0]

            # Si la arista cruza la altura y_altura
            if (y1 <= y_altura <= y2) or (y2 <= y_altura <= y1):
                # Interpolar X en la altura y_altura
                if abs(y2 - y1) > 1e-6:
                    t = (y_altura - y1) / (y2 - y1)
                    x_interp = x1 + t * (x2 - x1)

                    if x_interp < symmetry_axis:
                        x_izq_min = min(x_izq_min, x_interp)
                    else:
                        x_der_max = max(x_der_max, x_interp)

    # Si no se encontraron puntos, usar valores por defecto
    if x_izq_min == float('inf'):
        x_izq_min = 0.0
    if x_der_max == float('-inf'):
        x_der_max = symmetry_axis * 2

    return x_izq_min, x_der_max


def horizontal_va_lado_a_lado(grupo: Dict, G: nx.Graph, symmetry_axis: float,
                              tolerance: float = 0.5) -> bool:
    """
    Verifica si un grupo de horizontales colineales va de lado a lado de la torre.

    CORRECCIÓN CLAVE:
    - Calcula los contornos dinámicamente en la altura Y de la horizontal
    - En torres decrecientes, el contorno cambia con la altura

    Args:
        grupo: Diccionario con información del grupo (de agrupar_segmentos_colineales)
        G: Grafo de NetworkX
        symmetry_axis: Coordenada X del eje de simetría
        tolerance: Tolerancia en metros para considerar que llega al contorno

    Returns:
        True si la horizontal va de lado a lado
    """
    x_min = grupo['x_min']
    x_max = grupo['x_max']
    y_avg = grupo['y_avg']

    # Calcular contornos en esta altura específica
    limite_izq, limite_der = calcular_contornos_en_altura(G, y_avg, symmetry_axis)

    # Verificar si llega cerca de ambos contornos
    llega_izquierda = abs(x_min - limite_izq) < tolerance
    llega_derecha = abs(x_max - limite_der) < tolerance

    return llega_izquierda and llega_derecha


# ================================================================================================
# HORIZONTALES FILTRADAS (SOLO LADO A LADO)
# ================================================================================================

def obtener_horizontales_lado_a_lado(G: nx.Graph, section_bounds: Tuple,
                                    symmetry_axis: float,
                                    tolerance_horizontal: float = 0.01,
                                    tolerance_colineal: float = 2.0,
                                    tolerance_contorno: float = 0.5,
                                    verbose: bool = False) -> List[float]:
    """
    Obtiene las alturas Y de horizontales que van de lado a lado de la torre.

    CORRECCIÓN CLAVE:
    - Agrupa segmentos horizontales colineales
    - Calcula contornos dinámicamente para cada altura Y
    - Solo cuenta como límite las horizontales continuas que van del contorno izquierdo al derecho
    - Descarta horizontales internas que no cruzan toda la torre

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        symmetry_axis: Coordenada X del eje de simetría
        tolerance_horizontal: Tolerancia para considerar una línea horizontal
        tolerance_colineal: Tolerancia para agrupar segmentos colineales
        tolerance_contorno: Tolerancia para verificar que llega al contorno
        verbose: Imprimir información de depuración

    Returns:
        Lista de alturas Y donde hay horizontales que van de lado a lado
    """
    # Agrupar horizontales colineales
    grupos_horizontales = agrupar_segmentos_colineales(
        G, section_bounds,
        tipo='horizontal',
        tolerance_direccion=tolerance_horizontal,
        tolerance_colineal=tolerance_colineal,
        verbose=verbose
    )

    if verbose:
        print(f"    📊 Grupos horizontales encontrados: {len(grupos_horizontales)}")

    # Filtrar solo las que van de lado a lado Y están conectadas físicamente
    alturas_validas = []
    grupos_rechazados_conectividad = 0

    for grupo in grupos_horizontales:
        # PASO 1: Verificar conectividad física (V2.3)
        esta_conectado = verificar_conectividad_grupo(grupo['segmentos'])

        if not esta_conectado:
            grupos_rechazados_conectividad += 1
            if verbose:
                print(f"       Y={grupo['y_avg']:.3f}: {grupo['num_segmentos']} segs, "
                      f"X=[{grupo['x_min']:.2f} - {grupo['x_max']:.2f}], "
                      f"conectado=❌ (rechazado)")
            continue

        # PASO 2: Calcular contornos dinámicamente en la altura de esta horizontal
        limite_izq, limite_der = calcular_contornos_en_altura(G, grupo['y_avg'], symmetry_axis)

        # PASO 3: Verificar que vaya de lado a lado
        va_lado_a_lado = horizontal_va_lado_a_lado(
            grupo, G, symmetry_axis, tolerance_contorno
        )

        if verbose:
            print(f"       Y={grupo['y_avg']:.3f}: {grupo['num_segmentos']} segs, "
                  f"X=[{grupo['x_min']:.2f} - {grupo['x_max']:.2f}], "
                  f"ext={grupo['extension_x']:.2f}, "
                  f"contornos=[{limite_izq:.2f} - {limite_der:.2f}], "
                  f"conectado=✅, "
                  f"lado_a_lado={'✅' if va_lado_a_lado else '❌'}")

        if va_lado_a_lado:
            alturas_validas.append(grupo['y_avg'])

    if verbose and grupos_rechazados_conectividad > 0:
        print(f"    ⚠️  Grupos rechazados por falta de conectividad: {grupos_rechazados_conectividad}")

    if verbose:
        print(f"    ✅ Horizontales válidas (lado a lado): {len(alturas_validas)}")

    return sorted(alturas_validas)


# ================================================================================================
# DETECCIÓN DE MÓDULOS X (SIN CAMBIOS)
# ================================================================================================

def detectar_modulos_x_mejorado(G: nx.Graph, section_bounds: Tuple,
                                symmetry_axis: float, tolerance: float = 0.05,
                                verbose: bool = False) -> Dict:
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

        if verbose:
            print(f"       [DEBUG X] Candidato Y={candidato['y']:.3f}: grado={candidato['grado']}, "
                  f"vecinos={len(vecinos)}, pares_colineales={len(pares_colineales)}")

        # Criterio relajado para módulos X en secciones pequeñas
        # Si tiene grado >= 4 y al menos 1 par colineal con diagonales, puede ser X
        if len(pares_colineales) >= 1:
            tiene_diagonales = False
            for v1, v2 in pares_colineales:
                if not es_horizontal((v1, v2), tolerance):
                    tiene_diagonales = True
                    break

            if tiene_diagonales:
                candidato['pares_colineales'] = pares_colineales
                centros_modulo_x.append(candidato)
                if verbose:
                    print(f"       [DEBUG X] ✅ Aceptado como centro de módulo X")
            elif verbose:
                print(f"       [DEBUG X] ❌ Rechazado: no tiene diagonales")
        elif verbose:
            print(f"       [DEBUG X] ❌ Rechazado: insuficientes pares colineales")

    return {
        'detected': len(centros_modulo_x) > 0,
        'candidates': len(candidatos),
        'x_centers': centros_modulo_x,
        'num_x_modules': len(centros_modulo_x)
    }


# ================================================================================================
# DIAGONALES PARA MÓDULOS X (CON AGRUPACIÓN COLINEAL)
# ================================================================================================

def obtener_alturas_de_diagonales_mejorado(G: nx.Graph, section_bounds: Tuple,
                                          x_centers: List[Dict],
                                          symmetry_axis: float,
                                          tolerance: float = 0.05,
                                          tolerance_colineal: float = 2.0,
                                          verbose: bool = False) -> List[float]:
    """
    Obtiene las alturas Y únicas donde cambian las diagonales en módulos X.

    CORRECCIÓN:
    - Agrupa diagonales colineales
    - Solo cuenta extremos exteriores de grupos de diagonales
    - Excluye coordenadas Y de centros de módulos X
    """
    y_start, y_end = section_bounds

    # Obtener coordenadas Y de los centros de módulos X (a excluir)
    y_centros = set()
    for centro in x_centers:
        y_centros.add(centro['y'])

    # Agrupar diagonales colineales
    grupos_diagonales = agrupar_segmentos_colineales(
        G, section_bounds,
        tipo='diagonal',
        tolerance_direccion=tolerance,
        tolerance_colineal=tolerance_colineal
    )

    if verbose:
        print(f"    📊 Grupos de diagonales: {len(grupos_diagonales)}")

    # Extraer alturas Y de los extremos de los grupos
    alturas_y = set()

    for grupo in grupos_diagonales:
        y_min = grupo['y_min']
        y_max = grupo['y_max']

        # Agregar y_min solo si NO es un centro de módulo X
        es_centro_min = any(abs(y_min - yc) < tolerance for yc in y_centros)
        if not es_centro_min:
            alturas_y.add(y_min)

        # Agregar y_max solo si NO es un centro de módulo X
        es_centro_max = any(abs(y_max - yc) < tolerance for yc in y_centros)
        if not es_centro_max:
            alturas_y.add(y_max)

    if verbose:
        print(f"    ✅ Alturas de diagonales (sin centros): {len(alturas_y)}")

    return sorted(list(alturas_y))


# ================================================================================================
# ANÁLISIS DE SECCIÓN CON GRAFO (CORREGIDO)
# ================================================================================================

def analizar_seccion_con_grafo(G: nx.Graph, section: Dict, symmetry_axis: float,
                               tolerance: float = 0.05, verbose: bool = True) -> Dict:
    """Analiza una sección usando la estructura del grafo (VERSIÓN CORREGIDA CON COLINEALIDAD)."""
    y_start = section["altura_inicio"]
    y_end = section["altura_fin"]
    section_height = section["altura_tramo"]
    section_type = section["tipo"]

    if verbose:
        print(f"\n🔧 ANÁLISIS CON GRAFO - Sección {section_type}")
        print(f"    📏 Y: [{y_start:.3f} - {y_end:.3f}], h: {section_height:.3f}")

    # PASO 1: Detectar módulos X
    deteccion_x = detectar_modulos_x_mejorado(G, (y_start, y_end), symmetry_axis, tolerance, verbose=verbose)

    if verbose:
        print(f"    🔍 Candidatos de grado alto: {deteccion_x['candidates']}")
        print(f"    🎯 Módulos X detectados: {deteccion_x['num_x_modules'] if deteccion_x['detected'] else 0}")

    if deteccion_x['detected']:
        # HAY MÓDULO X → Usar alturas Y de diagonales
        if verbose:
            print(f"    ✅ Estrategia: DIAGONALES (módulo X detectado)")

        # Obtener alturas únicas de diagonales (agrupadas y sin centros)
        alturas_diagonales = obtener_alturas_de_diagonales_mejorado(
            G, (y_start, y_end), deteccion_x['x_centers'], symmetry_axis, tolerance, verbose=verbose
        )

        # Filtrar diagonales que están en los límites de sección (evitar duplicados)
        tolerancia_limite = 0.001
        alturas_filtradas = []
        for alt in alturas_diagonales:
            if abs(alt - y_start) > tolerancia_limite and abs(alt - y_end) > tolerancia_limite:
                alturas_filtradas.append(alt)

        # Agregar límites de sección
        alturas_modulos = sorted([y_start] + alturas_filtradas + [y_end])

        return {
            'metodo': 'grafo-diagonal-colineal',
            'alturas': alturas_modulos,
            'num_modulos': len(alturas_modulos) - 1,
            'tiene_modulo_x': True,
            'x_centers': deteccion_x['x_centers']
        }

    else:
        # NO HAY MÓDULO X → Usar estrategia de horizontales (SOLO LADO A LADO)
        if verbose:
            print(f"    ➖ Estrategia: HORIZONTALES (solo lado a lado)")

        alturas_horizontales = obtener_horizontales_lado_a_lado(
            G, (y_start, y_end), symmetry_axis,
            tolerance_horizontal=0.01,
            tolerance_colineal=2.0,
            tolerance_contorno=0.5,
            verbose=verbose
        )

        # Filtrar horizontales que están en los límites de sección (evitar duplicados)
        # Tolerancia: 0.001m (1mm) para considerar que es el mismo límite
        tolerancia_limite = 0.001
        alturas_filtradas = []
        for alt in alturas_horizontales:
            if abs(alt - y_start) > tolerancia_limite and abs(alt - y_end) > tolerancia_limite:
                alturas_filtradas.append(alt)

        # Agregar límites de sección
        alturas_modulos = sorted([y_start] + alturas_filtradas + [y_end])

        return {
            'metodo': 'grafo-horizontal-colineal',
            'alturas': alturas_modulos,
            'num_modulos': len(alturas_modulos) - 1,
            'horizontales_lado_a_lado': alturas_horizontales,
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

print("\n🔧 CREANDO Y LIMPIANDO GRAFO...")

G = crear_grafo_desde_lineas(oriented_lines)

print(f"   Grafo inicial:")
print(f"   • Nodos: {G.number_of_nodes()}")
print(f"   • Aristas: {G.number_of_edges()}")

# Aplicar limpieza del grafo (CRÍTICO para detectar módulos X)
G = limpiar_grafo_completo(G, verbose=True)

print(f"✅ Grafo limpio:")
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
# VISUALIZACIÓN MEJORADA
# ================================================================================================

print("\n📊 GENERANDO VISUALIZACIÓN...")

fig, ax = plt.subplots(1, 1, figsize=(14, 16))

ax.set_title('Torre con Secciones y Módulos Detectados (Colinealidad Corregida)',
             fontsize=18, fontweight='bold', pad=20)

# Dibujar todas las aristas en gris claro
for edge in G.edges():
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        ax.plot([n1[0], n2[0]], [n1[1], n2[1]], 'gray', linewidth=0.5, alpha=0.3)

# Colores para secciones
colores_seccion = ['red', 'blue', 'green', 'orange', 'purple']

# Marcar límites de secciones
for i, section in enumerate(sections_con_modulos):
    y_start = section['altura_inicio']
    y_end = section['altura_fin']
    color = colores_seccion[i % len(colores_seccion)]

    ax.axhline(y_start, color=color, linestyle='--', linewidth=3, alpha=0.8,
               label=f"Sección {i+1}: {section['tipo']} ({section['num_modulos']} mód)")

    if i == len(sections_con_modulos) - 1:
        ax.axhline(y_end, color=color, linestyle='--', linewidth=3, alpha=0.8)

# Marcar alturas de módulos
for i, section in enumerate(sections_con_modulos):
    alturas = section['limites_modulos']
    color = colores_seccion[i % len(colores_seccion)]

    for j, altura in enumerate(alturas[1:-1], 1):
        ax.axhline(altura, color=color, linestyle=':', linewidth=1.5, alpha=0.6)
        ax.text(max(all_x) + 0.3, altura, f'Y={altura:.1f}',
                fontsize=9, color=color, va='center')

# Marcar eje de simetría
ax.axvline(symmetry_axis, color='green', linestyle=':', linewidth=2.5, alpha=0.7,
           label=f'Eje simetría X={symmetry_axis:.2f}', zorder=5)

# Marcar centros de módulos X
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

    print(f"\n   {tiene_x} Sección {i+1} ({tipo}): {num_mod} módulos [{metodo}]")

    if num_mod <= 20:
        alturas = section['limites_modulos']
        for j in range(num_mod):
            h = section['alturas_modulos'][j]
            y_ini = alturas[j]
            y_fin = alturas[j+1]
            print(f"       M{j+1}: h={h:.3f}m, Y=[{y_ini:.3f} - {y_fin:.3f}]")

print("\n" + "="*60)
print("✅ ANÁLISIS COMPLETADO - VERSIÓN 2.4 (Limpieza de Grafos)")
print("="*60)
