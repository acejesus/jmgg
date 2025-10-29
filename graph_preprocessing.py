"""
================================================================================================
MÓDULO DE PREPROCESAMIENTO CON GRAFOS PARA ANÁLISIS DE TORRES DXF
================================================================================================
Este módulo resuelve problemas clave del análisis directo de líneas DXF:

✅ Contrae nodos muy cercanos (errores de precisión DXF)
✅ Une líneas colineales (diagonales divididas en múltiples segmentos)
✅ Elimina líneas redundantes
✅ Limpia el grafo antes del análisis de módulos

Autor: Integración con NetworkX
Versión: 1.0
================================================================================================
"""

import networkx as nx
import numpy as np
import math
from typing import List, Tuple, Dict, Set


def distancia_euclidiana(p1: Tuple, p2: Tuple) -> float:
    """Calcula la distancia euclidiana entre dos puntos."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


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


def contraccion_dinamica_nodos(G: nx.Graph, tolerancia: float = 0.01) -> nx.Graph:
    """
    Contrae nodos que están muy cerca entre sí.

    Esto resuelve el problema de errores de precisión en archivos DXF donde
    el mismo punto puede aparecer con coordenadas ligeramente diferentes.

    Args:
        G: Grafo de entrada
        tolerancia: Tolerancia relativa al tamaño del modelo (default: 0.01 = 1%)

    Returns:
        nx.Graph: Grafo con nodos contraídos
    """
    G_limpio = G.copy()
    nodos = list(G_limpio.nodes())

    if len(nodos) == 0:
        return G_limpio

    # Calcular tolerancia absoluta basada en el tamaño del modelo
    coords = np.array(nodos)
    tamaño = max(coords.max(axis=0) - coords.min(axis=0))
    tolerancia_abs = tolerancia * tamaño

    print(f"   🔍 Contrayendo nodos cercanos (tolerancia: {tolerancia_abs:.4f})...")

    procesados = set()
    num_contracciones = 0

    for i, nodo1 in enumerate(nodos):
        if nodo1 in procesados or nodo1 not in G_limpio:
            continue

        grupo = [nodo1]

        # Buscar nodos cercanos
        for j, nodo2 in enumerate(nodos[i+1:], i+1):
            if nodo2 in procesados or nodo2 not in G_limpio:
                continue

            if distancia_euclidiana(nodo1, nodo2) < tolerancia_abs:
                grupo.append(nodo2)
                procesados.add(nodo2)

        # Si hay nodos para contraer
        if len(grupo) > 1:
            # Calcular centroide del grupo
            centroide = tuple(np.mean([list(n) for n in grupo], axis=0))

            # Reconectar todas las aristas al centroide
            for nodo in grupo:
                vecinos = list(G_limpio.neighbors(nodo))
                for vecino in vecinos:
                    if vecino not in grupo:
                        G_limpio.add_edge(centroide, vecino)
                G_limpio.remove_node(nodo)

            G_limpio.add_node(centroide, pos=centroide)
            num_contracciones += len(grupo) - 1

    print(f"   ✅ {num_contracciones} nodos contraídos")
    return G_limpio


def angulo_entre_vectores(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calcula el ángulo en grados entre dos vectores.

    Args:
        v1, v2: Vectores como arrays de numpy

    Returns:
        float: Ángulo en grados (siempre positivo)
    """
    cos_angulo = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
    cos_angulo = np.clip(cos_angulo, -1.0, 1.0)
    return math.degrees(math.acos(abs(cos_angulo)))


def son_colineales(p1: Tuple, p2: Tuple, p3: Tuple, tolerancia_angulo: float = 2.0) -> bool:
    """
    Verifica si tres puntos son colineales (forman una línea recta).

    Args:
        p1, p2, p3: Tres puntos en el espacio
        tolerancia_angulo: Ángulo máximo en grados para considerar colinealidad

    Returns:
        bool: True si los puntos son colineales
    """
    # Vectores entre puntos consecutivos
    v1 = np.array([p2[i] - p1[i] for i in range(len(p1))])
    v2 = np.array([p3[i] - p2[i] for i in range(len(p2))])

    # Si algún vector es casi cero, no son colineales significativos
    if np.linalg.norm(v1) < 1e-10 or np.linalg.norm(v2) < 1e-10:
        return False

    angulo = angulo_entre_vectores(v1, v2)
    return angulo < tolerancia_angulo


