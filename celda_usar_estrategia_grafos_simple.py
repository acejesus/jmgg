# ================================================================================================
# CELDA SIMPLE: USAR ESTRATEGIA DE GRAFOS - LISTA PARA COLAB
# ================================================================================================
# INSTRUCCIONES:
# 1. Sube el archivo "graph_module_detection.py" a Colab (arrastra y suelta en Files)
# 2. Copia esta celda en tu notebook
# 3. Ejecuta para analizar módulos con la nueva estrategia
# ================================================================================================

import pandas as pd
import os
import networkx as nx

# ================================================================================================
# IMPORTAR EL MÓDULO DE DETECCIÓN CON GRAFOS
# ================================================================================================

print("🔧 CARGANDO MÓDULO DE DETECCIÓN CON GRAFOS...")

try:
    # Importar todas las funciones del módulo
    from graph_module_detection import (
        crear_grafo_desde_lineas,
        analizar_todas_secciones_con_grafo,
        analizar_seccion_con_grafo,
        detectar_modulos_x_por_nodos,
        reconstruir_diagonales_completas,
        filtrar_horizontales_divididas
    )
    print("✅ Módulo cargado correctamente")
except ImportError as e:
    print(f"❌ Error al importar módulo: {e}")
    print("\n💡 SOLUCIÓN:")
    print("   1. Asegúrate de haber subido 'graph_module_detection.py' a Colab")
    print("   2. En el panel izquierdo, arrastra el archivo .py y suéltalo")
    print("   3. Re-ejecuta esta celda")
    raise

# ================================================================================================
# CARGAR DATOS DESDE CSV
# ================================================================================================

print("\n📁 CARGANDO DATOS DESDE CSV...")

data_folder = '/content/tower_data'

# Verificar que la carpeta existe
if not os.path.exists(data_folder):
    print(f"❌ Carpeta {data_folder} no encontrada")
    print("💡 Asegúrate de haber ejecutado las celdas de preprocesamiento primero")
    raise FileNotFoundError(f"Carpeta {data_folder} no encontrada")

# Cargar oriented_lines
oriented_lines_csv = os.path.join(data_folder, 'oriented_lines.csv')
if not os.path.exists(oriented_lines_csv):
    print(f"❌ Archivo {oriented_lines_csv} no encontrado")
    raise FileNotFoundError(f"Archivo {oriented_lines_csv} no encontrado")

df_lines = pd.read_csv(oriented_lines_csv)
oriented_lines = [(row['x1'], row['y1'], row['z1'], row['x2'], row['y2'], row['z2'])
                  for _, row in df_lines.iterrows()]

print(f"✅ Líneas cargadas: {len(oriented_lines)}")

# Cargar sections
sections_csv = os.path.join(data_folder, 'sections.csv')
if not os.path.exists(sections_csv):
    print(f"❌ Archivo {sections_csv} no encontrado")
    raise FileNotFoundError(f"Archivo {sections_csv} no encontrado")

df_sections = pd.read_csv(sections_csv)

# Convertir DataFrame de sections a lista de diccionarios
sections = []
for _, row in df_sections.iterrows():
    sections.append({
        'altura_inicio': row['altura_inicio'],
        'altura_fin': row['altura_fin'],
        'altura_tramo': row['altura_tramo'],
        'tipo': row['tipo']
    })

print(f"✅ Secciones cargadas: {len(sections)}")

# Obtener symmetry_axis
try:
    symmetry_axis_file = os.path.join(data_folder, 'symmetry_axis.txt')
    if os.path.exists(symmetry_axis_file):
        with open(symmetry_axis_file, 'r') as f:
            symmetry_axis = float(f.read().strip())
        print(f"✅ Eje de simetría cargado: {symmetry_axis:.3f}")
    else:
        # Calcular como punto medio del ancho del modelo
        all_x = [line[0] for line in oriented_lines] + [line[3] for line in oriented_lines]
        symmetry_axis = (min(all_x) + max(all_x)) / 2
        print(f"✅ Eje de simetría calculado: {symmetry_axis:.3f}")
except Exception as e:
    print(f"⚠️ No se pudo determinar eje de simetría: {e}")
    symmetry_axis = 0.0
    print(f"   Usando valor por defecto: {symmetry_axis}")

# ================================================================================================
# CREAR GRAFO DESDE LÍNEAS
# ================================================================================================

print("\n🔧 CREANDO GRAFO DESDE LÍNEAS...")

G = crear_grafo_desde_lineas(oriented_lines)

print(f"✅ Grafo creado:")
print(f"   • Nodos: {G.number_of_nodes()}")
print(f"   • Aristas: {G.number_of_edges()}")

# Mostrar distribución de grados
degrees = dict(G.degree())
degree_counts = {}
for node, degree in degrees.items():
    degree_counts[degree] = degree_counts.get(degree, 0) + 1

print(f"\n📊 Distribución de grados:")
for degree in sorted(degree_counts.keys())[:6]:  # Mostrar solo primeros 6
    count = degree_counts[degree]
    percentage = (count / len(degrees)) * 100
    print(f"   Grado {degree}: {count:3d} nodos ({percentage:5.1f}%)")

# ================================================================================================
# ANALIZAR TODAS LAS SECCIONES CON ESTRATEGIA DE GRAFOS
# ================================================================================================

print("\n" + "="*60)
print("🚀 INICIANDO ANÁLISIS CON ESTRATEGIA DE GRAFOS")
print("="*60)

sections_con_modulos = analizar_todas_secciones_con_grafo(
    G,
    sections,
    symmetry_axis,
    tolerance=0.05
)

