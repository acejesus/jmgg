# 🔧 Guía de Integración: Preprocesamiento con Grafos

## 📋 Resumen

Esta guía muestra cómo integrar el módulo de preprocesamiento con grafos en tu análisis de torres DXF para resolver los problemas identificados:

| Problema | Solución |
|----------|----------|
| ❌ Diagonales divididas en múltiples líneas | ✅ `combinacion_aristas()` las une automáticamente |
| ❌ Nodos duplicados por errores de precisión | ✅ `contraccion_dinamica_nodos()` los fusiona |
| ❌ Líneas redundantes confunden el análisis | ✅ `eliminacion_aristas_redundantes()` las elimina |
| ❌ Solo se procesan horizontales | ✅ Se procesan **todas** las líneas |

---

## 🎯 Cambios Necesarios en tu Código

### **OPCIÓN 1: Integración Automática (Recomendada)**

Agrega esta celda **ANTES** de ejecutar `main_universal_improved_analysis()`:

```python
# ================================================================================================
# NUEVA CELDA: PREPROCESAMIENTO CON GRAFOS
# ================================================================================================

import networkx as nx
import numpy as np
import math
from typing import List, Tuple

# Copiar aquí el código del archivo graph_preprocessing.py
# O importarlo si lo subes a Colab:
# from graph_preprocessing import preprocesar_lineas_dxf, integrar_preprocesamiento_en_analisis

# ... (código del módulo graph_preprocessing.py) ...

# ================================================================================================
# APLICAR PREPROCESAMIENTO A LOS DATOS CARGADOS
# ================================================================================================

# Cargar datos originales
loaded_data = load_processed_data('/content/tower_data')

if loaded_data:
    oriented_lines_original, left_contour_original, right_contour_original, sections, symmetry_axis = loaded_data

    print("🔧 APLICANDO PREPROCESAMIENTO CON GRAFOS...")
    print("="*60)

    # APLICAR PREPROCESAMIENTO
    oriented_lines, left_contour, right_contour = integrar_preprocesamiento_en_analisis(
        oriented_lines_original,
        left_contour_original,
        right_contour_original
    )

    print("\n✅ Datos preprocesados listos para análisis de módulos")

    # GUARDAR LOS DATOS PREPROCESADOS PARA USO POSTERIOR
    preprocessed_data = {
        'oriented_lines': oriented_lines,
        'left_contour': left_contour,
        'right_contour': right_contour,
        'sections': sections,
        'symmetry_axis': symmetry_axis
    }

    # Ahora estos datos limpios se usan en el análisis
```

### **OPCIÓN 2: Modificar la Función Principal**

Modifica `main_universal_improved_analysis()` para incluir preprocesamiento:

```python
def main_universal_improved_analysis():
    """Función principal con análisis universal mejorado + preprocesamiento de grafos."""
    print("🚀 ANÁLISIS UNIVERSAL MEJORADO CON PREPROCESAMIENTO DE GRAFOS")
    print("="*60)

    # Cargar datos originales
    loaded_data = load_processed_data('/content/tower_data')

    if loaded_data is None:
        print("❌ No se pudieron cargar los datos.")
        return None

    oriented_lines_original, left_contour_original, right_contour_original, sections, symmetry_axis = loaded_data

    print(f"\n📊 DATOS ORIGINALES:")
    print(f"   • Líneas: {len(oriented_lines_original)}")
    print(f"   • Secciones: {len(sections)}")
    print(f"   • Eje de simetría: X = {symmetry_axis:.3f}")

    # ===========================
    # NUEVO: PREPROCESAMIENTO
    # ===========================
    print("\n🔧 PREPROCESANDO DATOS CON GRAFOS...")

    oriented_lines, left_contour, right_contour = integrar_preprocesamiento_en_analisis(
        oriented_lines_original,
        left_contour_original,
        right_contour_original
    )

    print(f"\n✅ DATOS PREPROCESADOS:")
    print(f"   • Líneas: {len(oriented_lines)} (reducción: {len(oriented_lines_original) - len(oriented_lines)})")
    print(f"   • Contornos actualizados")

    # Continuar con el análisis normal...
    horizontal_lines, diagonal_lines = identify_module_defining_elements_improved(
        oriented_lines, left_contour, right_contour, sections, symmetry_axis, tolerance=0.05
    )

    # ... resto del código sin cambios ...
```

