# 🎨 Guía de Visualización de Grafos

## 📋 Resumen

Esta guía explica cómo interpretar las visualizaciones de grafos generadas por `celda_visualizacion_grafos.py` y qué buscar en cada una.

---

## 🎯 4 Visualizaciones Principales

### **1️⃣ Comparación Antes/Después**

**Qué muestra:**
- Lado izquierdo (ROJO): Grafo antes del preprocesamiento
- Lado derecho (VERDE): Grafo después del preprocesamiento

**Qué buscar:**

| Elemento | Significado | Interpretación |
|----------|------------|----------------|
| **Densidad de nodos** | Cantidad de puntos en el grafo | Menos nodos = mejor limpieza |
| **Cluster de nodos** | Grupos de nodos muy cercanos | Antes: muchos clusters → Después: unificados |
| **Longitud de aristas** | Tamaño de las líneas | Antes: muchas cortas → Después: más largas (unificadas) |
| **Reducción numérica** | Texto en esquinas | Mayor reducción = mayor mejora |

**Interpretación:**

```
✅ BUENA LIMPIEZA:
   • Reducción de nodos: > 20%
   • Reducción de aristas: > 15%
   • Visualmente menos "ruidoso"

⚠️ LIMPIEZA MODERADA:
   • Reducción de nodos: 5-20%
   • Reducción de aristas: 5-15%
   • Algunas mejoras visibles

ℹ️ LIMPIEZA MÍNIMA:
   • Reducción de nodos: < 5%
   • Reducción de aristas: < 5%
   • Modelo ya estaba limpio
```

---

### **2️⃣ Proceso Completo Paso a Paso**

**Qué muestra:**
- **Paso 0 (GRIS)**: Grafo original sin procesar
- **Paso 1 (ROJO)**: Después de contracción de nodos
- **Paso 2 (AMARILLO)**: Después de combinar líneas colineales
- **Paso 3 (VERDE)**: Después de eliminar redundantes

**Qué buscar en cada paso:**

#### **Paso 0 → Paso 1: Contracción de Nodos**

```
¿Qué cambió?
   • Reducción de nodos (principalmente)
   • Las aristas se mantienen o reducen ligeramente

¿Qué significa?
   • Nodos cercanos fueron fusionados
   • Errores de precisión DXF corregidos

Ejemplo visual:
   ANTES:  ● ● ●  (3 nodos muy cercanos)
   DESPUÉS:  ●     (1 nodo en el centroide)
```

**Indicadores:**
- ✅ Reducción > 10% de nodos: Muchos errores de precisión corregidos
- ⚠️ Reducción 5-10%: Algunos errores corregidos
- ℹ️ Reducción < 5%: Modelo tenía buena precisión

#### **Paso 1 → Paso 2: Combinación de Líneas Colineales**

```
¿Qué cambió?
   • Reducción significativa de nodos
   • Reducción significativa de aristas

¿Qué significa?
   • Líneas divididas fueron unificadas
   • Nodos intermedios eliminados

Ejemplo visual:
   ANTES:  ●───●───●  (2 aristas, 3 nodos)
   DESPUÉS: ●──────●  (1 arista, 2 nodos)
```

**Indicadores:**
- ✅ Reducción > 20% de aristas: Muchas líneas fragmentadas unificadas
- ⚠️ Reducción 10-20%: Algunas líneas unificadas
- ℹ️ Reducción < 10%: Pocas líneas fragmentadas

**🎯 ESTO ES LO MÁS IMPORTANTE:** Este paso es el que resuelve el problema de diagonales divididas en módulos X.

#### **Paso 2 → Paso 3: Eliminación de Redundantes**

```
¿Qué cambió?
   • Reducción de aristas (principalmente)
   • Reducción de nodos aislados

¿Qué significa?
   • Líneas muy cortas eliminadas
   • Ruido en el modelo reducido

Ejemplo visual:
   ANTES:  ●───────●─●  (línea larga + línea corta)
   DESPUÉS: ●───────●    (solo línea estructural)
```

**Indicadores:**
- ✅ Reducción > 5% de aristas: Había líneas cortas innecesarias
- ⚠️ Reducción 2-5%: Algunas líneas cortas eliminadas
- ℹ️ Reducción < 2%: Modelo no tenía líneas redundantes

