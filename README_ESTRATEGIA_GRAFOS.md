# 🎯 Nueva Estrategia de Detección de Módulos Basada en Grafos

## 📋 Problema Identificado

El análisis anterior asumía **líneas continuas** de lado a lado de la torre:
- ✅ Diagonales continuas → definen módulos
- ❌ Horizontales continuas en el centro → descartadas

**PERO** con la representación de grafo:
- ❌ Las diagonales están **divididas en segmentos** (nodo central grado 6)
- ❌ Las horizontales están **divididas en segmentos** (nodo central grado 6)
- ❌ La lógica anterior **NO funciona**

---

## 🔍 Observaciones Clave (Tu Análisis)

**Has identificado correctamente que:**

1. **Horizontales divididas en módulos X:**
   - Están divididas en 2 segmentos
   - Se encuentran en un nodo común de grado 6
   - Este nodo es el cruce de las diagonales
   - **NO deberían definir la altura del módulo**

2. **Diagonales divididas en módulos X:**
   - También están divididas en 2 segmentos
   - Llegan al mismo nodo de grado 6
   - Son colineales entre sí
   - **SÍ deberían definir la altura del módulo** (usando extremos: inicio de una + fin de su colineal)

3. **Patrón visual:**
   ```
   Módulo X en grafo:
     ┌───────┐
     │ ╱─  ─╲│ ← Diagonal izq (2 segmentos colineales)
     │╱  ●6 ╲│ ← Nodo grado 6 (cruce central)
     │─●───●─│ ← Horizontal (2 segmentos)
     └───────┘
   ```

---

## 🎯 Nueva Estrategia Propuesta

### **Estrategia 1: Detectar Módulos X por Nodos de Alto Grado**

**Algoritmo:**
1. Buscar nodos de grado 5-6 en la sección
2. Verificar que estén cerca del eje de simetría
3. Analizar sus vecinos
4. Encontrar pares de vecinos colineales (forman líneas rectas pasando por el nodo)
5. Si hay ≥2 pares colineales Y al menos uno es diagonal → **es un módulo X**

**Función:** `detectar_modulos_x_por_nodos(G, section_bounds, symmetry_axis)`

**Resultado:**
```python
{
    'detected': True,  # ¿Se detectó módulo X?
    'candidates': 5,   # Nodos de grado alto encontrados
    'x_centers': [...], # Lista de centros de módulos X
    'num_x_modules': 1  # Cantidad de módulos X
}
```

---

### **Estrategia 2: Reconstruir Diagonales Completas**

**Algoritmo:**
1. Encontrar todos los segmentos diagonales en la sección
2. Para cada segmento, intentar extenderlo siguiendo segmentos colineales
3. Continuar hasta llegar a nodos extremos (sin más vecinos colineales)
4. Retornar la "diagonal completa" con sus extremos

**Función:** `reconstruir_diagonales_completas(G, section_bounds, symmetry_axis)`

**Resultado:**
```python
[
    {
        'segmentos': [(nodo1, nodo2), (nodo2, nodo3)],  # Segmentos que forman la diagonal
        'extremo_inicio': nodo1,
        'extremo_fin': nodo3,
        'y_min': 10.0,  # Coordenada Y del extremo inferior
        'y_max': 15.0,  # Coordenada Y del extremo superior
        'num_segmentos': 2
    },
    ...  # Una entrada por cada diagonal completa
]
```

**Uso para definir módulos:**
```python
alturas_modulos = [seccion_inicio, seccion_fin]

for diagonal in diagonales_completas:
    alturas_modulos.append(diagonal['y_min'])
    alturas_modulos.append(diagonal['y_max'])

# Los módulos están entre alturas consecutivas
```

---

### **Estrategia 3: Filtrar Horizontales Divididas**

**Algoritmo:**
1. Obtener todas las horizontales de la sección
2. Para cada horizontal, verificar sus nodos extremos
3. Si un extremo es un nodo de grado 5-6 con pares colineales → **está dividida**
4. Solo retornar horizontales NO divididas

**Función:** `filtrar_horizontales_divididas(horizontales, G)`

**Resultado:**
```python
# Horizontales válidas (no divididas)
[
    (x1, y1, z1, x2, y2, z2),
    (x1, y1, z1, x2, y2, z2),
    ...
]
```

---

## 🔧 Uso Completo

### **Función Principal:**