---

## 🧪 Ejemplo de Uso Completo

```python
# ================================================================================================
# FLUJO COMPLETO CON PREPROCESAMIENTO
# ================================================================================================

# 1. Cargar datos originales
loaded_data = load_processed_data('/content/tower_data')
oriented_lines_original, left_contour_original, right_contour_original, sections, symmetry_axis = loaded_data

# 2. Preprocesar con grafos
print("🔧 Preprocesando líneas DXF con grafos...")

oriented_lines_clean = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.01,      # 1% del tamaño del modelo
    tolerancia_angulo=2.0,       # 2 grados para considerar colinealidad
    tolerancia_longitud=0.005    # 0.5% para eliminar líneas muy cortas
)

# 3. Ver mejoras
analizar_mejoras_preprocesamiento(oriented_lines_original, oriented_lines_clean)

# 4. Continuar con el análisis normal
horizontal_lines, diagonal_lines = identify_module_defining_elements_improved(
    oriented_lines_clean,  # ← Usar líneas limpias
    left_contour,
    right_contour,
    sections,
    symmetry_axis,
    tolerance=0.05
)

# ... resto del análisis ...
```

---

## 📊 Beneficios Esperados

### **Antes del Preprocesamiento:**
```
Sección Decreciente con módulo X:
  • Diagonal 1: Línea A (segmento 1)
  • Diagonal 1: Línea B (segmento 2) ← Colineal con A
  • Diagonal 1: Línea C (segmento 3) ← Colineal con A y B
  • Resultado: detect_single_x_module_robust() ve 3 líneas separadas
  • Problema: Puede no detectar el módulo X único ❌
```

### **Después del Preprocesamiento:**
```
Sección Decreciente con módulo X:
  • Diagonal 1: Línea UNIFICADA (A+B+C combinadas)
  • Resultado: detect_single_x_module_robust() ve 1 diagonal clara
  • Éxito: Detecta correctamente el módulo X único ✅
```

---

## 🎯 Ajuste de Tolerancias

### **tolerancia_nodos (default: 0.01)**
- **Qué hace**: Une nodos que están a menos del 1% del tamaño del modelo
- **Cuándo ajustar**:
  - Aumentar a `0.02` si el DXF tiene muchos errores de precisión
  - Reducir a `0.005` si el modelo es muy preciso

### **tolerancia_angulo (default: 2.0)**
- **Qué hace**: Une líneas con ángulo menor a 2 grados entre ellas
- **Cuándo ajustar**:
  - Aumentar a `5.0` si las diagonales tienen pequeñas desviaciones
  - Reducir a `1.0` para ser más estricto

### **tolerancia_longitud (default: 0.005)**
- **Qué hace**: Elimina líneas más cortas del 0.5% del tamaño del modelo
- **Cuándo ajustar**:
  - Aumentar a `0.01` si hay muchas líneas cortas innecesarias
  - Reducir a `0.001` para ser más conservador

---

## 🔍 Validación de Resultados

Después de aplicar el preprocesamiento, verifica:

### **1. Estadísticas de Reducción**
```python
print(f"Líneas originales:  {len(oriented_lines_original)}")
print(f"Líneas procesadas:  {len(oriented_lines_clean)}")
print(f"Reducción: {((len(oriented_lines_original) - len(oriented_lines_clean)) / len(oriented_lines_original) * 100):.1f}%")
```

**Interpretación:**
- **5-15% reducción**: ✅ Bueno, había redundancias moderadas
- **15-30% reducción**: ✅ Excelente, había muchas redundancias
- **>30% reducción**: ⚠️ Verificar que no se eliminaron líneas importantes

