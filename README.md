# 📊 Datasets — Analítica de Datos para la Toma de Decisiones

¡Bienvenido/a a este repositorio! Este espacio está destinado al almacenamiento, gestión y distribución de los conjuntos de datos utilizados en el **Diplomado de Grado en Análisis de Datos Aplicado a la Toma de Decisiones** de la **Fundación Universitaria Colombo Internacional (UNICOLOMBO)**.

El objetivo principal es centralizar los recursos de datos para garantizar la trazabilidad, reproducibilidad y un acceso rápido ("Raw") directamente desde entornos de desarrollo en Python como Jupyter Notebooks y Google Colab.

---

## 🏢 Casos de Estudio y Origen de los Datos

Los recursos almacenados en este repositorio se dividen en dos vertientes principales:

1. **DataRetail LATAM S.A.S. (Ficticio):** Una cadena de retail electrónico con operaciones en tiendas físicas, e-commerce y canales B2B en seis países de América Latina (Colombia, Perú, México, Argentina, Chile y Uruguay). Diseñado para simular retos del mundo real en consistencia y calidad de datos (valores nulos, duplicados, inconsistencias de texto y outliers).
2. **Datos Reales y Contratación Pública (Colombia):** Datos abiertos provenientes de plataformas oficiales como el **SECOP II**, enfocados en el análisis masivo de contratación electrónica, estructuración de compras públicas y analítica avanzada de datos gubernamentales.

---

## 📂 Inventario de Datasets disponibles

| Archivo | Módulo / Caso | Estado | Descripción |
| :--- | :--- | :--- | :--- |
| `Dataset_DataRetail_LATAM_S01.csv` | Sesión 1: Diagnóstico y Calidad | 🛠️ En Proceso | Archivo inicial para evaluar la calidad integral del dataset e identificar nulos, duplicados y outliers. |
| `Dataset_DataRetail_LATAM_S02.csv` | Sesión 2: Limpieza de Datos | 🛠️ En Proceso | Contiene registros con problemas estructurales para aplicar técnicas de imputación y tratamiento estadístico. |
| `SECOP_II_-_Contratos_Electrónicos_20260625.csv` | Analítica Avanzada / Casos Reales | 📥 Disponible | Dataset masivo (>160 MB) con registros detallados de contratos electrónicos de SECOP II para minería de datos y analítica predictiva. |

> ⚠️ **Nota sobre archivos grandes:** Debido a que el dataset de SECOP II supera el límite estándar de GitHub (100 MB), este repositorio utiliza **Git LFS (Large File Storage)** para gestionar su historial y almacenamiento.

---

## 🐍 ¿Cómo consumir estos datasets en Python (Pandas)?

Para evitar la descarga manual de los archivos, puedes importar los datasets directamente en tus entornos de Jupyter o Google Colab mediante su URL en formato **Raw**.

```python
import pandas as pd

# Ruta base del repositorio en modo RAW
BASE_URL = '[https://raw.githubusercontent.com/JoseIbarraH/datasets-analitica-de-datos/refs/heads/main/](https://raw.githubusercontent.com/JoseIbarraH/datasets-analitica-de-datos/refs/heads/main/)'

# --- Cargar Datasets de DataRetail ---
df_s01 = pd.read_csv(BASE_URL + 'Dataset_DataRetail_LATAM_S01.csv')
df_s02 = pd.read_csv(BASE_URL + 'Dataset_DataRetail_LATAM_S02.csv')

# --- Cargar Dataset Masivo de SECOP II ---
# Nota: Al estar en Git LFS, Pandas resolverá el puntero automáticamente al usar la URL Raw pública.
df_secop = pd.read_csv(BASE_URL + 'SECOP_II_-_Contratos_Electrónicos_20260625.csv', low_memory=False)

# Verificar la carga exitosa (Ejemplo con SECOP II)
print(f"Dimensiones del dataset SECOP II: {df_secop.shape}")
display(df_secop.head())