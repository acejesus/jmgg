# Instrucciones para Ejecutar el Análisis

## Opción A: Google Colab (Más Fácil)

### Paso 1: Abrir el Notebook
Clic aquí: https://colab.research.google.com/github/acejesus/jmgg/blob/claude/create-github-repo-011CUNUEEcbHj3AGkm9cDfwE/torre_dxf_analisis.ipynb

### Paso 2: Clonar el Repositorio en Colab
```python
# Ejecuta esto en la primera celda:
!git clone -b claude/create-github-repo-011CUNUEEcbHj3AGkm9cDfwE https://github.com/acejesus/jmgg.git
%cd jmgg
```

### Paso 3: Configurar Rutas
```python
# Las rutas ya estarán configuradas automáticamente:
ruta_dxf = "data/ejemplos/TORRE 3 SECCIONES_35.dxf"
ruta_json = "data/patrones/patrones_estructurales.json"
```

### Paso 4: Ejecutar
- Ejecuta todas las celdas: Runtime → Run all
- O ejecuta celda por celda con Shift + Enter

---

## Opción B: Jupyter Local

### Requisitos
```bash
pip install ezdxf matplotlib numpy pandas
```

### Descargar Archivos
```bash
# Clonar el repositorio
git clone -b claude/create-github-repo-011CUNUEEcbHj3AGkm9cDfwE https://github.com/acejesus/jmgg.git
cd jmgg

# Abrir Jupyter
jupyter notebook torre_dxf_analisis.ipynb
```

---

## Archivos Disponibles

✅ DXF: `data/ejemplos/TORRE 3 SECCIONES_35.dxf` (133 KB)
✅ JSON: `data/patrones/patrones_estructurales.json` (34 patrones)

---

## Resultados Esperados

Al ejecutar el notebook obtendrás:

1. **CSVs de análisis:**
   - `secciones_torre.csv` - Información de las 3 secciones
   - `modulos_torre_universal.csv` - Módulos detectados
   - `2_módulos_torre.csv` - Módulos con patrones identificados

2. **Excel de parámetros:**
   - `PARAMETROS_FAMILIA_TORRE_3S.xlsx` - Para Revit

3. **Gráficos de diagnóstico:**
   - Visualización de la torre completa
   - Diagramas de cada módulo
   - Imágenes en `diagnosticos/`

4. **Estadísticas:**
   - Número de módulos por sección
   - Patrones estructurales detectados
   - Distribución de familias

---

## Troubleshooting

### Error: "Archivo DXF no encontrado"
```python
# Verifica que clonaste el repositorio correctamente:
!ls -la data/ejemplos/
```

### Error: "Módulo ezdxf no encontrado"
```python
# Instala las dependencias:
!pip install ezdxf matplotlib numpy pandas
```

### Notebook muy lento
- La torre tiene muchos elementos, puede tardar 2-5 minutos
- Los gráficos con muchos módulos tardan más

---

Creado por Claude Code 🤖
