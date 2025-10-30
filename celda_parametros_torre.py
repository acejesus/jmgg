# ================================================================================================
# GENERACIÓN DE PARÁMETROS DE TORRE DESDE ANÁLISIS DE GRAFOS
# ================================================================================================
# Esta celda genera el archivo Excel con parámetros de torre para Revit/Dynamo
# Usa los datos generados por la celda de análisis con grafos
# ================================================================================================

import pandas as pd
import numpy as np

def calcular_anchos_por_seccion(oriented_lines, sections):
    """
    Calcula el ancho de la torre (max X - min X) en el inicio y fin de cada sección.

    Args:
        oriented_lines: Lista de líneas (x1, y1, z1, x2, y2, z2)
        sections: Lista de secciones con altura_inicio, altura_fin

    Returns:
        DataFrame con Tramo, Ancho_Base, Ancho_Top
    """
    anchos_data = []

    for i, section in enumerate(sections, 1):
        y_inicio = section['altura_inicio']
        y_fin = section['altura_fin']

        # Buscar puntos cerca del inicio de la sección (±0.1m)
        tolerance = 0.1
        x_coords_inicio = []
        x_coords_fin = []

        for line in oriented_lines:
            x1, y1, z1, x2, y2, z2 = line

            # Puntos cerca del inicio
            if abs(y1 - y_inicio) < tolerance:
                x_coords_inicio.append(x1)
            if abs(y2 - y_inicio) < tolerance:
                x_coords_inicio.append(x2)

            # Puntos cerca del fin
            if abs(y1 - y_fin) < tolerance:
                x_coords_fin.append(x1)
            if abs(y2 - y_fin) < tolerance:
                x_coords_fin.append(x2)

        # Calcular anchos
        if x_coords_inicio:
            ancho_base = max(x_coords_inicio) - min(x_coords_inicio)
        else:
            ancho_base = 0.0

        if x_coords_fin:
            ancho_top = max(x_coords_fin) - min(x_coords_fin)
        else:
            ancho_top = 0.0

        anchos_data.append({
            'Tramo': i,
            'Ancho_Base': round(ancho_base, 3),
            'Ancho_Top': round(ancho_top, 3)
        })

    return pd.DataFrame(anchos_data)


def generar_tabla_modulos(sections_con_modulos):
    """
    Genera una tabla detallada de módulos similar a modulos_torre_universal.csv

    Args:
        sections_con_modulos: Lista de secciones con módulos detectados

    Returns:
        DataFrame con detalles de cada módulo
    """
    modulos_data = []

    for i, section in enumerate(sections_con_modulos, 1):
        num_modulos = section['num_modulos']
        alturas = section['limites_modulos']
        tipo = section['tipo']
        altura_tramo = section['altura_tramo']
        y_inicio = section['altura_inicio']
        y_fin = section['altura_fin']
        metodo = 'diagonales' if section.get('tiene_modulo_x', False) else 'horizontales'

        for j in range(num_modulos):
            altura_modulo = section['alturas_modulos'][j]
            y_inicio_modulo = alturas[j]
            y_fin_modulo = alturas[j + 1]

            modulos_data.append({
                'Tramo': i,
                'Tipo': tipo,
                'Altura_Tramo': altura_tramo,
                'Y_Inicio': y_inicio,
                'Y_Fin': y_fin,
                'Num_Modulos': num_modulos,
                'Metodo_Deteccion': metodo,
                'Modulo': j + 1,
                'Altura_Modulo': altura_modulo,
                'Y_Inicio_Modulo': y_inicio_modulo,
                'Y_Fin_Modulo': y_fin_modulo
            })

    return pd.DataFrame(modulos_data)


