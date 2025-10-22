# Análisis de Torres DXF

## Descripción

Este repositorio contiene un notebook de Jupyter para el análisis automatizado de estructuras de torres de telecomunicaciones a partir de archivos DXF.

## Características

- **Carga y validación de archivos DXF**: Extrae datos geométricos de archivos CAD
- **Análisis de contornos**: Identifica contornos izquierdo y derecho de la torre
- **Detección de secciones**: Divide la torre en secciones con características similares
- **Análisis de módulos**: Identifica y clasifica módulos estructurales
- **Reconocimiento de patrones**: Detecta familias estructurales (FAC_OH2, etc.)
- **Generación de parámetros**: Crea archivos de parámetros para uso en Revit

## Estructura del Proyecto

```
jmgg/
├── torre_dxf_analisis.ipynb    # Notebook principal
├── README.md                    # Este archivo
└── data/                        # Datos de prueba
    ├── ejemplos/                # Archivos DXF de ejemplo
    ├── patrones/                # Biblioteca de patrones estructurales
    └── resultados/              # Resultados esperados (validación)
```

### Archivos Principales

- `torre_dxf_analisis.ipynb`: Notebook principal con todo el análisis
- `data/`: Directorio con datos de prueba (ver [data/README.md](data/README.md))

## Requisitos

```python
ezdxf
matplotlib
numpy
pandas
```

## Uso

### Inicio Rápido

1. Abre el notebook `torre_dxf_analisis.ipynb` en Google Colab
2. Sube tu archivo DXF cuando se solicite (o usa uno de `data/ejemplos/`)
3. Asegúrate de tener `patrones_estructurales.json` en `data/patrones/`
4. Ejecuta todas las celdas
5. Los resultados se generarán automáticamente

### Con Datos de Prueba

```python
# En el notebook, puedes cargar directamente los datos de ejemplo:
ruta_dxf = "/content/data/ejemplos/torre_ejemplo.dxf"
```

## Outputs

- `secciones_torre.csv`: Información de secciones
- `modulos_torre_universal.csv`: Datos de módulos
- `PARAMETROS_FAMILIA_TORRE_[N]S.xlsx`: Parámetros para Revit
- Gráficos de visualización de la torre

## Compatibilidad

Este notebook está diseñado para ejecutarse en Google Colab.

---

Desarrollado para análisis estructural de torres de telecomunicaciones.