def combinacion_aristas(G: nx.Graph, tolerancia_angulo: float = 2.0) -> nx.Graph:
    """
    Combina aristas adyacentes que forman una línea recta.

    Esta es la función CLAVE para unir diagonales divididas en múltiples segmentos.
    Por ejemplo, si una diagonal de un módulo X está dividida en 2-3 líneas,
    esta función las unirá en una sola arista.

    Args:
        G: Grafo de entrada
        tolerancia_angulo: Ángulo máximo en grados para considerar colinealidad

    Returns:
        nx.Graph: Grafo con aristas colineales combinadas
    """
    G_limpio = G.copy()
    cambios = True
    iteracion = 0
    num_combinaciones = 0

    print(f"   🔗 Combinando líneas colineales (tolerancia: {tolerancia_angulo}°)...")

    while cambios:
        cambios = False
        iteracion += 1

        # Encontrar nodos de grado 2 (candidatos a estar en medio de una línea)
        nodos_grado_2 = [n for n in G_limpio.nodes() if G_limpio.degree(n) == 2]

        for nodo in nodos_grado_2:
            vecinos = list(G_limpio.neighbors(nodo))

            if len(vecinos) == 2:
                v1, v2 = vecinos

                # Verificar si los tres puntos son colineales
                if son_colineales(v1, nodo, v2, tolerancia_angulo):
                    # Unir las dos aristas eliminando el nodo intermedio
                    G_limpio.add_edge(v1, v2)
                    G_limpio.remove_node(nodo)
                    cambios = True
                    num_combinaciones += 1
                    break  # Reiniciar búsqueda con el grafo modificado

        # Límite de iteraciones por seguridad
        if iteracion > 10000:
            print(f"   ⚠️ Límite de iteraciones alcanzado")
            break

    print(f"   ✅ {num_combinaciones} líneas combinadas en {iteracion} iteraciones")
    return G_limpio


def eliminacion_aristas_redundantes(G: nx.Graph, tolerancia_longitud: float = 0.005) -> nx.Graph:
    """
    Elimina aristas cortas que están cubiertas por aristas más largas.

    Esto elimina líneas redundantes que pueden confundir el análisis de módulos.

    Args:
        G: Grafo de entrada
        tolerancia_longitud: Longitud mínima relativa (default: 0.005 = 0.5%)

    Returns:
        nx.Graph: Grafo sin aristas redundantes
    """
    G_limpio = G.copy()

    # Calcular longitud mínima basada en el tamaño del modelo
    nodos = np.array(list(G_limpio.nodes()))
    if len(nodos) > 0:
        tamaño = max(nodos.max(axis=0) - nodos.min(axis=0))
        longitud_min = tolerancia_longitud * tamaño
    else:
        longitud_min = tolerancia_longitud

    print(f"   ✂️ Eliminando aristas redundantes (longitud mín: {longitud_min:.4f})...")

    # Calcular longitudes de todas las aristas
    aristas_con_longitud = []
    for e in G_limpio.edges():
        longitud = distancia_euclidiana(e[0], e[1])
        aristas_con_longitud.append((e, longitud))

    # Ordenar por longitud (más cortas primero)
    aristas_con_longitud.sort(key=lambda x: x[1])

    num_eliminadas = 0

    # Intentar eliminar aristas cortas manteniendo conectividad
    for arista, longitud in aristas_con_longitud:
        if longitud < longitud_min and G_limpio.has_edge(*arista):
            # Intentar eliminar la arista
            G_temp = G_limpio.copy()
            G_temp.remove_edge(*arista)

            # Solo eliminar si mantiene la conectividad del grafo
            if nx.is_connected(G_temp):
                G_limpio.remove_edge(*arista)
                num_eliminadas += 1

    # Eliminar nodos aislados
    nodos_aislados = list(nx.isolates(G_limpio))
    G_limpio.remove_nodes_from(nodos_aislados)

    if nodos_aislados:
        print(f"   🗑️ {len(nodos_aislados)} nodos aislados eliminados")

    print(f"   ✅ {num_eliminadas} aristas redundantes eliminadas")
    return G_limpio


