# ================================================================================================
# CELDA DE DIAGNÓSTICO - DETECTAR POR QUÉ NO ENCUENTRA MÓDULOS X
# ================================================================================================
# Ejecuta esta celda para diagnosticar el problema
# ================================================================================================

import matplotlib.pyplot as plt
import numpy as np

print("🔍 DIAGNÓSTICO: ¿Por qué no detecta módulos X?")
print("="*60)

# Analizar SOLO el tramo 1 (donde dices que hay 8 módulos X)
tramo_1 = sections[0]
y_start = tramo_1['altura_inicio']
y_end = tramo_1['altura_fin']

print(f"\n📍 TRAMO 1: Y=[{y_start:.3f} - {y_end:.3f}]")
print(f"   Tipo: {tramo_1['tipo']}")
print(f"   Según tu análisis: 8 módulos X con horizontal en el centro")

# 1. Ver distribución de grados EN EL TRAMO 1
print(f"\n1️⃣ DISTRIBUCIÓN DE GRADOS EN TRAMO 1:")
nodos_en_tramo = []
for node in G.nodes():
    if len(node) >= 2:
        y = node[1]
        if y_start <= y <= y_end:
            nodos_en_tramo.append(node)

print(f"   • Nodos totales en tramo: {len(nodos_en_tramo)}")

grados_en_tramo = {}
for node in nodos_en_tramo:
    grado = G.degree(node)
    x, y = node[0], node[1]
    if grado not in grados_en_tramo:
        grados_en_tramo[grado] = []
    grados_en_tramo[grado].append({'node': node, 'x': x, 'y': y})

for grado in sorted(grados_en_tramo.keys(), reverse=True):
    nodos = grados_en_tramo[grado]
    print(f"   • Grado {grado}: {len(nodos)} nodos")

    # Mostrar primeros 3 nodos de cada grado
    for i, info in enumerate(nodos[:3]):
        dist_eje = abs(info['x'] - symmetry_axis)
        print(f"      - Nodo {i+1}: X={info['x']:.3f}, Y={info['y']:.3f}, dist_eje={dist_eje:.3f}")

# 2. Ver nodos de ALTO grado (4, 5, 6, 7, 8...)
print(f"\n2️⃣ ANÁLISIS DE NODOS DE ALTO GRADO (>=4):")
nodos_alto_grado = []
for grado in grados_en_tramo:
    if grado >= 4:
        nodos_alto_grado.extend(grados_en_tramo[grado])

print(f"   • Nodos con grado >= 4: {len(nodos_alto_grado)}")

# Agrupar por cercanía al eje
tolerance = 0.05
max_coords = max([abs(n[0]) for n in G.nodes() if len(n) >= 2])
threshold_eje = tolerance * 10

cerca_eje = []
lejos_eje = []

for info in nodos_alto_grado:
    dist = abs(info['x'] - symmetry_axis)
    if dist < threshold_eje:
        cerca_eje.append(info)
    else:
        lejos_eje.append(info)

print(f"   • Cerca del eje (dist < {threshold_eje:.3f}): {len(cerca_eje)}")
print(f"   • Lejos del eje (dist >= {threshold_eje:.3f}): {len(lejos_eje)}")

# 3. Analizar en detalle los nodos cerca del eje
print(f"\n3️⃣ NODOS CERCA DEL EJE:")
if cerca_eje:
    for i, info in enumerate(cerca_eje[:5]):  # Mostrar primeros 5
        node = info['node']
        x, y = info['x'], info['y']
        grado = G.degree(node)
        dist = abs(x - symmetry_axis)

        print(f"\n   Nodo {i+1}: X={x:.3f}, Y={y:.3f}, Grado={grado}, Dist_eje={dist:.3f}")

        # Ver vecinos
        vecinos = list(G.neighbors(node))
        print(f"      Vecinos ({len(vecinos)}):")
        for j, vecino in enumerate(vecinos[:6]):  # Mostrar primeros 6
            vx, vy = vecino[0], vecino[1]
            # Ver si es horizontal, vertical o diagonal
            if abs(vy - y) < 0.01:
                tipo = "horizontal"
            elif abs(vx - x) < 0.01:
                tipo = "vertical"
            else:
                tipo = "diagonal"
            print(f"         {j+1}. X={vx:.3f}, Y={vy:.3f} ({tipo})")
else:
    print("   ❌ NO HAY nodos de alto grado cerca del eje!")
    print(f"   💡 Threshold actual: {threshold_eje:.3f}")
    print(f"   💡 Eje de simetría: {symmetry_axis:.3f}")

    # Mostrar los más cercanos aunque estén lejos
    print(f"\n   📊 Nodos más cercanos al eje (aunque lejos del threshold):")
    todos_nodos_tramo = []
    for grado in grados_en_tramo:
        todos_nodos_tramo.extend(grados_en_tramo[grado])

    # Ordenar por distancia al eje
    todos_nodos_tramo.sort(key=lambda n: abs(n['x'] - symmetry_axis))

    for i, info in enumerate(todos_nodos_tramo[:10]):  # Mostrar 10 más cercanos
        node = info['node']
        x, y = info['x'], info['y']
        grado = G.degree(node)
        dist = abs(x - symmetry_axis)
        print(f"      {i+1}. X={x:.3f}, Y={y:.3f}, Grado={grado}, Dist={dist:.3f}")