### **2. Inspección Visual**
```python
# Comparar visualización antes/después
visualize_tower_modules_improved(
    oriented_lines_original,  # Antes
    # ... otros parámetros ...
)

visualize_tower_modules_improved(
    oriented_lines_clean,  # Después
    # ... otros parámetros ...
)
```

### **3. Comparación de Módulos Detectados**
```python
# Analizar sin preprocesamiento
sections_sin_preprocesar = analyze_modules_universal_improved(...)

# Analizar con preprocesamiento
sections_con_preprocesar = analyze_modules_universal_improved(...)

# Comparar
for i, (s1, s2) in enumerate(zip(sections_sin_preprocesar, sections_con_preprocesar)):
    print(f"Sección {i+1}:")
    print(f"  Sin preprocesar:  {s1['num_modulos']} módulos [{s1['metodo_deteccion']}]")
    print(f"  Con preprocesar:  {s2['num_modulos']} módulos [{s2['metodo_deteccion']}]")
    if s1['num_modulos'] != s2['num_modulos']:
        print(f"  ⚠️ Diferencia detectada!")
```

---

## 🐛 Troubleshooting

### **Problema: Reducción > 50%**
**Causa**: Tolerancias demasiado agresivas
**Solución**:
```python
oriented_lines_clean = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.005,     # ← Reducir
    tolerancia_angulo=1.0,       # ← Reducir
    tolerancia_longitud=0.001    # ← Reducir
)
```

### **Problema: No se detectan mejoras (reducción < 2%)**
**Causa**: Tolerancias demasiado conservadoras o DXF ya limpio
**Solución**:
- Si el DXF tiene errores conocidos, aumentar tolerancias
- Si el DXF ya está limpio, el preprocesamiento es opcional

### **Problema: detect_single_x_module_robust() sigue fallando**
**Causa**: La lógica de detección necesita ajustes adicionales
**Solución**:
```python
# Modificar detect_single_x_module_robust para considerar líneas unificadas
def detect_single_x_module_robust(section_diagonals, symmetry_axis, section_bounds, tolerance=0.05):
    # Añadir logging para diagnóstico
    print(f"        🔍 Analizando {len(section_diagonals)} diagonales")
    for i, diagonal in enumerate(section_diagonals):
        x1, y1, z1, x2, y2, z2 = diagonal
        longitud = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        print(f"        📏 Diagonal {i+1}: longitud={longitud:.3f}, Y=[{min(y1,y2):.3f}-{max(y1,y2):.3f}]")

    # ... resto del código ...
```

---

## 🚀 Siguiente Paso Recomendado

1. **Integrar el preprocesamiento** usando la OPCIÓN 1 (más simple)
2. **Ejecutar el análisis completo** y comparar resultados
3. **Ajustar tolerancias** si es necesario
4. **Validar visualmente** que los módulos detectados son correctos

---

## 📞 Preguntas Frecuentes

**P: ¿El preprocesamiento afecta las coordenadas originales?**
R: Sí, ajusta coordenadas de nodos cercanos al centroide. Esto es **intencional** para corregir errores de precisión.

**P: ¿Puedo aplicarlo solo a las diagonales?**
R: Sí, pero se recomienda aplicarlo a todas las líneas para consistencia.

**P: ¿Cuánto tiempo tarda?**
R: Para modelos típicos (1000-5000 líneas): 1-5 segundos.

**P: ¿Qué pasa si tengo un modelo 2D?**
R: El código maneja automáticamente modelos 2D agregando z=0.

---

## 📝 Resumen

✅ **Beneficio principal**: Diagonales divididas se unifican → Mejor detección de módulos X
✅ **Fácil de integrar**: Solo agregar una celda antes del análisis
✅ **Ajustable**: Tres tolerancias para afinar el comportamiento
✅ **Seguro**: Mantiene conectividad del grafo y no elimina elementos estructurales

**🎯 Recomendación**: Integrar inmediatamente y comparar resultados antes/después.
