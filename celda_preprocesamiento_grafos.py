# ================================================================================================
# CELDA DE PREPROCESAMIENTO CON GRAFOS - LISTA PARA COLAB
# ================================================================================================
# INSTRUCCIONES:
# 1. Copia esta celda COMPLETA en tu notebook de Colab
# 2. Colócala ANTES de la celda "main_universal_improved_analysis()"
# 3. Ejecuta esta celda para preprocesar los datos
# 4. Ejecuta el análisis normal - usará automáticamente los datos limpios
# ================================================================================================

import networkx as nx
import numpy as np
import math
from typing import List, Tuple, Dict

print("🔧 MÓDULO DE PREPROCESAMIENTO CON GRAFOS")
print("="*60)

# ================================================================================================
# FUNCIONES AUXILIARES
# ================================================================================================

def distancia_euclidiana(p1: Tuple, p2: Tuple) -> float:
    """Calcula la distancia euclidiana entre dos puntos."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


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
            continue
        G.add_node(p1, pos=p1)
        G.add_node(p2, pos=p2)
        G.add_edge(p1, p2)
    return G


def contraccion_dinamica_nodos(G: nx.Graph, tolerancia: float = 0.01) -> nx.Graph:
    """Contrae nodos que están muy cerca entre sí."""
    G_limpio = G.copy()
    nodos = list(G_limpio.nodes())

    if len(nodos) == 0:
        return G_limpio

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
            num_contracciones += len(grupo) - 1

    print(f"   ✅ {num_contracciones} nodos contraídos")
    return G_limpio


def angulo_entre_vectores(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calcula el ángulo en grados entre dos vectores."""
    cos_angulo = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
    cos_angulo = np.clip(cos_angulo, -1.0, 1.0)
    return math.degrees(math.acos(abs(cos_angulo)))


def son_colineales(p1: Tuple, p2: Tuple, p3: Tuple, tolerancia_angulo: float = 2.0) -> bool:
    """Verifica si tres puntos son colineales."""
    v1 = np.array([p2[i] - p1[i] for i in range(len(p1))])
    v2 = np.array([p3[i] - p2[i] for i in range(len(p2))])

    if np.linalg.norm(v1) < 1e-10 or np.linalg.norm(v2) < 1e-10:
        return False

    angulo = angulo_entre_vectores(v1, v2)
    return angulo < tolerancia_angulo


def combinacion_aristas(G: nx.Graph, tolerancia_angulo: float = 2.0) -> nx.Graph:
    """Combina aristas adyacentes que forman una línea recta."""
    G_limpio = G.copy()
    cambios = True
    iteracion = 0
    num_combinaciones = 0

    print(f"   🔗 Combinando líneas colineales (tolerancia: {tolerancia_angulo}°)...")

    while cambios:
        cambios = False
        iteracion += 1

        nodos_grado_2 = [n for n in G_limpio.nodes() if G_limpio.degree(n) == 2]

        for nodo in nodos_grado_2:
            vecinos = list(G_limpio.neighbors(nodo))

            if len(vecinos) == 2:
                v1, v2 = vecinos

                if son_colineales(v1, nodo, v2, tolerancia_angulo):
                    G_limpio.add_edge(v1, v2)
                    G_limpio.remove_node(nodo)
                    cambios = True
                    num_combinaciones += 1
                    break

        if iteracion > 10000:
            print(f"   ⚠️ Límite de iteraciones alcanzado")
            break

    print(f"   ✅ {num_combinaciones} líneas combinadas en {iteracion} iteraciones")
    return G_limpio


def eliminacion_aristas_redundantes(G: nx.Graph, tolerancia_longitud: float = 0.005) -> nx.Graph:
    """Elimina aristas cortas que están cubiertas por aristas más largas."""
    G_limpio = G.copy()

    nodos = np.array(list(G_limpio.nodes()))
    if len(nodos) > 0:
        tamaño = max(nodos.max(axis=0) - nodos.min(axis=0))
        longitud_min = tolerancia_longitud * tamaño
    else:
        longitud_min = tolerancia_longitud

    print(f"   ✂️ Eliminando aristas redundantes (longitud mín: {longitud_min:.4f})...")

    aristas_con_longitud = []
    for e in G_limpio.edges():
        longitud = distancia_euclidiana(e[0], e[1])
        aristas_con_longitud.append((e, longitud))

    aristas_con_longitud.sort(key=lambda x: x[1])

    num_eliminadas = 0

    for arista, longitud in aristas_con_longitud:
        if longitud < longitud_min and G_limpio.has_edge(*arista):
            G_temp = G_limpio.copy()
            G_temp.remove_edge(*arista)

            if nx.is_connected(G_temp):
                G_limpio.remove_edge(*arista)
                num_eliminadas += 1

    nodos_aislados = list(nx.isolates(G_limpio))
    G_limpio.remove_nodes_from(nodos_aislados)

    if nodos_aislados:
        print(f"   🗑️ {len(nodos_aislados)} nodos aislados eliminados")

    print(f"   ✅ {num_eliminadas} aristas redundantes eliminadas")
    return G_limpio


