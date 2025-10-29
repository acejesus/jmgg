# 🎨 Visualización de Grafos - Inicio Rápido

## 📋 ¿Qué es esto?

Visualizaciones gráficas interactivas del proceso de preprocesamiento de grafos para análisis de torres DXF.

---

## 🚀 Uso en 2 Pasos

### **Paso 1: Agregar Celda de Visualización**

Copia el contenido de **`celda_visualizacion_grafos.py`** como una nueva celda en Colab **DESPUÉS** de la celda de preprocesamiento.

### **Paso 2: Ejecutar**

```python
# Ejecuta la celda
# Se generarán automáticamente 4 visualizaciones
```

---

## 🎨 4 Visualizaciones Generadas

### **1. Comparación Antes/Después**
- Vista lado a lado del grafo original vs procesado
- Muestra reducción de nodos y aristas
- **Color:** 🔴 Antes (rojo) → 🟢 Después (verde)

### **2. Proceso Completo Paso a Paso**
- 4 paneles mostrando cada etapa:
  - Paso 0: Grafo original (gris)
  - Paso 1: Contracción de nodos (rojo)
  - Paso 2: Combinación de colineales (amarillo)
  - Paso 3: Eliminación de redundantes (verde)

### **3. Estadísticas Detalladas**
- Grafo coloreado por grado de nodos
- Distribución de grados (histograma)
- Distribución de longitudes de aristas

### **4. Zoom en Área Central**
- Vista completa + área ampliada
- Nodos numerados para inspección detallada
- Verificación de fusión y limpieza local

---

## 🔍 ¿Qué Buscar?

### **Indicadores de Buena Limpieza:**

✅ **Reducción de nodos:** > 20%
✅ **Reducción de aristas:** > 15%
✅ **Grafo "después" menos denso visualmente**
✅ **Pocas aristas muy cortas en el histograma**

### **Indicadores de Problemas:**

⚠️ **Reducción < 5%:** Tolerancias muy conservadoras
⚠️ **Reducción > 50%:** Tolerancias muy agresivas
⚠️ **Nodos aún muy cercanos en zoom:** Aumentar `tolerancia_nodos`
⚠️ **Líneas quebradas en zoom:** Aumentar `tolerancia_angulo`

---

## 📊 Interpretación Rápida

### **Visualización 1 (Comparación):**
```
Antes:  🔴 1245 nodos, 1523 aristas
Después: 🟢 891 nodos, 1102 aristas
         ✅ -28.4% nodos, -27.6% aristas
```
**Interpretación:** ✅ Mejora significativa, preprocesamiento exitoso

### **Visualización 2 (Proceso):**
```
Paso 0→1: -127 nodos    (fusión de duplicados)
Paso 1→2: -89 nodos     (unión de colineales) ← IMPORTANTE
Paso 2→3: -45 aristas   (eliminación de cortas)
```
**Interpretación:** ✅ Paso 2 muestra unificación de diagonales divididas

### **Visualización 3 (Estadísticas):**
```
Grado 2: 70% de nodos   ← Mayoría (nodos de paso)
Grado 3-4: 20%          ← Intersecciones
Grado 5+: 10%           ← Cruces complejos
```
**Interpretación:** ✅ Distribución saludable para estructura de torre

### **Visualización 4 (Zoom):**
```
En área central:
  • Nodos bien espaciados
  • Líneas continuas (no quebradas)
  • Sin segmentos muy cortos
```
**Interpretación:** ✅ Limpieza local correcta

---

## 🔧 Ajustes Según Visualización

### **Si el grafo sigue "ruidoso":**
```python
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.02,       # ← Aumentar
    tolerancia_angulo=3.0,        # ← Aumentar
    tolerancia_longitud=0.01      # ← Aumentar
)
```

### **Si hay reducción excesiva (>50%):**
```python
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.005,      # ← Reducir
    tolerancia_angulo=1.0,        # ← Reducir
    tolerancia_longitud=0.001     # ← Reducir
)
```

---

## 💡 Funciones Disponibles

Además de la ejecución automática, puedes usar manualmente:

```python
# Crear grafo desde líneas
G = crear_grafo_desde_lineas(oriented_lines)

# Visualización básica
visualizar_grafo_basico(G, titulo="Mi Grafo")

# Comparación personalizada
visualizar_grafo_comparativo(G_antes, G_despues)

# Estadísticas detalladas
visualizar_grafo_con_estadisticas(G, titulo="Análisis Completo")

# Zoom en área específica
visualizar_zoom_area(G, x_center=10.0, y_center=20.0, radio=5.0)

# Proceso completo
visualizar_proceso_limpieza_completo(lineas_original)
```

---

## 📚 Documentación Completa

Para interpretación detallada, consulta:
- **`GUIA_VISUALIZACION_GRAFOS.md`** - Guía completa de interpretación
- **`celda_visualizacion_grafos.py`** - Código fuente documentado

---

## ✅ Checklist de Validación

Después de ejecutar las visualizaciones:

- [ ] Visualización 1: Hay reducción visible (> 15%)
- [ ] Visualización 2: Paso 1→2 muestra unificación de líneas
- [ ] Visualización 3: Distribución de grados es saludable
- [ ] Visualización 4: No hay nodos duplicados ni líneas quebradas
- [ ] Las mejoras son coherentes con las expectativas

Si todos los puntos están marcados: ✅ **Procede con el análisis de módulos**

---

## 🎯 Ejemplo de Salida Esperada

```
🎨 MÓDULO DE VISUALIZACIÓN DE GRAFOS
============================================================

📊 Visualización 1: Comparación Antes/Después
------------------------------------------------------------
[Gráfico comparativo generado]

📊 Visualización 2: Proceso Completo de Limpieza
------------------------------------------------------------
(Mostrando cada paso del preprocesamiento...)
[4 paneles con progreso del preprocesamiento]

📊 Visualización 3: Estadísticas Detalladas del Grafo Final
------------------------------------------------------------
[Grafo con estadísticas + histogramas]

📊 Visualización 4: Zoom en Área Central
------------------------------------------------------------
Centro: (15.23, 42.67), Radio: 3.45
[Vista completa + zoom detallado]

============================================================
✅ VISUALIZACIONES COMPLETADAS
============================================================

📋 RESUMEN DE VISUALIZACIONES:
   1. ✅ Comparación antes/después del preprocesamiento
   2. ✅ Proceso completo paso a paso (4 etapas)
   3. ✅ Estadísticas detalladas del grafo final
   4. ✅ Zoom en área central del modelo

📊 MEJORAS CUANTIFICADAS:
   • Reducción de nodos:   354 (28.4%)
   • Reducción de aristas: 421 (27.6%)
   ✅ ¡Mejora significativa! El grafo fue optimizado considerablemente.
```

---

## 🚀 Próximos Pasos

1. ✅ Ejecuta la celda de visualización
2. ✅ Revisa las 4 visualizaciones generadas
3. ✅ Verifica que la limpieza es adecuada
4. ✅ Ajusta tolerancias si es necesario (re-ejecuta preprocesamiento + visualización)
5. ✅ Una vez satisfecho, procede con el análisis de módulos

---

**🎨 ¡Listo para visualizar tus grafos!**

Las visualizaciones te ayudarán a entender exactamente qué hizo el preprocesamiento y a validar que las diagonales divididas fueron correctamente unificadas.

**Tiempo de ejecución:** ~10-15 segundos para generar las 4 visualizaciones
**Beneficio:** Validación visual completa del preprocesamiento 📊