# 4. Visualizar el tramo 1
print(f"\n4️⃣ VISUALIZACIÓN DEL TRAMO 1:")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Vista completa de la torre
ax1.set_title('Torre Completa', fontsize=14, fontweight='bold')
for edge in G.edges():
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        ax1.plot([n1[0], n2[0]], [n1[1], n2[1]], 'gray', linewidth=0.5, alpha=0.3)

# Resaltar tramo 1
ax1.axhline(y_start, color='red', linestyle='--', linewidth=2, label=f'Tramo 1: Y={y_start:.1f}')
ax1.axhline(y_end, color='red', linestyle='--', linewidth=2, label=f'Y={y_end:.1f}')
ax1.axvline(symmetry_axis, color='green', linestyle=':', linewidth=2, label=f'Eje: X={symmetry_axis:.1f}')

# Marcar nodos de alto grado en tramo 1
for info in nodos_alto_grado:
    x, y = info['x'], info['y']
    grado = G.degree(info['node'])
    color = 'red' if abs(x - symmetry_axis) < threshold_eje else 'orange'
    ax1.scatter(x, y, c=color, s=100, marker='o', edgecolors='black', linewidths=2,
                label=f'Grado {grado}' if f'Grado {grado}' not in [l.get_label() for l in ax1.get_lines()] else "")

ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right')
ax1.axis('equal')

# Zoom en tramo 1
ax2.set_title(f'ZOOM: Tramo 1 (Y=[{y_start:.1f} - {y_end:.1f}])', fontsize=14, fontweight='bold')

# Dibujar aristas del tramo 1
for edge in G.edges():
    n1, n2 = edge
    if len(n1) >= 2 and len(n2) >= 2:
        y1, y2 = n1[1], n2[1]
        # Dibujar si ambos extremos están en el tramo
        if (y_start <= y1 <= y_end and y_start <= y2 <= y_end):
            # Colorear por tipo
            if abs(y1 - y2) < 0.01:
                color = 'blue'  # Horizontal
                linewidth = 2
                alpha = 0.7
            elif abs(n1[0] - n2[0]) < 0.01:
                color = 'gray'  # Vertical
                linewidth = 1
                alpha = 0.5
            else:
                color = 'green'  # Diagonal
                linewidth = 1.5
                alpha = 0.6

            ax2.plot([n1[0], n2[0]], [n1[1], n2[1]], color=color, linewidth=linewidth, alpha=alpha)

# Marcar nodos por grado
for grado in sorted(grados_en_tramo.keys(), reverse=True):
    if grado >= 4:
        for info in grados_en_tramo[grado]:
            x, y = info['x'], info['y']
            dist = abs(x - symmetry_axis)

            if dist < threshold_eje:
                color = 'red'
                size = 150
                marker = 'o'
            else:
                color = 'orange'
                size = 100
                marker = 's'

            ax2.scatter(x, y, c=color, s=size, marker=marker, edgecolors='black',
                       linewidths=2, zorder=10, label=f'Grado {grado}' if f'Grado {grado}' not in [l.get_label() for l in ax2.lines] else "")

            # Etiqueta con el grado
            ax2.text(x, y, str(grado), fontsize=8, ha='center', va='center',
                    color='white', fontweight='bold', zorder=11)

# Eje de simetría
ax2.axvline(symmetry_axis, color='green', linestyle=':', linewidth=2, label=f'Eje X={symmetry_axis:.1f}')

# Límites del tramo
ax2.axhline(y_start, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax2.axhline(y_end, color='red', linestyle='--', linewidth=2, alpha=0.5)

ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_ylim(y_start - 1, y_end + 1)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.show()

# 5. Conclusión y recomendaciones
print(f"\n5️⃣ CONCLUSIÓN Y RECOMENDACIONES:")
print("="*60)

if len(cerca_eje) == 0:
    print("❌ PROBLEMA: No hay nodos de grado alto cerca del eje")
    print("\n💡 POSIBLES SOLUCIONES:")
    print(f"   1. Aumentar threshold de distancia al eje")
    print(f"      Actual: {threshold_eje:.3f}")
    print(f"      Sugerido: {threshold_eje * 3:.3f} (3x)")
    print(f"\n   2. Reducir requisito de grado mínimo")
    print(f"      Actual: grado >= 5")
    print(f"      Sugerido: grado >= 4")
    print(f"\n   3. Revisar cálculo del eje de simetría")
    print(f"      Actual: {symmetry_axis:.3f}")
    print(f"      ¿Es correcto?")
elif len(cerca_eje) < 8:
    print(f"⚠️ PROBLEMA: Solo {len(cerca_eje)} nodos cerca del eje, pero deberían ser ~8")
    print(f"\n💡 Ajustar threshold de distancia o grado mínimo")
else:
    print(f"✅ Hay {len(cerca_eje)} nodos de alto grado cerca del eje")
    print(f"   Esto es consistente con 8 módulos X")
    print(f"\n🔍 Verificar que tengan pares colineales de diagonales")

print("\n📊 Variables disponibles:")
print("   • nodos_en_tramo: Todos los nodos del tramo 1")
print("   • grados_en_tramo: Dict con nodos agrupados por grado")
print("   • nodos_alto_grado: Lista de nodos con grado >= 4")
print("   • cerca_eje: Nodos de alto grado cerca del eje")
