# ================================================================================================
# ANÁLISIS DE MÓDULOS CON GRAFOS - VERSIÓN CORREGIDA CON LÓGICA DE COLINEALIDAD
# ================================================================================================
# CORRECCIONES PRINCIPALES:
# 1. Agrupa segmentos colineales para formar líneas continuas
# 2. Verifica que las horizontales vayan de lado a lado (contorno izquierdo → contorno derecho)
# 3. Filtra horizontales internas que no definen límites de módulos
# 4. Aplica la misma lógica a diagonales en módulos X
# ================================================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import math
import pandas as pd
import os
from typing import List, Tuple, Dict, Set

print("🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS (VERSIÓN CORREGIDA)")
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
# FUNCIONES DE AGRUPACIÓN DE LÍNEAS COLINEALES (NUEVO)
# ================================================================================================

def segmentos_son_colineales(seg1: Tuple[Tuple, Tuple], seg2: Tuple[Tuple, Tuple],
                            tolerancia_angulo: float = 2.0) -> bool:
    """
    Verifica si dos segmentos son colineales (están en la misma línea recta).

    Args:
        seg1: Tupla (punto1, punto2) del primer segmento
        seg2: Tupla (punto1, punto2) del segundo segmento
        tolerancia_angulo: Tolerancia en grados para considerar colineales

    Returns:
        True si los segmentos son colineales
    """
    p1_1, p1_2 = seg1
    p2_1, p2_2 = seg2

    # Verificar que los 4 puntos sean colineales
    # Tomamos el primer punto del primer segmento como referencia
    if son_colineales(p1_1, p1_2, p2_1, tolerancia_angulo) and \
       son_colineales(p1_1, p1_2, p2_2, tolerancia_angulo):
        return True

    return False