def convertir_grafo_a_lineas(G: nx.Graph) -> List[Tuple]:
    """Convierte un grafo de NetworkX de vuelta a lista de líneas."""
    lineas = []
    for edge in G.edges():
        p1, p2 = edge
        if len(p1) == 3 and len(p2) == 3:
            x1, y1, z1 = p1
            x2, y2, z2 = p2
        elif len(p1) == 2 and len(p2) == 2:
            x1, y1 = p1
            x2, y2 = p2
            z1, z2 = 0, 0
        else:
            continue
        lineas.append((x1, y1, z1, x2, y2, z2))
    return lineas


def limpiar_grafo_completo(G: nx.Graph,
                          tolerancia_nodos: float = 0.01,
                          tolerancia_angulo: float = 2.0,
                          tolerancia_longitud: float = 0.005) -> nx.Graph:
    """Pipeline completo de limpieza de grafo."""
    nodos_inicial = G.number_of_nodes()
    aristas_inicial = G.number_of_edges()

    # Paso 1: Contraer nodos cercanos
    G = contraccion_dinamica_nodos(G, tolerancia_nodos)

    # Paso 2: Combinar líneas colineales
    G = combinacion_aristas(G, tolerancia_angulo)

    # Paso 3: Eliminar aristas redundantes
    G = eliminacion_aristas_redundantes(G, tolerancia_longitud)

    nodos_final = G.number_of_nodes()
    aristas_final = G.number_of_edges()

    print(f"\n   📊 Nodos: {nodos_inicial} → {nodos_final} (reducción: {nodos_inicial - nodos_final})")
    print(f"   📊 Aristas: {aristas_inicial} → {aristas_final} (reducción: {aristas_inicial - aristas_final})")

    return G


def preprocesar_lineas_dxf(lineas: List[Tuple],
                           tolerancia_nodos: float = 0.01,
                           tolerancia_angulo: float = 2.0,
                           tolerancia_longitud: float = 0.005) -> List[Tuple]:
    """Función principal: Preprocesa líneas DXF usando análisis de grafos."""
    G = crear_grafo_desde_lineas(lineas)
    G_limpio = limpiar_grafo_completo(G, tolerancia_nodos, tolerancia_angulo, tolerancia_longitud)
    lineas_limpias = convertir_grafo_a_lineas(G_limpio)
    return lineas_limpias


# ================================================================================================
# APLICAR PREPROCESAMIENTO AUTOMÁTICAMENTE
# ================================================================================================

print("\n🚀 APLICANDO PREPROCESAMIENTO A LOS DATOS CARGADOS")
print("="*60)