def generate_tower_parameters_from_analysis(sections_con_modulos, oriented_lines):
    """
    Genera parámetros de torre desde el análisis de grafos.

    Args:
        sections_con_modulos: Lista de secciones con módulos detectados (de celda anterior)
        oriented_lines: Lista de líneas orientadas

    Returns:
        df_params: DataFrame con parámetros
        df_tramos: DataFrame con resumen de tramos
    """
    print("="*60)
    print("📊 GENERANDO PARÁMETROS DE TORRE")
    print("="*60)

    # 1. Crear DataFrame de módulos (para referencia, equivalente a modulos_torre_universal.csv)
    print("\n1️⃣ Generando tabla de módulos...")
    df_modulos = generar_tabla_modulos(sections_con_modulos)
    print(f"   ✅ {len(df_modulos)} módulos procesados")

    # Guardar para referencia
    df_modulos.to_csv('modulos_torre_generados.csv', index=False)
    print(f"   💾 Guardado en 'modulos_torre_generados.csv'")

    # 2. Calcular anchos por sección
    print("\n2️⃣ Calculando anchos de secciones...")
    df_anchos = calcular_anchos_por_seccion(oriented_lines, sections_con_modulos)
    print(f"   ✅ Anchos calculados para {len(df_anchos)} secciones")

    # 3. Crear DataFrame de tramos combinando toda la información
    print("\n3️⃣ Combinando datos de secciones...")
    df_tramos_data = []

    for i, section in enumerate(sections_con_modulos, 1):
        ancho_info = df_anchos[df_anchos['Tramo'] == i].iloc[0]

        df_tramos_data.append({
            'Tramo': i,
            'Tipo': section['tipo'],
            'Altura_Tramo': section['altura_tramo'],
            'Y_Inicio': section['altura_inicio'],
            'Y_Fin': section['altura_fin'],
            'Ancho_Base': ancho_info['Ancho_Base'],
            'Ancho_Top': ancho_info['Ancho_Top'],
            'Num_Modulos': section['num_modulos'],
            'Metodo_Deteccion': section['metodo_deteccion']
        })

    df_tramos = pd.DataFrame(df_tramos_data)

    # Guardar para referencia
    df_tramos.to_csv('secciones_torre_generadas.csv', index=False)
    print(f"   💾 Guardado en 'secciones_torre_generadas.csv'")

    # 4. Generar tabla de parámetros
    print("\n4️⃣ Generando parámetros...")
    parametros = [{"Parámetro": "Número de Secciones", "Valor": len(df_tramos)}]

    for _, tramo in df_tramos.iterrows():
        tramo_idx = int(tramo["Tramo"])
        parametros.append({"Parámetro": f"CNX_S{tramo_idx}BaseWidth", "Valor": round(tramo["Ancho_Base"], 1)})
        parametros.append({"Parámetro": f"CNX_S{tramo_idx}TopWidth",  "Valor": round(tramo["Ancho_Top"], 1)})
        parametros.append({"Parámetro": f"CNX_S{tramo_idx}Height",    "Valor": round(tramo["Altura_Tramo"], 1)})

    df_parametros = pd.DataFrame(parametros)

    # 5. Añadir número de módulos
    print("5️⃣ Añadiendo número de módulos por sección...")
    new_rows = []
    for _, tramo in df_tramos.iterrows():
        tramo_idx = int(tramo["Tramo"])
        param_name = f"CNX_S{tramo_idx}NModules"
        param_val = int(tramo["Num_Modulos"])
        new_rows.append({"Parámetro": param_name, "Valor": param_val})

    # 6. Parámetros calculados
    print("6️⃣ Calculando parámetros adicionales...")
    tower_height = df_tramos["Y_Fin"].max()
    new_rows.append({"Parámetro": "CNX_Height", "Valor": round(tower_height, 1)})

    n_secciones = len(df_tramos)
    s1_base_width = df_tramos.loc[df_tramos['Tramo']==1, 'Ancho_Base'].iloc[0] if not df_tramos.loc[df_tramos['Tramo']==1].empty else None
    s2_base_width = df_tramos.loc[df_tramos['Tramo']==2, 'Ancho_Base'].iloc[0] if not df_tramos.loc[df_tramos['Tramo']==2].empty else None

    leg_foundation_value = bool(s1_base_width is not None and s2_base_width is not None and s1_base_width > s2_base_width)
    buried_module_value = 2 if (s1_base_width is not None and s2_base_width is not None and s1_base_width == s2_base_width) else 0

    additional_params = []
    if s1_base_width is not None:
        additional_params.append({"Parámetro": "CNX_S1BaseDepth", "Valor": round(s1_base_width, 1)})
    if s2_base_width is not None:
        additional_params.append({"Parámetro": "CNX_S2BaseDepth", "Valor": round(s2_base_width, 1)})
    additional_params.append({"Parámetro": "CNX_BuriedModule", "Valor": buried_module_value})

    foundation_width = s1_base_width if s1_base_width is not None else 0
    foundation_params = [
        {"Parámetro": "CNX_LegFoundation",           "Valor": leg_foundation_value},
        {"Parámetro": "CNX_FoundationTopFaceHeight", "Valor": 0.1},
        {"Parámetro": "CNX_FoundationWidth",         "Valor": round(foundation_width, 1)},
        {"Parámetro": "CNX_LegFoundationWidth",      "Valor": 1},
        {"Parámetro": "CNX_LegFoundationOffset",     "Valor": 0},
    ]

    # 7. Combinar todos los parámetros
    df_params = pd.concat([
        df_parametros,
        pd.DataFrame(new_rows),
        pd.DataFrame(foundation_params),
        pd.DataFrame(additional_params)
    ], ignore_index=True)

    # 8. Redondear valores numéricos
    for col in df_params.columns:
        mask = df_params[col].apply(lambda x: isinstance(x, (float, np.float64)))
        df_params.loc[mask, col] = df_params.loc[mask, col].round(1)

    # 9. Escribir archivo Excel
    print("\n7️⃣ Generando archivo Excel...")
    output_excel = f"PARAMETROS_FAMILIA_TORRE_{n_secciones}S.xlsx"

    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_params.to_excel(writer, sheet_name="Hoja1", index=False)

    print(f"   ✅ Excel '{output_excel}' generado correctamente")

    # 10. Mostrar resumen
    print("\n" + "="*60)
    print("📋 RESUMEN DE PARÁMETROS GENERADOS")
    print("="*60)
    print(f"\n🏗️ TORRE:")
    print(f"   • Altura total: {tower_height:.1f} m")
    print(f"   • Número de secciones: {n_secciones}")
    print(f"   • Total de módulos: {df_tramos['Num_Modulos'].sum()}")

    print(f"\n📊 SECCIONES:")
    for _, tramo in df_tramos.iterrows():
        idx = int(tramo['Tramo'])
        tipo = tramo['Tipo']
        h = tramo['Altura_Tramo']
        w_base = tramo['Ancho_Base']
        w_top = tramo['Ancho_Top']
        n_mod = int(tramo['Num_Modulos'])
        metodo = tramo['Metodo_Deteccion']

        print(f"   Sección {idx} ({tipo}): h={h:.1f}m, W_base={w_base:.1f}m, W_top={w_top:.1f}m, {n_mod} módulos [{metodo}]")

    print("\n" + "="*60)
    print("✅ PARÁMETROS DE TORRE GENERADOS CORRECTAMENTE")
    print("="*60)

    print("\n📄 Archivos generados:")
    print(f"   1. {output_excel} - Parámetros para Revit/Dynamo")
    print(f"   2. modulos_torre_generados.csv - Detalle de módulos")
    print(f"   3. secciones_torre_generadas.csv - Resumen de secciones")

    return df_params, df_tramos, df_modulos