def agrupar_segmentos_colineales(G: nx.Graph, section_bounds: Tuple,
                                tipo: str = 'horizontal',
                                tolerance_direccion: float = 0.01,
                                tolerance_colineal: float = 2.0) -> List[Dict]:
    """
    Agrupa segmentos colineales del grafo para formar líneas continuas.

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        tipo: 'horizontal', 'vertical' o 'diagonal'
        tolerance_direccion: Tolerancia para clasificar la dirección
        tolerance_colineal: Tolerancia en grados para considerar colineales

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

    # Agrupar segmentos colineales
    grupos = []
    segmentos_usados = set()

    for i, seg1 in enumerate(segmentos):
        if i in segmentos_usados:
            continue

        # Crear nuevo grupo
        grupo = [seg1]
        segmentos_usados.add(i)

        # Buscar segmentos colineales
        for j, seg2 in enumerate(segmentos):
            if j in segmentos_usados:
                continue

            # Verificar si seg2 es colineal con algún segmento del grupo
            es_colineal_con_grupo = False
            for seg_grupo in grupo:
                if segmentos_son_colineales(seg_grupo, seg2, tolerance_colineal):
                    es_colineal_con_grupo = True
                    break

            if es_colineal_con_grupo:
                grupo.append(seg2)
                segmentos_usados.add(j)

        # Calcular información del grupo
        todos_los_puntos = []
        for seg in grupo:
            todos_los_puntos.extend([seg[0], seg[1]])

        # Calcular extensión en X e Y
        x_coords = [p[0] for p in todos_los_puntos]
        y_coords = [p[1] for p in todos_los_puntos]

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        y_avg = sum(y_coords) / len(y_coords)

        grupos.append({
            'segmentos': grupo,
            'num_segmentos': len(grupo),
            'x_min': x_min,
            'x_max': x_max,
            'extension_x': x_max - x_min,
            'y_min': y_min,
            'y_max': y_max,
            'y_avg': y_avg,
            'puntos': todos_los_puntos
        })

    return grupos


def horizontal_va_lado_a_lado(grupo: Dict, contorno_izq: List, contorno_der: List,
                              tolerance: float = 0.5) -> bool:
    """
    Verifica si un grupo de horizontales colineales va de lado a lado de la torre.

    Args:
        grupo: Diccionario con información del grupo (de agrupar_segmentos_colineales)
        contorno_izq: Lista de coordenadas X del contorno izquierdo en la sección
        contorno_der: Lista de coordenadas X del contorno derecho en la sección
        tolerance: Tolerancia en metros para considerar que llega al contorno

    Returns:
        True si la horizontal va de lado a lado
    """
    x_min = grupo['x_min']
    x_max = grupo['x_max']
    y_avg = grupo['y_avg']

    # Obtener los límites de los contornos en esta altura
    # (simplificación: usamos los valores extremos de los contornos)
    if not contorno_izq or not contorno_der:
        return False

    limite_izq = min(contorno_izq)
    limite_der = max(contorno_der)

    # Verificar si llega cerca de ambos contornos
    llega_izquierda = abs(x_min - limite_izq) < tolerance
    llega_derecha = abs(x_max - limite_der) < tolerance

    return llega_izquierda and llega_derecha


def obtener_contornos_en_seccion(G: nx.Graph, section_bounds: Tuple,
                                symmetry_axis: float) -> Tuple[List, List]:
    """
    Obtiene las coordenadas X de los contornos izquierdo y derecho en una sección.

    Args:
        G: Grafo de NetworkX
        section_bounds: (y_start, y_end) límites de la sección
        symmetry_axis: Coordenada X del eje de simetría

    Returns:
        (contorno_izq, contorno_der): Listas de coordenadas X
    """
    y_start, y_end = section_bounds

    contorno_izq = []
    contorno_der = []

    for node in G.nodes():
        if len(node) >= 2:
            x, y = node[0], node[1]

            if y_start <= y <= y_end:
                if x < symmetry_axis:
                    contorno_izq.append(x)
                else:
                    contorno_der.append(x)

    return contorno_izq, contorno_der


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
    # Paso 1: Obtener contornos
    contorno_izq, contorno_der = obtener_contornos_en_seccion(G, section_bounds, symmetry_axis)

    if verbose:
        print(f"    📊 Contornos: Izq [{min(contorno_izq):.2f}], Der [{max(contorno_der):.2f}]")

    # Paso 2: Agrupar horizontales colineales
    grupos_horizontales = agrupar_segmentos_colineales(
        G, section_bounds,
        tipo='horizontal',
        tolerance_direccion=tolerance_horizontal,
        tolerance_colineal=tolerance_colineal
    )

    if verbose:
        print(f"    📊 Grupos horizontales encontrados: {len(grupos_horizontales)}")

    # Paso 3: Filtrar solo las que van de lado a lado
    alturas_validas = []

    for grupo in grupos_horizontales:
        va_lado_a_lado = horizontal_va_lado_a_lado(
            grupo, contorno_izq, contorno_der, tolerance_contorno
        )

        if verbose:
            print(f"       Y={grupo['y_avg']:.3f}: {grupo['num_segmentos']} segs, "
                  f"X=[{grupo['x_min']:.2f} - {grupo['x_max']:.2f}], "
                  f"ext={grupo['extension_x']:.2f}, "
                  f"lado_a_lado={'✅' if va_lado_a_lado else '❌'}")

        if va_lado_a_lado:
            alturas_validas.append(grupo['y_avg'])

    if verbose:
        print(f"    ✅ Horizontales válidas (lado a lado): {len(alturas_validas)}")

    return sorted(alturas_validas)


# ================================================================================================
# DETECCIÓN DE MÓDULOS X (SIN CAMBIOS)
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
    deteccion_x = detectar_modulos_x_mejorado(G, (y_start, y_end), symmetry_axis, tolerance)

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

        # Agregar límites de sección
        alturas_modulos = sorted(list(set([y_start, y_end] + alturas_diagonales)))

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

        # Agregar límites de sección
        alturas_modulos = sorted(list(set([y_start, y_end] + alturas_horizontales)))

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
print("✅ ANÁLISIS CON COLINEALIDAD CORREGIDO COMPLETADO")
print("="*60)
