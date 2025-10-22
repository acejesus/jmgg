# Directorio de Datos

Este directorio contiene todos los archivos de prueba y configuración para el análisis de torres.

## Estructura de Carpetas

### 📁 `ejemplos/`
**Archivos DXF de entrada**
- Coloca aquí tus archivos `.dxf` de torres de ejemplo
- Recomendación: Nombra los archivos de forma descriptiva (ej: `torre_3_secciones.dxf`)
- Estos archivos se usarán como entrada para el análisis

**Ejemplo de uso:**
```
ejemplos/
├── torre_simple.dxf
├── torre_4_tramos.dxf
└── torre_compleja.dxf
```

### 📁 `patrones/`
**Archivos JSON con biblioteca de patrones estructurales**
- `patrones_estructurales.json`: Biblioteca de patrones para reconocimiento
- Define las familias estructurales (FAC_OH2, FAC_OV2, etc.)

**Ejemplo de contenido:**
```json
{
  "FAC_OH2": {
    "conexiones": [[1, 2], [2, 3], ...],
    "descripcion": "Familia estructural horizontal tipo 2"
  }
}
```

### 📁 `resultados/`
**Archivos de salida esperados (para validación)**
- CSVs con resultados de ejemplo
- Archivos Excel de parámetros
- Imágenes de diagnóstico

**Archivos típicos:**
```
resultados/
├── secciones_torre.csv
├── modulos_torre_universal.csv
├── PARAMETROS_FAMILIA_TORRE_3S.xlsx
└── diagnosticos/
    ├── tramo1_modulo1.png
    └── ...
```

## ¿Qué archivos necesitas subir?

### ✅ Archivos obligatorios:
1. **Al menos un archivo DXF** en `ejemplos/`
2. **Archivo de patrones** `patrones_estructurales.json` en `patrones/`

### 📋 Archivos opcionales:
- Resultados de ejemplo en `resultados/` (para validar que el notebook funciona correctamente)
- Múltiples archivos DXF con diferentes tipos de torres

## Formato de archivos

- **DXF**: AutoCAD DXF format
- **JSON**: UTF-8, formato válido
- **CSV**: UTF-8, separados por comas
- **Excel**: .xlsx

---

**Nota**: Los archivos muy grandes (>50MB) no deberían subirse a GitHub.
Para archivos grandes, considera usar Git LFS o proporcionar enlaces de descarga.