```python
from graph_module_detection import analizar_seccion_con_grafo

resultado = analizar_seccion_con_grafo(
    G=grafo,
    section=seccion_dict,
    symmetry_axis=1.25,
    tolerance=0.05,
    verbose=True
)
```

**Retorna:**
```python
{
    'metodo': 'grafo-diagonal',  # o 'grafo-horizontal'
    'alturas': [0.0, 5.2, 10.5, 15.0],  # Límites de módulos
    'num_modulos': 3,  # Cantidad de módulos
    'tiene_modulo_x': True,  # ¿Hay módulo X?

    # Si hay módulo X:
    'diagonales': [...],  # Diagonales reconstruidas

    # Si no hay módulo X:
    'horizontales': [...]  # Horizontales válidas
}
```

---

## 📊 Comparación de Estrategias

| Aspecto | Estrategia Anterior | Nueva Estrategia (Grafos) |
|---------|---------------------|---------------------------|
| **Representación** | Líneas continuas | Grafo con segmentos |
| **Detección módulo X** | Intersecciones con eje | Nodos de grado alto (5-6) |
| **Diagonales** | Busca líneas lado a lado | Reconstruye desde segmentos colineales |
| **Horizontales** | Busca líneas lado a lado | Filtra las divididas en módulos X |
| **Definición módulos** | Extremos de líneas | Extremos de diagonales reconstruidas |
| **Funciona con segmentos** | ❌ NO | ✅ SÍ |

---

## 🚀 Ejemplo de Uso

```python
import networkx as nx
import pandas as pd
from graph_module_detection import analizar_todas_secciones_con_grafo

# 1. Cargar datos
df_lines = pd.read_csv('/content/tower_data/oriented_lines.csv')
oriented_lines = [(row['x1'], row['y1'], row['z1'], row['x2'], row['y2'], row['z2'])
                  for _, row in df_lines.iterrows()]

df_sections = pd.read_csv('/content/tower_data/sections.csv')
sections = df_sections.to_dict('records')

symmetry_axis = 1.25  # O calcularlo

# 2. Crear grafo
G = crear_grafo_desde_lineas(oriented_lines)

# 3. Analizar todas las secciones
sections_con_modulos = analizar_todas_secciones_con_grafo(
    G, sections, symmetry_axis, tolerance=0.05
)

# 4. Resultados
for i, section in enumerate(sections_con_modulos):
    print(f"Sección {i+1}:")
    print(f"  Tipo: {section['tipo']}")
    print(f"  Módulos: {section['num_modulos']}")
    print(f"  Método: {section['metodo_deteccion']}")
    print(f"  Módulo X: {'Sí' if section['tiene_modulo_x'] else 'No'}")
```

**Salida esperada:**
```
🎯 ANÁLISIS DE MÓDULOS CON ESTRATEGIA DE GRAFOS
============================================================

📍 SECCIÓN 1/3

🔧 ANÁLISIS CON GRAFO - Sección Decreciente
    📏 Y: [19.500 - 24.000], h: 4.500
    🔍 Candidatos de grado alto: 1
    🎯 Módulos X detectados: 1
    ✅ Estrategia: DIAGONALES (módulo X detectado)
    📊 Diagonales reconstruidas: 2
        Diagonal 1: 2 segmentos, Y=[19.500-24.000]
        Diagonal 2: 2 segmentos, Y=[19.500-24.000]
    🎉 RESULTADO: 1 módulos [grafo-diagonal]
        D1: h=4.500, Y=[19.500-24.000]

... (resto de secciones)

✅ ANÁLISIS COMPLETADO
============================================================

📊 RESUMEN:
   • Total de módulos: 15
   • Distribución de métodos:
      - grafo-diagonal: 1 secciones
      - grafo-horizontal: 2 secciones
```

---

## 📁 Archivos del Módulo

| Archivo | Descripción |
|---------|-------------|
| **`graph_module_detection.py`** | Módulo completo con todas las funciones |
| **`celda_analisis_modulos_con_grafo.py`** | Celda lista para Colab |
| **`README_ESTRATEGIA_GRAFOS.md`** | Este archivo (documentación) |

---

## ✅ Ventajas de la Nueva Estrategia