# ================================================================================================
# GUARDAR RESULTADOS
# ================================================================================================

print("\n💾 GUARDANDO RESULTADOS...")

# Crear DataFrame con resultados
resultados = []

for i, section in enumerate(sections_con_modulos):
    limites = section.get('limites_modulos', [])
    alturas_modulos = section.get('alturas_modulos', [])

    for j, altura_modulo in enumerate(alturas_modulos):
        resultados.append({
            'Tramo': i + 1,
            'Tipo': section['tipo'],
            'Altura_Tramo': section['altura_tramo'],
            'Y_Inicio_Tramo': section['altura_inicio'],
            'Y_Fin_Tramo': section['altura_fin'],
            'Num_Modulos': section['num_modulos'],
            'Metodo_Deteccion': section['metodo_deteccion'],
            'Tiene_Modulo_X': section.get('tiene_modulo_x', False),
            'Modulo': j + 1,
            'Altura_Modulo': altura_modulo,
            'Y_Inicio_Modulo': limites[j] if j < len(limites) else None,
            'Y_Fin_Modulo': limites[j+1] if j+1 < len(limites) else None
        })

df_resultados = pd.DataFrame(resultados)

# Guardar a CSV
output_csv = os.path.join(data_folder, 'modulos_con_grafo.csv')
df_resultados.to_csv(output_csv, index=False)

print(f"✅ Resultados guardados en: {output_csv}")

# ================================================================================================
# MOSTRAR RESUMEN FINAL
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

    # Mostrar detalle de módulos si son pocos
    if num_mod <= 5:
        alturas = section.get('alturas_modulos', [])
        limites = section.get('limites_modulos', [])
        for j, h in enumerate(alturas):
            y_ini = limites[j] if j < len(limites) else '?'
            y_fin = limites[j+1] if j+1 < len(limites) else '?'
            prefix = "D" if 'diagonal' in metodo else "H"
            print(f"      {prefix}{j+1}: h={h:.3f}, Y=[{y_ini:.3f}-{y_fin:.3f}]")

# ================================================================================================
# COMPARACIÓN CON MÉTODO ANTERIOR (si existe)
# ================================================================================================

print("\n" + "="*60)
print("📊 COMPARACIÓN CON MÉTODO ANTERIOR")
print("="*60)

try:
    old_results_csv = os.path.join(data_folder, 'modulos_torre_universal.csv')

    if os.path.exists(old_results_csv):
        df_old = pd.read_csv(old_results_csv)

        # Agrupar por tramo
        old_modules_count = df_old.groupby('Tramo')['Modulo'].max().tolist()
        new_modules_count = [s['num_modulos'] for s in sections_con_modulos]

        print(f"\n{'Sección':<12} {'Anterior':<10} {'Grafos':<10} {'Diferencia':<12}")
        print("-" * 50)

        total_old = 0
        total_new = 0

        for i in range(len(sections_con_modulos)):
            old_count = old_modules_count[i] if i < len(old_modules_count) else 0
            new_count = new_modules_count[i]
            diff = new_count - old_count

            total_old += old_count
            total_new += new_count

            if diff > 0:
                symbol = "📈"
            elif diff < 0:
                symbol = "📉"
            else:
                symbol = "➡️"

            tipo = sections_con_modulos[i]['tipo']
            print(f"{tipo:<12} {old_count:<10} {new_count:<10} {symbol} {diff:+d}")

        print("-" * 50)
        print(f"{'TOTAL':<12} {total_old:<10} {total_new:<10} {total_new - total_old:+d}")

        print("\n💡 Interpretación:")
        if total_new > total_old:
            print(f"   ✅ La estrategia de grafos detectó {total_new - total_old} módulos MÁS")
            print("      (Mejor granularidad o detección de módulos antes perdidos)")
        elif total_new < total_old:
            print(f"   📉 La estrategia de grafos detectó {total_old - total_new} módulos MENOS")
            print("      (Mejor consolidación o filtrado de horizontales divididas)")
        else:
            print("   ➡️ Ambos métodos detectaron la misma cantidad total de módulos")
            print("      (Revisa el detalle por sección para ver diferencias)")

    else:
        print("ℹ️ No se encontró archivo de resultados anteriores")
        print(f"   Buscado en: {old_results_csv}")
        print("   Ejecuta el análisis anterior primero para comparar")

except Exception as e:
    print(f"⚠️ No se pudo comparar con método anterior: {e}")

# ================================================================================================
# VARIABLES DISPONIBLES
# ================================================================================================

print("\n" + "="*60)
print("✅ ANÁLISIS COMPLETADO")
print("="*60)

print(f"\n🎯 Variables disponibles:")
print(f"   • G: Grafo de NetworkX ({G.number_of_nodes()} nodos, {G.number_of_edges()} aristas)")
print(f"   • sections_con_modulos: Lista con {len(sections_con_modulos)} secciones analizadas")
print(f"   • df_resultados: DataFrame de pandas con {len(df_resultados)} filas")
print(f"   • oriented_lines: {len(oriented_lines)} líneas originales")

print(f"\n📁 Archivos generados:")
print(f"   • {output_csv}")

print(f"\n💡 Próximos pasos:")
print(f"   1. Revisar df_resultados para ver detalles")
print(f"   2. Comparar con análisis anterior")
print(f"   3. Visualizar si es necesario")
print(f"   4. Ajustar tolerancias si los resultados no son correctos")

# ================================================================================================
# FIN DE LA CELDA
# ================================================================================================