---

### **3️⃣ Estadísticas Detalladas**

**Qué muestra:**
- **Gráfico principal (izquierda)**: Grafo coloreado por grado de nodos
- **Gráfico superior derecho**: Distribución de grados
- **Gráfico inferior derecho**: Distribución de longitudes de aristas

#### **Interpretación del Grafo Coloreado:**

```
COLOR DEL NODO → SIGNIFICADO:
   🟡 Amarillo claro (grado 1-2): Extremos o nodos de paso
   🟠 Naranja (grado 3-4): Nodos de conexión importante
   🔴 Rojo oscuro (grado 5+): Nodos muy conectados (cruces, intersecciones)
```

**¿Qué buscar?**

| Patrón Visual | Significado | ¿Es Normal? |
|--------------|------------|-------------|
| Mayoría amarilla/naranja | Estructura lineal predominante | ✅ Sí, para torres |
| Muchos nodos rojos | Muchas intersecciones/cruces | ✅ Sí, en zonas con diagonales |
| Nodos rojos agrupados | Zona compleja (ej. módulo X) | ✅ Sí, esperable |
| Nodos rojos dispersos | Posibles errores o nodos mal fusionados | ⚠️ Verificar |

#### **Interpretación de Distribución de Grados:**

```
GRÁFICO DE BARRAS:
   Eje X: Grado del nodo (cuántas conexiones tiene)
   Eje Y: Cantidad de nodos con ese grado

¿Qué buscar?

   ✅ DISTRIBUCIÓN SALUDABLE:
      • Pico en grado 2 (nodos de paso)
      • Algunos nodos de grado 3-4 (intersecciones)
      • Pocos nodos de grado 5+ (cruces complejos)

   ⚠️ DISTRIBUCIÓN SOSPECHOSA:
      • Muchos nodos de grado 1 (extremos sueltos → posible fragmentación)
      • Muchos nodos de grado 6+ (posible error en fusión)
```

#### **Interpretación de Distribución de Longitudes:**

```
HISTOGRAMA:
   Eje X: Longitud de arista
   Eje Y: Cantidad de aristas con esa longitud

¿Qué buscar?

   ✅ DISTRIBUCIÓN SALUDABLE:
      • Distribución continua (sin picos aislados)
      • Pocas aristas muy cortas (< 0.5% del modelo)
      • Mayoría de longitudes similares

   ⚠️ DISTRIBUCIÓN SOSPECHOSA:
      • Pico grande en longitudes muy cortas (líneas redundantes no eliminadas)
      • Bimodalidad extrema (dos grupos distintos sin conexión)
```

---

### **4️⃣ Zoom en Área Central**

**Qué muestra:**
- **Izquierda**: Vista completa con rectángulo rojo indicando área de zoom
- **Derecha**: Zoom detallado del área central con nodos numerados

**Qué buscar:**

| Elemento | ¿Qué verificar? | Interpretación |
|----------|----------------|----------------|
| **Nodos muy cercanos** | ¿Hay nodos casi encimados? | ❌ Tolerancia de contracción muy baja |
| **Líneas quebradas** | ¿Hay líneas en zig-zag? | ❌ Tolerancia de colinealidad muy baja |
| **Líneas muy cortas** | ¿Hay segmentos < 1% del zoom? | ❌ Tolerancia de longitud muy baja |
| **Etiquetas numeradas** | ¿Los nodos tienen sentido estructural? | ✅ Verificación manual |

**Uso práctico:**

```python
# Si ves problemas en el zoom, ajusta tolerancias:

# Problema: Nodos muy cercanos sin fusionar
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.02,  # ← AUMENTAR de 0.01 a 0.02
    ...
)

# Problema: Líneas quebradas no unificadas
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_angulo=5.0,  # ← AUMENTAR de 2.0 a 5.0
    ...
)

# Problema: Líneas muy cortas no eliminadas
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_longitud=0.01,  # ← AUMENTAR de 0.005 a 0.01
    ...
)
```

---

## 🔍 Casos de Uso Práctico

### **Caso 1: Verificar Unificación de Diagonales**

**Objetivo:** Confirmar que las diagonales divididas fueron unificadas

