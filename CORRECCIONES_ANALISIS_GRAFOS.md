# Correcciones al Análisis de Módulos con Grafos

## Problema Identificado

El análisis previo detectaba **horizontales internas** (que no van de lado a lado) como límites de módulos. Esto causaba una sobre-segmentación incorrecta.

### Ejemplo del Problema

En la torre de prueba:
- ❌ Detectaba horizontales en Y=2.0, 5.9, 9.9 como límites de módulos
- ✅ Solo Y=4.0 es un límite real (va de contorno izquierdo a contorno derecho)

### Causa Raíz

Las horizontales internas están formadas por segmentos cortos que **NO** cruzan toda la torre, mientras que las horizontales límite están formadas por múltiples segmentos colineales que en conjunto **SÍ** van de lado a lado.

---

## Solución Implementada

### 1. Agrupación de Líneas Colineales

**Función:** `agrupar_segmentos_colineales()`

Agrupa segmentos del grafo que están en la misma línea recta, aunque estén separados por nodos intermedios.

```python
# Ejemplo:
# Segmento 1: (0, 4, 0) -> (2, 4, 0)
# Segmento 2: (2, 4, 0) -> (4, 4, 0)
# Resultado: 1 grupo horizontal continuo de X=0 a X=4
```

**Características:**
- Verifica colinealidad mediante ángulos entre vectores
- Funciona para horizontales, verticales y diagonales
- Calcula la extensión total del grupo (x_min, x_max, y_min, y_max)

### 2. Verificación de Horizontales Lado a Lado

**Función:** `horizontal_va_lado_a_lado()`

Verifica si un grupo de horizontales colineales va desde el contorno izquierdo hasta el contorno derecho de la torre.

```python
# Verifica:
# 1. x_min ≈ límite_izquierdo (dentro de tolerancia)
# 2. x_max ≈ límite_derecho (dentro de tolerancia)
```

**Parámetros configurables:**
- `tolerance_contorno`: Distancia máxima al contorno (default: 0.5m)

### 3. Obtención de Contornos

**Función:** `obtener_contornos_en_seccion()`

Extrae las coordenadas X de los contornos izquierdo y derecho en cada sección, usando el eje de simetría como divisor.

### 4. Análisis Mejorado

**Función:** `obtener_horizontales_lado_a_lado()`

Pipeline completo:
1. Obtener contornos de la sección
2. Agrupar horizontales colineales
3. Filtrar solo las que van de lado a lado
4. Retornar alturas Y válidas

---

## Cambios en el Código

### Antes (código original)

```python
def obtener_horizontales_de_grafo(G, section_bounds, tolerance=0.01):
    horizontales = []
    for edge in G.edges():
        if es_horizontal(edge, tolerance):
            horizontales.append(edge)  # ❌ Incluye TODAS las horizontales
    return horizontales
```

### Después (código corregido)

```python
def obtener_horizontales_lado_a_lado(G, section_bounds, symmetry_axis, ...):
    # 1. Obtener contornos
    contorno_izq, contorno_der = obtener_contornos_en_seccion(...)

    # 2. Agrupar horizontales colineales
    grupos = agrupar_segmentos_colineales(G, ...)

    # 3. Filtrar solo las que van de lado a lado
    alturas_validas = []
    for grupo in grupos:
        if horizontal_va_lado_a_lado(grupo, contorno_izq, contorno_der):
            alturas_validas.append(grupo['y_avg'])  # ✅ Solo válidas

    return alturas_validas
```

---

## Aplicación a Diagonales

La misma lógica de agrupación colineal se aplica a las diagonales en módulos X:

**Función:** `obtener_alturas_de_diagonales_mejorado()`

1. Agrupa diagonales colineales
2. Extrae solo los extremos exteriores (y_min, y_max) de cada grupo
3. Excluye las coordenadas Y de los centros de módulos X (estrellas)

---

## Parámetros de Configuración

### Tolerancias Principales

| Parámetro | Valor Default | Descripción |
|-----------|---------------|-------------|
| `tolerance_horizontal` | 0.01 m | Para clasificar una línea como horizontal |
| `tolerance_colineal` | 2.0° | Ángulo máximo para considerar segmentos colineales |
| `tolerance_contorno` | 0.5 m | Distancia máxima al contorno para "llegar" |

### Ajuste Recomendado

- **Torres regulares**: Usar valores default
- **Torres con geometría irregular**: Aumentar `tolerance_contorno` a 0.8-1.0m
- **DXF con errores de precisión**: Aumentar `tolerance_colineal` a 3.0-5.0°

---

## Resultados Esperados

### Antes de la Corrección
```
Sección 1: 9 módulos (incorrectos por horizontales internas)
  M1: h=1.980m
  M2: h=1.980m
  M3: h=1.980m
  ...
  M9: h=0.000m  ← Módulo vacío por doble conteo
```

### Después de la Corrección
```
Sección 1: 4 módulos (correctos, solo horizontales lado a lado)
  M1: h=3.960m
  M2: h=3.960m
  M3: h=3.960m
  M4: h=3.962m
```

---

## Mensajes de Debug

Con `verbose=True`, el análisis muestra información detallada:

```
📊 Contornos: Izq [0.50], Der [6.93]
📊 Grupos horizontales encontrados: 12
   Y=2.000: 2 segs, X=[2.00 - 4.93], ext=2.93, lado_a_lado=❌
   Y=4.000: 2 segs, X=[0.52 - 6.91], ext=6.39, lado_a_lado=✅
   Y=5.900: 3 segs, X=[1.50 - 5.43], ext=3.93, lado_a_lado=❌
   ...
✅ Horizontales válidas (lado a lado): 4
```

---

## Archivos Modificados

1. **analisis_modulos_grafos_corregido.py**: Versión corregida completa
2. **CORRECCIONES_ANALISIS_GRAFOS.md**: Esta documentación

---

## Uso

```python
# Copiar y ejecutar en Google Colab o Jupyter

# El script carga automáticamente:
# - /content/tower_data/oriented_lines.csv
# - /content/tower_data/sections.csv

# Y genera:
# - Análisis de módulos corregido
# - Visualización con límites correctos
# - Resumen detallado por sección
```

---

## Testing

Para verificar la corrección:

1. Ejecutar el script con `verbose=True`
2. Verificar que las horizontales internas se marcan como `lado_a_lado=❌`
3. Verificar que las horizontales límite se marcan como `lado_a_lado=✅`
4. Comparar el número de módulos con el diseño real de la torre

---

## Notas Técnicas

### Complejidad Computacional

- Agrupación colineal: O(n²) donde n = número de segmentos en la sección
- Optimización futura: Usar índices espaciales para reducir a O(n log n)

### Limitaciones

- Asume que los contornos son los puntos más extremos en X
- Torres con contornos curvos pueden requerir lógica adicional
- No detecta horizontales que solo tocan un contorno (deben tocar ambos)

### Extensiones Futuras

1. Soporte para torres asimétricas
2. Detección de horizontales en ángulo (no perfectamente horizontales)
3. Validación cruzada con DXF layers (si disponible)

---

## Contacto y Soporte

Si encuentras casos donde la detección falla:

1. Verifica los parámetros de tolerancia
2. Ejecuta con `verbose=True` para debug
3. Revisa que los datos CSV estén correctamente orientados
4. Comparte el output de debug para análisis

---

**Fecha:** 2025-10-31
**Versión:** 2.0 (Corrección de Colinealidad)
**Estado:** ✅ Listo para Producción