def limpiar_grafo_completo(G: nx.Graph,
                          tolerancia_nodos: float = 0.01,
                          tolerancia_angulo: float = 2.0,
                          tolerancia_longitud: float = 0.005) -> nx.Graph:
    """
    Pipeline completo de limpieza de grafo.

    Args:
        G: Grafo de entrada
        tolerancia_nodos: Tolerancia para contracción de nodos
        tolerancia_angulo: Tolerancia angular para líneas colineales
        tolerancia_longitud: Tolerancia para eliminación de aristas cortas

    Returns:
        nx.Graph: Grafo completamente limpio
    """
    print("\n🧹 LIMPIEZA COMPLETA DEL GRAFO")
    print("="*60)

    nodos_inicial = G.number_of_nodes()
    aristas_inicial = G.number_of_edges()

    print(f"📊 Estado inicial: {nodos_inicial} nodos, {aristas_inicial} aristas")

    # Paso 1: Contraer nodos cercanos
    print("\n1️⃣ CONTRACCIÓN DE NODOS")
    G = contraccion_dinamica_nodos(G, tolerancia_nodos)

    # Paso 2: Combinar líneas colineales
    print("\n2️⃣ COMBINACIÓN DE LÍNEAS COLINEALES")
    G = combinacion_aristas(G, tolerancia_angulo)

    # Paso 3: Eliminar aristas redundantes
    print("\n3️⃣ ELIMINACIÓN DE ARISTAS REDUNDANTES")
    G = eliminacion_aristas_redundantes(G, tolerancia_longitud)

    nodos_final = G.number_of_nodes()
    aristas_final = G.number_of_edges()

    print("\n" + "="*60)
    print(f"✅ LIMPIEZA COMPLETADA")
    print(f"📊 Nodos: {nodos_inicial} → {nodos_final} (reducción: {nodos_inicial - nodos_final})")
    print(f"📊 Aristas: {aristas_inicial} → {aristas_final} (reducción: {aristas_inicial - aristas_final})")
    print(f"📉 Reducción total: {((nodos_inicial + aristas_inicial) - (nodos_final + aristas_final)):.0f} elementos")

    return G


def convertir_grafo_a_lineas(G: nx.Graph) -> List[Tuple]:
    """
    Convierte un grafo de NetworkX de vuelta a lista de líneas.

    Args:
        G: Grafo de NetworkX

    Returns:
        List[Tuple]: Lista de líneas en formato (x1, y1, z1, x2, y2, z2)
    """
    lineas = []

    for edge in G.edges():
        p1, p2 = edge

        # Asegurar que tenemos tuplas de 3 elementos (x, y, z)
        if len(p1) == 3 and len(p2) == 3:
            x1, y1, z1 = p1
            x2, y2, z2 = p2
        elif len(p1) == 2 and len(p2) == 2:
            # Si solo hay 2D, agregar z=0
            x1, y1 = p1
            x2, y2 = p2
            z1, z2 = 0, 0
        else:
            print(f"⚠️ Advertencia: Nodo con dimensión inesperada: {p1}, {p2}")
            continue

        lineas.append((x1, y1, z1, x2, y2, z2))

    return lineas


def preprocesar_lineas_dxf(lineas: List[Tuple],
                           tolerancia_nodos: float = 0.01,
                           tolerancia_angulo: float = 2.0,
                           tolerancia_longitud: float = 0.005,
                           verbose: bool = True) -> List[Tuple]:
    """
    Función principal: Preprocesa líneas DXF usando análisis de grafos.

    Esta es la función que debes llamar ANTES del análisis de módulos.

    Args:
        lineas: Lista de líneas en formato (x1, y1, z1, x2, y2, z2)
        tolerancia_nodos: Tolerancia para unir nodos cercanos (default: 1% del tamaño)
        tolerancia_angulo: Tolerancia para unir líneas colineales (default: 2°)
        tolerancia_longitud: Tolerancia para eliminar líneas cortas (default: 0.5%)
        verbose: Mostrar mensajes detallados

    Returns:
        List[Tuple]: Líneas limpias y procesadas

    Example:
        >>> lineas_originales = load_lines_from_dxf()
        >>> lineas_limpias = preprocesar_lineas_dxf(lineas_originales)
        >>> # Ahora usar lineas_limpias para el análisis de módulos
    """
    if not verbose:
        # Silenciar prints temporalmente
        import sys
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    try:
        # Crear grafo
        G = crear_grafo_desde_lineas(lineas)

        # Limpiar grafo
        G_limpio = limpiar_grafo_completo(G,
                                         tolerancia_nodos,
                                         tolerancia_angulo,
                                         tolerancia_longitud)

        # Convertir de vuelta a líneas
        lineas_limpias = convertir_grafo_a_lineas(G_limpio)

        return lineas_limpias

    finally:
        if not verbose:
            sys.stdout = old_stdout