**Dónde mirar:**
1. **Visualización 2 (Paso 1→2)**: Debe haber reducción significativa de aristas
2. **Visualización 3 (Longitudes)**: Debe haber menos aristas cortas
3. **Visualización 4 (Zoom)**: Las diagonales deben verse como líneas continuas, no quebradas

**Ejemplo:**

```
ANTES (Visualización 2, Paso 1):
   • Aristas: 1000
   • Diagonal visible como: ╱╲╱╲ (segmentos)

DESPUÉS (Visualización 2, Paso 2):
   • Aristas: 700 (-30%)  ✅ BIEN
   • Diagonal visible como: ╱ ╲ (continua)
```

---

### **Caso 2: Detectar Errores de Precisión Corregidos**

**Objetivo:** Verificar que los nodos duplicados por errores DXF fueron fusionados

**Dónde mirar:**
1. **Visualización 2 (Paso 0→1)**: Debe haber reducción de nodos
2. **Visualización 1 (Comparación)**: El grafo "después" debe verse menos "ruidoso"
3. **Visualización 4 (Zoom)**: No debe haber nodos casi encimados

**Indicadores:**

```
✅ BIEN CORREGIDO:
   • Reducción > 10% de nodos en Paso 0→1
   • En zoom: nodos bien espaciados
   • No hay "nubes" de nodos

⚠️ NECESITA AJUSTE:
   • Reducción < 5% de nodos
   • En zoom: aún hay nodos muy cercanos
   • Aumentar tolerancia_nodos a 0.02
```

---

### **Caso 3: Validar Eliminación de Líneas Redundantes**

**Objetivo:** Confirmar que las líneas muy cortas fueron eliminadas

**Dónde mirar:**
1. **Visualización 3 (Histograma de longitudes)**: Debe haber pocas aristas cortas
2. **Visualización 2 (Paso 2→3)**: Debe haber reducción de aristas
3. **Visualización 4 (Zoom)**: No debe haber segmentos casi puntuales

**Criterios:**

```
✅ BIEN LIMPIADO:
   • Histograma: < 5% de aristas en el bin más bajo
   • Reducción: > 3% de aristas en Paso 2→3
   • Zoom: sin segmentos < 0.5% del área

⚠️ NECESITA AJUSTE:
   • Histograma: > 10% de aristas muy cortas
   • Aumentar tolerancia_longitud a 0.01
```

---

## 🎨 Colores y Leyenda

### **Colores por Visualización:**

| Visualización | Color | Significado |
|--------------|-------|------------|
| **Comparación** | 🔴 Rojo | Antes del preprocesamiento |
| **Comparación** | 🟢 Verde | Después del preprocesamiento |
| **Proceso (Paso 0)** | ⚪ Gris | Grafo original |
| **Proceso (Paso 1)** | 🔴 Coral | Después de contracción |
| **Proceso (Paso 2)** | 🟡 Amarillo | Después de combinación |
| **Proceso (Paso 3)** | 🟢 Verde | Después de eliminación |
| **Estadísticas** | 🌡️ Gradiente | Grado del nodo (amarillo→rojo) |

### **Elementos Gráficos:**

| Elemento | Representación | Significado |
|----------|---------------|------------|
| **● Nodo** | Círculo | Punto de conexión entre líneas |
| **─ Arista** | Línea gris | Conexión entre dos nodos (línea DXF) |
| **□ Rectángulo rojo** | Borde punteado | Área de zoom |
| **📊 Cajas de texto** | Fondo coloreado | Información numérica |

---

## 📊 Métricas de Referencia

### **Reducciones Esperadas (Archivos DXF Típicos):**

| Métrica | Rango Normal | Interpretación |
|---------|-------------|----------------|
| **Reducción de nodos** | 15-30% | Errores de precisión corregidos |
| **Reducción de aristas** | 20-35% | Líneas fragmentadas unificadas |
| **Reducción total** | 18-32% | Mejora general del modelo |

### **Distribuciones Saludables:**

#### **Grados de Nodos:**
```
Grado 1:  5-10%   (extremos)
Grado 2:  60-80%  (nodos de paso) ← MAYORÍA
Grado 3:  10-20%  (bifurcaciones)
Grado 4:  3-8%    (cruces simples)
Grado 5+: 1-5%    (cruces complejos)
```