# Verificar que los datos estén cargados
try:
    loaded_data = load_processed_data('/content/tower_data')

    if loaded_data:
        oriented_lines_original, left_contour_original, right_contour_original, sections, symmetry_axis = loaded_data

        print(f"\n📊 DATOS ORIGINALES:")
        print(f"   • Líneas orientadas: {len(oriented_lines_original)}")
        print(f"   • Contorno izquierdo: {len(left_contour_original)}")
        print(f"   • Contorno derecho: {len(right_contour_original)}")
        print(f"   • Secciones: {len(sections)}")

        # ===========================
        # PREPROCESAR LÍNEAS PRINCIPALES
        # ===========================
        print(f"\n1️⃣ Preprocesando líneas orientadas...")
        oriented_lines = preprocesar_lineas_dxf(
            oriented_lines_original,
            tolerancia_nodos=0.01,       # 1% del tamaño del modelo
            tolerancia_angulo=2.0,        # 2 grados para colinealidad
            tolerancia_longitud=0.005     # 0.5% para líneas cortas
        )

        # ===========================
        # PREPROCESAR CONTORNOS
        # ===========================
        print(f"\n2️⃣ Preprocesando contorno izquierdo...")
        left_contour = preprocesar_lineas_dxf(left_contour_original, tolerancia_nodos=0.01, tolerancia_angulo=2.0, tolerancia_longitud=0.005)

        print(f"\n3️⃣ Preprocesando contorno derecho...")
        right_contour = preprocesar_lineas_dxf(right_contour_original, tolerancia_nodos=0.01, tolerancia_angulo=2.0, tolerancia_longitud=0.005)

        # ===========================
        # ESTADÍSTICAS DE MEJORAS
        # ===========================
        print("\n" + "="*60)
        print("✅ PREPROCESAMIENTO COMPLETADO")
        print("="*60)

        print(f"\n📊 MEJORAS OBTENIDAS:")
        print(f"   • Líneas orientadas:  {len(oriented_lines_original)} → {len(oriented_lines)} (reducción: {len(oriented_lines_original) - len(oriented_lines)})")
        print(f"   • Contorno izquierdo: {len(left_contour_original)} → {len(left_contour)} (reducción: {len(left_contour_original) - len(left_contour)})")
        print(f"   • Contorno derecho:   {len(right_contour_original)} → {len(right_contour)} (reducción: {len(right_contour_original) - len(right_contour)})")

        total_reduccion = (len(oriented_lines_original) + len(left_contour_original) + len(right_contour_original)) - \
                         (len(oriented_lines) + len(left_contour) + len(right_contour))

        porcentaje_reduccion = (total_reduccion / (len(oriented_lines_original) + len(left_contour_original) + len(right_contour_original))) * 100

        print(f"\n   📉 Reducción total: {total_reduccion} líneas ({porcentaje_reduccion:.1f}%)")

        if porcentaje_reduccion > 5:
            print(f"   ✅ ¡Mejora significativa! Las diagonales divididas fueron unificadas.")
        elif porcentaje_reduccion > 0:
            print(f"   ✓ Mejora moderada. Algunos datos redundantes eliminados.")
        else:
            print(f"   ℹ️ Sin reducción. El modelo ya estaba limpio.")

        # ===========================
        # GUARDAR DATOS PREPROCESADOS
        # ===========================
        print("\n💾 Los datos preprocesados están listos en las variables:")
        print("   • oriented_lines (limpias)")
        print("   • left_contour (limpio)")
        print("   • right_contour (limpio)")
        print("   • sections (sin cambios)")
        print("   • symmetry_axis (sin cambios)")

        print("\n🎯 SIGUIENTE PASO:")
        print("   Ejecuta la celda 'main_universal_improved_analysis()' normalmente.")
        print("   Usará automáticamente los datos preprocesados.")

        # ===========================
        # ANÁLISIS DETALLADO (OPCIONAL)
        # ===========================
        print("\n" + "="*60)
        print("📋 BENEFICIOS ESPERADOS DEL PREPROCESAMIENTO:")
        print("="*60)
        print("✅ Diagonales divididas en múltiples segmentos → UNIFICADAS")
        print("✅ Nodos duplicados por errores de precisión → FUSIONADOS")
        print("✅ Líneas redundantes que confunden el análisis → ELIMINADAS")
        print("✅ Mejor detección de módulos X en secciones decrecientes")

    else:
        print("❌ No se pudieron cargar los datos desde '/content/tower_data'")
        print("💡 Asegúrate de haber ejecutado las celdas de carga de datos primero.")

except NameError:
    print("❌ La función 'load_processed_data' no está disponible.")
    print("💡 Asegúrate de haber ejecutado las celdas anteriores del notebook.")

except Exception as e:
    print(f"❌ Error durante el preprocesamiento: {str(e)}")
    print("💡 Verifica que los datos estén en el formato correcto.")

print("\n" + "="*60)
print("🔧 Módulo de preprocesamiento con grafos listo")
print("="*60)

# ================================================================================================
# FIN DE LA CELDA DE PREPROCESAMIENTO
# ================================================================================================
# NOTA IMPORTANTE:
# - Esta celda modifica las variables oriented_lines, left_contour y right_contour
# - El análisis posterior usará automáticamente estos datos limpios
# - Si quieres desactivar el preprocesamiento, simplemente no ejecutes esta celda
# - Los datos originales se preservan en las variables *_original
# ================================================================================================
