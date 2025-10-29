# ================================================================================================
# CELDA DE VISUALIZACIÓN GRÁFICA DE GRAFOS - PARA COLAB
# ================================================================================================
# INSTRUCCIONES:
# 1. Copia esta celda COMPLETA en tu notebook de Colab
# 2. Colócala DESPUÉS de la celda de preprocesamiento
# 3. Ejecuta para ver visualizaciones interactivas de los grafos
# ================================================================================================

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

print("🎨 MÓDULO DE VISUALIZACIÓN DE GRAFOS")
print("="*60)

# ================================================================================================
# FUNCIONES DE VISUALIZACIÓN
# ================================================================================================

def visualizar_grafo_basico(G, titulo="Grafo", figsize=(12, 10), node_size=20, font_size=8):
    """
    Visualización básica de un grafo.

    Args:
        G: Grafo de NetworkX
        titulo: Título de la visualización
        figsize: Tamaño de la figura
        node_size: Tamaño de los nodos
        font_size: Tamaño de fuente
    """
    plt.figure(figsize=figsize)

    # Usar posiciones reales de los nodos si están disponibles
    pos = {}
    for node in G.nodes():
        if len(node) >= 2:
            # Usar coordenadas X, Y (ignorar Z para visualización 2D)
            pos[node] = (node[0], node[1])
        else:
            # Si no hay coordenadas, usar layout automático
            pos = nx.spring_layout(G, seed=42)
            break

    # Dibujar el grafo
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='lightblue',
                          edgecolors='black', linewidths=0.5, alpha=0.7)

    nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.0, alpha=0.6)

    # Información del grafo
    info_text = f"Nodos: {G.number_of_nodes()}\nAristas: {G.number_of_edges()}"
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


