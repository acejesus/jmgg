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

## Archivo Principal

- `torre_dxf_analisis.ipynb`: Notebook principal con todo el análisis

## Requisitos

```python
ezdxf
matplotlib
numpy
pandas
```

## Uso

1. Sube tu archivo DXF cuando el notebook lo solicite
2. El notebook procesará automáticamente la torre
3. Se generarán archivos CSV y Excel con los resultados

## Outputs

- `secciones_torre.csv`: Información de secciones
- `modulos_torre_universal.csv`: Datos de módulos
- `PARAMETROS_FAMILIA_TORRE_[N]S.xlsx`: Parámetros para Revit
- Gráficos de visualización de la torre

## Compatibilidad

Este notebook está diseñado para ejecutarse en Google Colab.

---

Desarrollado para análisis estructural de torres de telecomunicaciones.