# ================================================================================================
# EJECUTAR GENERACIÓN DE PARÁMETROS
# ================================================================================================

print("🚀 GENERANDO PARÁMETROS DE TORRE...")
print("   (usando datos de: sections_con_modulos y oriented_lines)")

# Verificar que las variables existen
try:
    # Estas variables fueron creadas por la celda anterior (celda_grafo_corregida_final.py)
    if 'sections_con_modulos' not in locals() and 'sections_con_modulos' not in globals():
        raise NameError("Variable 'sections_con_modulos' no encontrada")
    if 'oriented_lines' not in locals() and 'oriented_lines' not in globals():
        raise NameError("Variable 'oriented_lines' no encontrada")

    # Generar parámetros
    df_params, df_tramos, df_modulos = generate_tower_parameters_from_analysis(
        sections_con_modulos,
        oriented_lines
    )

    # Mostrar todos los parámetros
    print("\n" + "="*60)
    print("📋 LISTA COMPLETA DE PARÁMETROS")
    print("="*60)
    for _, row in df_params.iterrows():
        valor = row['Valor']
        if isinstance(valor, bool):
            valor_str = 'True' if valor else 'False'
        elif isinstance(valor, (int, float)):
            valor_str = f"{valor:.1f}" if isinstance(valor, float) else str(valor)
        else:
            valor_str = str(valor)
        print(f"   {row['Parámetro']:<35} = {valor_str}")

    print("\n✅ Variables disponibles:")
    print("   • df_params  - DataFrame con todos los parámetros")
    print("   • df_tramos  - DataFrame con resumen de secciones")
    print("   • df_modulos - DataFrame con detalle de módulos")

except NameError as e:
    print(f"\n❌ ERROR: {e}")
    print("\n⚠️ Esta celda debe ejecutarse DESPUÉS de la celda de análisis con grafos")
    print("   Asegúrate de haber ejecutado 'celda_grafo_corregida_final.py' primero")
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()