def analizar_mejoras_preprocesamiento(lineas_originales: List[Tuple],
                                     lineas_procesadas: List[Tuple]) -> Dict:
    """
    Analiza las mejoras obtenidas por el preprocesamiento.

    Args:
        lineas_originales: Líneas antes del preprocesamiento
        lineas_procesadas: Líneas después del preprocesamiento

    Returns:
        Dict: Estadísticas de mejoras
    """
    stats = {
        'lineas_originales': len(lineas_originales),
        'lineas_procesadas': len(lineas_procesadas),
        'lineas_eliminadas': len(lineas_originales) - len(lineas_procesadas),
        'porcentaje_reduccion': ((len(lineas_originales) - len(lineas_procesadas)) /
                                len(lineas_originales) * 100) if lineas_originales else 0
    }

    print("\n📊 ANÁLISIS DE MEJORAS")
    print("="*60)
    print(f"📥 Líneas originales:  {stats['lineas_originales']}")
    print(f"📤 Líneas procesadas:  {stats['lineas_procesadas']}")
    print(f"🗑️ Líneas eliminadas:   {stats['lineas_eliminadas']}")
    print(f"📉 Reducción:          {stats['porcentaje_reduccion']:.1f}%")

    if stats['porcentaje_reduccion'] > 5:
        print(f"✅ ¡Mejora significativa! El preprocesamiento eliminó datos redundantes.")
    elif stats['porcentaje_reduccion'] > 0:
        print(f"✓ Mejora moderada. Algunos datos redundantes eliminados.")
    else:
        print(f"ℹ️ Sin reducción. El modelo ya estaba limpio.")

    return stats


# ================================================================================================
# FUNCIONES DE INTEGRACIÓN CON EL CÓDIGO EXISTENTE
# ================================================================================================

def integrar_preprocesamiento_en_analisis(oriented_lines: List[Tuple],
                                         left_contour: List[Tuple],
                                         right_contour: List[Tuple]) -> Tuple[List, List, List]:
    """
    Integra el preprocesamiento de grafos en el flujo de análisis existente.

    Args:
        oriented_lines: Todas las líneas orientadas
        left_contour: Líneas del contorno izquierdo
        right_contour: Líneas del contorno derecho

    Returns:
        Tuple: (oriented_lines_limpias, left_contour_limpio, right_contour_limpio)
    """
    print("\n🔧 INTEGRANDO PREPROCESAMIENTO EN EL ANÁLISIS")
    print("="*60)

    # Preprocesar todas las líneas
    print("\n1️⃣ Preprocesando todas las líneas orientadas...")
    oriented_lines_limpias = preprocesar_lineas_dxf(oriented_lines, verbose=True)

    # Preprocesar contorno izquierdo
    print("\n2️⃣ Preprocesando contorno izquierdo...")
    left_contour_limpio = preprocesar_lineas_dxf(left_contour, verbose=False)

    # Preprocesar contorno derecho
    print("\n3️⃣ Preprocesando contorno derecho...")
    right_contour_limpio = preprocesar_lineas_dxf(right_contour, verbose=False)

    print("\n" + "="*60)
    print("✅ PREPROCESAMIENTO INTEGRADO COMPLETADO")

    # Mostrar estadísticas
    analizar_mejoras_preprocesamiento(oriented_lines, oriented_lines_limpias)

    return oriented_lines_limpias, left_contour_limpio, right_contour_limpio


if __name__ == "__main__":
    print("📦 Módulo de preprocesamiento con grafos cargado correctamente")
    print("\n🎯 Funciones principales:")
    print("   • preprocesar_lineas_dxf() - Función principal de preprocesamiento")
    print("   • integrar_preprocesamiento_en_analisis() - Integración con análisis existente")
    print("   • limpiar_grafo_completo() - Pipeline completo de limpieza")