def visualizar_grafo_comparativo(G_antes, G_despues, figsize=(20, 10)):
    """
    Visualización comparativa de grafos antes y después del preprocesamiento.

    Args:
        G_antes: Grafo antes del preprocesamiento
        G_despues: Grafo después del preprocesamiento
        figsize: Tamaño de la figura
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # === GRAFO ANTES ===
    plt.sca(ax1)
    pos_antes = {}
    for node in G_antes.nodes():
        if len(node) >= 2:
            pos_antes[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G_antes, pos_antes, node_size=15, node_color='lightcoral',
                          edgecolors='darkred', linewidths=0.5, alpha=0.6, ax=ax1)

    nx.draw_networkx_edges(G_antes, pos_antes, edge_color='gray', width=0.8, alpha=0.4, ax=ax1)

    info_antes = f"Nodos: {G_antes.number_of_nodes()}\nAristas: {G_antes.number_of_edges()}"
    ax1.text(0.02, 0.98, info_antes, transform=ax1.transAxes,
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

    ax1.set_title("ANTES DEL PREPROCESAMIENTO", fontsize=14, fontweight='bold', color='darkred')
    ax1.axis('equal')
    ax1.grid(True, alpha=0.3)

    # === GRAFO DESPUÉS ===
    plt.sca(ax2)
    pos_despues = {}
    for node in G_despues.nodes():
        if len(node) >= 2:
            pos_despues[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G_despues, pos_despues, node_size=15, node_color='lightgreen',
                          edgecolors='darkgreen', linewidths=0.5, alpha=0.6, ax=ax2)

    nx.draw_networkx_edges(G_despues, pos_despues, edge_color='gray', width=0.8, alpha=0.4, ax=ax2)

    info_despues = f"Nodos: {G_despues.number_of_nodes()}\nAristas: {G_despues.number_of_edges()}"
    ax2.text(0.02, 0.98, info_despues, transform=ax2.transAxes,
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

    # Calcular mejoras
    reduccion_nodos = G_antes.number_of_nodes() - G_despues.number_of_nodes()
    reduccion_aristas = G_antes.number_of_edges() - G_despues.number_of_edges()

    mejoras = f"Reducción:\nNodos: -{reduccion_nodos}\nAristas: -{reduccion_aristas}"
    ax2.text(0.98, 0.98, mejoras, transform=ax2.transAxes,
             fontsize=11, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

    ax2.set_title("DESPUÉS DEL PREPROCESAMIENTO", fontsize=14, fontweight='bold', color='darkgreen')
    ax2.axis('equal')
    ax2.grid(True, alpha=0.3)

    plt.suptitle("COMPARACIÓN DE GRAFOS", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()


def visualizar_grafo_con_estadisticas(G, titulo="Grafo con Estadísticas", figsize=(16, 10)):
    """
    Visualización del grafo con estadísticas detalladas.

    Args:
        G: Grafo de NetworkX
        titulo: Título de la visualización
        figsize: Tamaño de la figura
    """
    fig = plt.figure(figsize=figsize)

    # Crear grid de subplots
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    ax_main = fig.add_subplot(gs[:, :2])  # Grafo principal
    ax_degree = fig.add_subplot(gs[0, 2])  # Distribución de grados
    ax_lengths = fig.add_subplot(gs[1, 2])  # Longitudes de aristas

    # === GRAFO PRINCIPAL ===
    pos = {}
    for node in G.nodes():
        if len(node) >= 2:
            pos[node] = (node[0], node[1])

    # Colorear nodos por grado
    degrees = dict(G.degree())
    node_colors = [degrees[node] for node in G.nodes()]

    nodes = nx.draw_networkx_nodes(G, pos, node_size=30, node_color=node_colors,
                                   cmap='YlOrRd', edgecolors='black', linewidths=0.5,
                                   alpha=0.7, ax=ax_main)

    nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.0, alpha=0.5, ax=ax_main)

    # Colorbar para grados
    plt.colorbar(nodes, ax=ax_main, label='Grado del Nodo')

    info = f"Nodos: {G.number_of_nodes()}\nAristas: {G.number_of_edges()}"
    ax_main.text(0.02, 0.98, info, transform=ax_main.transAxes,
                 fontsize=11, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax_main.set_title(titulo, fontsize=14, fontweight='bold')
    ax_main.axis('equal')
    ax_main.grid(True, alpha=0.3)

    # === DISTRIBUCIÓN DE GRADOS ===
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    degree_count = {}
    for deg in degree_sequence:
        degree_count[deg] = degree_count.get(deg, 0) + 1

    degrees = list(degree_count.keys())
    counts = list(degree_count.values())

    ax_degree.bar(degrees, counts, color='steelblue', alpha=0.7, edgecolor='black')
    ax_degree.set_xlabel('Grado', fontsize=10)
    ax_degree.set_ylabel('Cantidad de Nodos', fontsize=10)
    ax_degree.set_title('Distribución de Grados', fontsize=11, fontweight='bold')
    ax_degree.grid(True, alpha=0.3, axis='y')

    # Agregar texto informativo
    max_degree = max(degree_sequence) if degree_sequence else 0
    avg_degree = np.mean(degree_sequence) if degree_sequence else 0

    degree_info = f"Grado máx: {max_degree}\nGrado prom: {avg_degree:.1f}"
    ax_degree.text(0.98, 0.98, degree_info, transform=ax_degree.transAxes,
                   fontsize=9, verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

    # === LONGITUDES DE ARISTAS ===
    edge_lengths = []
    for edge in G.edges():
        n1, n2 = edge
        if len(n1) >= 2 and len(n2) >= 2:
            length = np.sqrt((n2[0] - n1[0])**2 + (n2[1] - n1[1])**2)
            edge_lengths.append(length)

    if edge_lengths:
        ax_lengths.hist(edge_lengths, bins=30, color='coral', alpha=0.7, edgecolor='black')
        ax_lengths.set_xlabel('Longitud de Arista', fontsize=10)
        ax_lengths.set_ylabel('Cantidad', fontsize=10)
        ax_lengths.set_title('Distribución de Longitudes', fontsize=11, fontweight='bold')
        ax_lengths.grid(True, alpha=0.3, axis='y')

        # Agregar estadísticas
        min_length = min(edge_lengths)
        max_length = max(edge_lengths)
        avg_length = np.mean(edge_lengths)

        length_info = f"Mín: {min_length:.2f}\nMáx: {max_length:.2f}\nProm: {avg_length:.2f}"
        ax_lengths.text(0.98, 0.98, length_info, transform=ax_lengths.transAxes,
                        fontsize=9, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    plt.suptitle("ANÁLISIS DETALLADO DEL GRAFO", fontsize=15, fontweight='bold', y=0.98)


def visualizar_proceso_limpieza_completo(lineas_original, figsize=(20, 15)):
    """
    Visualización del proceso completo de limpieza mostrando cada paso.

    Args:
        lineas_original: Líneas originales antes del preprocesamiento
        figsize: Tamaño de la figura
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()

    # === PASO 0: GRAFO ORIGINAL ===
    G0 = crear_grafo_desde_lineas(lineas_original)

    pos0 = {}
    for node in G0.nodes():
        if len(node) >= 2:
            pos0[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G0, pos0, node_size=15, node_color='lightgray',
                          edgecolors='black', linewidths=0.5, alpha=0.6, ax=axes[0])
    nx.draw_networkx_edges(G0, pos0, edge_color='gray', width=0.8, alpha=0.4, ax=axes[0])

    info0 = f"Nodos: {G0.number_of_nodes()}\nAristas: {G0.number_of_edges()}"
    axes[0].text(0.02, 0.98, info0, transform=axes[0].transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    axes[0].set_title("PASO 0: Grafo Original", fontsize=12, fontweight='bold')
    axes[0].axis('equal')
    axes[0].grid(True, alpha=0.3)

    # === PASO 1: DESPUÉS DE CONTRACCIÓN DE NODOS ===
    G1 = contraccion_dinamica_nodos(G0.copy(), tolerancia=0.01)

    pos1 = {}
    for node in G1.nodes():
        if len(node) >= 2:
            pos1[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G1, pos1, node_size=15, node_color='lightcoral',
                          edgecolors='darkred', linewidths=0.5, alpha=0.6, ax=axes[1])
    nx.draw_networkx_edges(G1, pos1, edge_color='gray', width=0.8, alpha=0.4, ax=axes[1])

    reduccion1 = G0.number_of_nodes() - G1.number_of_nodes()
    info1 = f"Nodos: {G1.number_of_nodes()} (-{reduccion1})\nAristas: {G1.number_of_edges()}"
    axes[1].text(0.02, 0.98, info1, transform=axes[1].transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

    axes[1].set_title("PASO 1: Contracción de Nodos", fontsize=12, fontweight='bold', color='darkred')
    axes[1].axis('equal')
    axes[1].grid(True, alpha=0.3)

    # === PASO 2: DESPUÉS DE COMBINACIÓN DE ARISTAS ===
    G2 = combinacion_aristas(G1.copy(), tolerancia_angulo=2.0)

    pos2 = {}
    for node in G2.nodes():
        if len(node) >= 2:
            pos2[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G2, pos2, node_size=15, node_color='lightyellow',
                          edgecolors='orange', linewidths=0.5, alpha=0.6, ax=axes[2])
    nx.draw_networkx_edges(G2, pos2, edge_color='gray', width=0.8, alpha=0.4, ax=axes[2])

    reduccion2_nodos = G1.number_of_nodes() - G2.number_of_nodes()
    reduccion2_aristas = G1.number_of_edges() - G2.number_of_edges()
    info2 = f"Nodos: {G2.number_of_nodes()} (-{reduccion2_nodos})\nAristas: {G2.number_of_edges()} (-{reduccion2_aristas})"
    axes[2].text(0.02, 0.98, info2, transform=axes[2].transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    axes[2].set_title("PASO 2: Combinación de Líneas Colineales", fontsize=12, fontweight='bold', color='orange')
    axes[2].axis('equal')
    axes[2].grid(True, alpha=0.3)

    # === PASO 3: DESPUÉS DE ELIMINACIÓN DE REDUNDANTES ===
    G3 = eliminacion_aristas_redundantes(G2.copy(), tolerancia_longitud=0.005)

    pos3 = {}
    for node in G3.nodes():
        if len(node) >= 2:
            pos3[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G3, pos3, node_size=15, node_color='lightgreen',
                          edgecolors='darkgreen', linewidths=0.5, alpha=0.6, ax=axes[3])
    nx.draw_networkx_edges(G3, pos3, edge_color='gray', width=0.8, alpha=0.4, ax=axes[3])

    reduccion3_nodos = G2.number_of_nodes() - G3.number_of_nodes()
    reduccion3_aristas = G2.number_of_edges() - G3.number_of_edges()
    info3 = f"Nodos: {G3.number_of_nodes()} (-{reduccion3_nodos})\nAristas: {G3.number_of_edges()} (-{reduccion3_aristas})"
    axes[3].text(0.02, 0.98, info3, transform=axes[3].transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

    # Resumen final
    reduccion_total_nodos = G0.number_of_nodes() - G3.number_of_nodes()
    reduccion_total_aristas = G0.number_of_edges() - G3.number_of_edges()
    resumen = f"TOTAL:\n-{reduccion_total_nodos} nodos\n-{reduccion_total_aristas} aristas"
    axes[3].text(0.98, 0.98, resumen, transform=axes[3].transAxes,
                 fontsize=10, verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9))

    axes[3].set_title("PASO 3: Eliminación de Redundantes", fontsize=12, fontweight='bold', color='darkgreen')
    axes[3].axis('equal')
    axes[3].grid(True, alpha=0.3)

    plt.suptitle("PROCESO COMPLETO DE LIMPIEZA DEL GRAFO", fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()


def visualizar_zoom_area(G, x_center, y_center, radio=5.0, figsize=(12, 10)):
    """
    Visualización con zoom en un área específica del grafo.

    Args:
        G: Grafo de NetworkX
        x_center, y_center: Coordenadas del centro del zoom
        radio: Radio del área de zoom
        figsize: Tamaño de la figura
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # === GRAFO COMPLETO ===
    pos = {}
    for node in G.nodes():
        if len(node) >= 2:
            pos[node] = (node[0], node[1])

    nx.draw_networkx_nodes(G, pos, node_size=10, node_color='lightblue',
                          edgecolors='black', linewidths=0.3, alpha=0.5, ax=ax1)
    nx.draw_networkx_edges(G, pos, edge_color='gray', width=0.5, alpha=0.3, ax=ax1)

    # Dibujar rectángulo de zoom
    rect = Rectangle((x_center - radio, y_center - radio), radio * 2, radio * 2,
                     linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
    ax1.add_patch(rect)

    ax1.set_title("Vista Completa", fontsize=12, fontweight='bold')
    ax1.axis('equal')
    ax1.grid(True, alpha=0.3)

    # === ÁREA DE ZOOM ===
    # Filtrar nodos en el área de zoom
    nodes_in_area = []
    for node in G.nodes():
        if len(node) >= 2:
            x, y = node[0], node[1]
            if (x_center - radio <= x <= x_center + radio and
                y_center - radio <= y <= y_center + radio):
                nodes_in_area.append(node)

    # Crear subgrafo con nodos en el área
    G_zoom = G.subgraph(nodes_in_area)

    pos_zoom = {}
    for node in G_zoom.nodes():
        if len(node) >= 2:
            pos_zoom[node] = (node[0], node[1])

    # Colorear nodos por grado
    degrees = dict(G_zoom.degree())
    node_colors = [degrees[node] for node in G_zoom.nodes()]

    if len(G_zoom.nodes()) > 0:
        nodes = nx.draw_networkx_nodes(G_zoom, pos_zoom, node_size=80, node_color=node_colors,
                                      cmap='YlOrRd', edgecolors='black', linewidths=1.0,
                                      alpha=0.8, ax=ax2)

        nx.draw_networkx_edges(G_zoom, pos_zoom, edge_color='gray', width=2.0, alpha=0.6, ax=ax2)

        # Etiquetas de nodos (solo para grafos pequeños en zoom)
        if len(G_zoom.nodes()) < 30:
            labels = {node: f"{i+1}" for i, node in enumerate(G_zoom.nodes())}
            nx.draw_networkx_labels(G_zoom, pos_zoom, labels, font_size=8, ax=ax2)

        plt.colorbar(nodes, ax=ax2, label='Grado del Nodo')

    info_zoom = f"Nodos en área: {G_zoom.number_of_nodes()}\nAristas: {G_zoom.number_of_edges()}"
    ax2.text(0.02, 0.98, info_zoom, transform=ax2.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    ax2.set_xlim(x_center - radio, x_center + radio)
    ax2.set_ylim(y_center - radio, y_center + radio)
    ax2.set_title(f"Zoom: Centro({x_center:.1f}, {y_center:.1f}), Radio={radio:.1f}",
                  fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.suptitle("VISUALIZACIÓN CON ZOOM", fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()


# ================================================================================================
# EJECUCIÓN AUTOMÁTICA DE VISUALIZACIONES
# ================================================================================================

print("\n🎨 GENERANDO VISUALIZACIONES...")
print("="*60)

try:
    # Verificar que las variables necesarias estén disponibles
    if 'oriented_lines_original' in globals() and 'oriented_lines' in globals():

        print("\n📊 Visualización 1: Comparación Antes/Después")
        print("-"*60)

        # Crear grafos
        G_original = crear_grafo_desde_lineas(oriented_lines_original)
        G_procesado = crear_grafo_desde_lineas(oriented_lines)

        # Visualización comparativa
        visualizar_grafo_comparativo(G_original, G_procesado, figsize=(20, 10))
        plt.show()

        print("\n📊 Visualización 2: Proceso Completo de Limpieza")
        print("-"*60)
        print("(Mostrando cada paso del preprocesamiento...)")

        # Visualización del proceso completo
        visualizar_proceso_limpieza_completo(oriented_lines_original, figsize=(20, 15))
        plt.show()

        print("\n📊 Visualización 3: Estadísticas Detalladas del Grafo Final")
        print("-"*60)

        # Visualización con estadísticas
        visualizar_grafo_con_estadisticas(G_procesado,
                                         titulo="Grafo Preprocesado - Análisis Completo",
                                         figsize=(16, 10))
        plt.show()

        # Calcular centro del modelo para zoom
        coords = np.array(list(G_procesado.nodes()))
        if len(coords) > 0:
            x_center = np.mean(coords[:, 0])
            y_center = np.mean(coords[:, 1])

            # Calcular radio apropiado (10% del tamaño del modelo)
            x_range = coords[:, 0].max() - coords[:, 0].min()
            y_range = coords[:, 1].max() - coords[:, 1].min()
            radio = max(x_range, y_range) * 0.1

            print("\n📊 Visualización 4: Zoom en Área Central")
            print("-"*60)
            print(f"Centro: ({x_center:.2f}, {y_center:.2f}), Radio: {radio:.2f}")

            # Visualización con zoom
            visualizar_zoom_area(G_procesado, x_center, y_center, radio, figsize=(18, 9))
            plt.show()

        print("\n" + "="*60)
        print("✅ VISUALIZACIONES COMPLETADAS")
        print("="*60)

        print("\n📋 RESUMEN DE VISUALIZACIONES:")
        print(f"   1. ✅ Comparación antes/después del preprocesamiento")
        print(f"   2. ✅ Proceso completo paso a paso (4 etapas)")
        print(f"   3. ✅ Estadísticas detalladas del grafo final")
        print(f"   4. ✅ Zoom en área central del modelo")

        print("\n💡 INTERPRETACIÓN:")
        print("   • Nodos ROJOS → Antes del preprocesamiento (muchos)")
        print("   • Nodos VERDES → Después del preprocesamiento (menos)")
        print("   • Aristas GRISES → Conexiones entre nodos")
        print("   • Colores por GRADO → Cuántas conexiones tiene cada nodo")

        # Estadísticas finales
        reduccion_nodos = G_original.number_of_nodes() - G_procesado.number_of_nodes()
        reduccion_aristas = G_original.number_of_edges() - G_procesado.number_of_edges()
        porcentaje_nodos = (reduccion_nodos / G_original.number_of_nodes()) * 100 if G_original.number_of_nodes() > 0 else 0
        porcentaje_aristas = (reduccion_aristas / G_original.number_of_edges()) * 100 if G_original.number_of_edges() > 0 else 0

        print("\n📊 MEJORAS CUANTIFICADAS:")
        print(f"   • Reducción de nodos:   {reduccion_nodos} ({porcentaje_nodos:.1f}%)")
        print(f"   • Reducción de aristas: {reduccion_aristas} ({porcentaje_aristas:.1f}%)")

        if porcentaje_nodos > 20 or porcentaje_aristas > 20:
            print(f"   ✅ ¡Mejora significativa! El grafo fue optimizado considerablemente.")
        elif porcentaje_nodos > 5 or porcentaje_aristas > 5:
            print(f"   ✓ Mejora moderada. Algunas redundancias eliminadas.")
        else:
            print(f"   ℹ️ Mejora mínima. El modelo ya estaba relativamente limpio.")

    else:
        print("⚠️ Variables no encontradas.")
        print("💡 Asegúrate de haber ejecutado la celda de preprocesamiento primero.")
        print("   Las variables esperadas son: oriented_lines_original, oriented_lines")

except NameError as e:
    print(f"❌ Error: Variable no encontrada - {str(e)}")
    print("💡 Ejecuta la celda de preprocesamiento antes de esta celda de visualización.")

except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
    print("💡 Verifica que todos los módulos necesarios estén cargados.")

print("\n" + "="*60)
print("🎨 Módulo de visualización de grafos listo")
print("="*60)

# ================================================================================================
# FUNCIONES ADICIONALES PARA USO MANUAL (OPCIONAL)
# ================================================================================================

print("\n💡 FUNCIONES DISPONIBLES PARA VISUALIZACIÓN PERSONALIZADA:")
print("   • visualizar_grafo_basico(G, titulo='...')")
print("   • visualizar_grafo_comparativo(G_antes, G_despues)")
print("   • visualizar_grafo_con_estadisticas(G, titulo='...')")
print("   • visualizar_proceso_limpieza_completo(lineas_original)")
print("   • visualizar_zoom_area(G, x_center, y_center, radio=5.0)")
print("\nEjemplo de uso:")
print("   G = crear_grafo_desde_lineas(oriented_lines)")
print("   visualizar_grafo_basico(G, titulo='Mi Grafo')")

# ================================================================================================
# FIN DE LA CELDA DE VISUALIZACIÓN
# ================================================================================================