#### **Longitudes de Aristas:**
```
Muy cortas (< 1% del modelo):   < 5%
Cortas (1-5% del modelo):       10-20%
Medianas (5-20% del modelo):    40-60% ← MAYORÍA
Largas (> 20% del modelo):      10-30%
```

---

## 🐛 Detección de Problemas Visuales

### **Problema 1: Grafo "Ruidoso" Después del Preprocesamiento**

**Síntoma:**
- Aún hay muchos nodos pequeños y cercanos
- Distribución de longitudes tiene pico en valores muy bajos

**Causa:**
- Tolerancias demasiado conservadoras

**Solución:**
```python
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.02,       # ← Aumentar
    tolerancia_angulo=3.0,        # ← Aumentar
    tolerancia_longitud=0.01      # ← Aumentar
)
```

---

### **Problema 2: Reducción Excesiva (>50%)**

**Síntoma:**
- El grafo "después" se ve muy simplificado
- Estructuras importantes desaparecieron

**Causa:**
- Tolerancias demasiado agresivas

**Solución:**
```python
oriented_lines = preprocesar_lineas_dxf(
    oriented_lines_original,
    tolerancia_nodos=0.005,      # ← Reducir
    tolerancia_angulo=1.0,        # ← Reducir
    tolerancia_longitud=0.001     # ← Reducir
)
```

---

### **Problema 3: Distribución Bimodal Extrema**

**Síntoma:**
- Histograma de longitudes tiene dos picos separados
- No hay longitudes intermedias

**Causa:**
- El modelo tiene dos tipos de elementos muy diferentes (ej. estructura principal + detalles)

**Solución:**
- Es normal, no requiere ajuste
- Considerar preprocesar por separado si es problemático

---

## 🎯 Checklist de Validación Visual

Después de ejecutar las visualizaciones, verifica:

### **Visualización 1 (Comparación):**
- [ ] El grafo "después" se ve menos denso
- [ ] Hay reducción numérica de nodos y aristas
- [ ] No hay pérdida de estructura general

### **Visualización 2 (Proceso):**
- [ ] Paso 0→1: Reducción de nodos visible
- [ ] Paso 1→2: Reducción de aristas significativa
- [ ] Paso 2→3: Reducción final de redundantes
- [ ] No hay pérdida de conectividad entre pasos

### **Visualización 3 (Estadísticas):**
- [ ] Distribución de grados tiene pico en grado 2
- [ ] Histograma de longitudes no tiene pico grande en valores bajos
- [ ] Grafo coloreado muestra estructura coherente

### **Visualización 4 (Zoom):**
- [ ] No hay nodos casi encimados
- [ ] Las líneas se ven continuas, no quebradas
- [ ] No hay segmentos muy cortos innecesarios

---

## 💡 Consejos Prácticos

### **Para Análisis Rápido:**
1. Ejecuta solo **Visualización 1** (comparación)
2. Verifica que haya reducción > 15%
3. Si es correcta, procede con el análisis de módulos

### **Para Análisis Detallado:**
1. Ejecuta todas las visualizaciones
2. Revisa **Visualización 2** para entender qué pasó en cada paso
3. Usa **Visualización 4** para verificar áreas específicas
4. Ajusta tolerancias si es necesario

### **Para Depuración:**
1. Usa **Visualización 4** con diferentes centros de zoom
2. Compara zonas con/sin problemas
3. Identifica patrones de error
4. Ajusta tolerancias específicamente para esos patrones

---

## 📚 Recursos Adicionales

- **`celda_visualizacion_grafos.py`**: Código fuente de las visualizaciones
- **`graph_preprocessing.py`**: Funciones de preprocesamiento
- **`RESPUESTAS_PREGUNTAS_USUARIO.md`**: Detalles técnicos del preprocesamiento

---

## ✅ Resumen

Las visualizaciones te permiten:

1. ✅ **Validar** que el preprocesamiento funcionó correctamente
2. ✅ **Diagnosticar** problemas en el modelo DXF
3. ✅ **Ajustar** tolerancias de forma informada
4. ✅ **Verificar** que las diagonales divididas fueron unificadas
5. ✅ **Entender** la estructura del grafo antes del análisis de módulos

**Próximo paso:** Si las visualizaciones muestran buena limpieza, ejecuta el análisis de módulos con confianza de que los datos de entrada son óptimos.