1. ✅ **Funciona con segmentos divididos** (el problema principal)
2. ✅ **Detecta correctamente módulos X** incluso con diagonales fragmentadas
3. ✅ **Filtra horizontales divididas** que no deberían definir módulos
4. ✅ **Reconstruye diagonales** siguiendo segmentos colineales
5. ✅ **Adapta la estrategia** según la estructura real del grafo
6. ✅ **Usa información topológica** (grados de nodos, conectividad)

---

## 🎯 Próximos Pasos

1. **Probar con tus datos reales:**
   ```python
   sections_con_modulos = analizar_todas_secciones_con_grafo(G, sections, symmetry_axis)
   ```

2. **Comparar con método anterior:**
   - ¿Detecta correctamente los módulos X?
   - ¿Filtra las horizontales divididas?
   - ¿Reconstruye bien las diagonales?

3. **Ajustar si es necesario:**
   - `tolerance`: Tolerancia geométrica
   - `tolerance_angulo` en `son_colineales()`: Si las diagonales tienen desviación

4. **Validar resultados:**
   - Verificar que cada sección con módulo X sea detectada
   - Verificar que las alturas de módulos sean correctas
   - Comparar con valores esperados

---

## 🐛 Troubleshooting

### **Problema: No detecta módulo X esperado**

**Síntoma:**
```
🔧 ANÁLISIS CON GRAFO - Sección Decreciente
    🔍 Candidatos de grado alto: 0
    🎯 Módulos X detectados: 0
    ➖ Estrategia: HORIZONTALES (sin módulo X)
```

**Posibles causas:**
1. Nodo central no está cerca del eje de simetría
2. Nodo central tiene grado < 5
3. No hay pares colineales de diagonales

**Solución:**
```python
# Aumentar tolerancia para distancia al eje
# En detectar_modulos_x_por_nodos(), línea ~110:
distancia_al_eje < tolerance * 20  # Aumentar de 10 a 20
```

---

### **Problema: Reconstruye diagonales incorrectamente**

**Síntoma:**
```
📊 Diagonales reconstruidas: 5
    Diagonal 1: 1 segmentos, Y=[19.500-20.000]  ← Solo 1 segmento
    Diagonal 2: 1 segmentos, Y=[20.500-21.000]  ← Debería estar unida con la 1
```

**Posibles causas:**
1. Tolerancia angular muy estricta
2. Segmentos no son exactamente colineales

**Solución:**
```python
# Aumentar tolerancia angular en reconstruir_diagonales_completas()
if son_colineales(n_prev, extremo_actual, vecino, tolerancia_angulo=10.0):  # De 5.0 a 10.0
```

---

### **Problema: Filtra horizontales que SÍ deberían estar**

**Síntoma:**
```
📊 Horizontales encontradas: 5
✅ Horizontales válidas (no divididas): 0  ← Filtró todas!
```

**Posibles causas:**
1. Criterio de filtrado muy agresivo
2. Todos los nodos tienen grado alto

**Solución:**
```python
# Ajustar criterio en filtrar_horizontales_divididas()
if grado >= 6:  # Cambiar de >= 5 a >= 6 (más estricto)
```

---

## 📚 Referencias Técnicas

### **Conceptos de Teoría de Grafos Usados:**

- **Grado de un nodo:** Número de aristas conectadas
- **Nodos colineales:** Tres nodos en línea recta
- **Subgrafo:** Porción del grafo completo
- **Vecinos:** Nodos directamente conectados por una arista

### **Parámetros Clave:**

| Parámetro | Valor Default | Propósito |
|-----------|---------------|-----------|
| `tolerance` | 0.05 | Tolerancia geométrica general |
| `tolerancia_angulo` | 5.0° | Para considerar 3 puntos colineales |
| `grado_minimo` | 5 | Grado mínimo para considerar nodo como cruce de módulo X |
| `distancia_eje_factor` | 10 | Multiplicador de tolerance para distancia al eje |

---

## 🎉 Resumen

La nueva estrategia basada en grafos:

1. ✅ **Detecta módulos X** por nodos de alto grado cerca del eje
2. ✅ **Reconstruye diagonales** siguiendo segmentos colineales
3. ✅ **Filtra horizontales divididas** que no definen módulos
4. ✅ **Adapta la estrategia** (diagonales vs. horizontales) según la estructura
5. ✅ **Funciona correctamente** con líneas divididas en segmentos

**Resultado:** Detección precisa de módulos X incluso cuando las diagonales están fragmentadas en el grafo.
