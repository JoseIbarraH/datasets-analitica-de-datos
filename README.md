# 📊 Datasets — Analítica de Datos para la Toma de Decisiones

¡Bienvenido/a a este repositorio! Este espacio está destinado al almacenamiento, gestión y distribución de los conjuntos de datos utilizados en el **Diplomado de Grado en Análisis de Datos Aplicado a la Toma de Decisiones** de la **Fundación Universitaria Colombo Internacional (UNICOLOMBO)**.

El objetivo principal es centralizar los recursos de datos para garantizar la trazabilidad, reproducibilidad y un acceso rápido ("Raw") directamente desde entornos de desarrollo en Python como Jupyter Notebooks y Google Colab.

---

## 🏢 Caso de Estudio: DataRetail LATAM S.A.S.

Los datasets almacenados aquí pertenecen a **DataRetail LATAM S.A.S.**, una cadena ficticia de retail electrónico con operaciones en tiendas físicas, e-commerce y canales B2B en seis países de América Latina (Colombia, Perú, México, Argentina, Chile y Uruguay).

Cada archivo simula retos del mundo real en consistencia y calidad de datos, tales como:
* Valores nulos y registros duplicados.
* Inconsistencias de capitalización (ej. ciudades mal digitadas).
* Outliers en cantidades y montos de ventas.
* Desajustes de formatos y tipos de datos.

---

## 📂 Inventario de Datasets disponibles

| Archivo | Sesión / Módulo | Estado | Descripción |
| :--- | :--- | :--- | :--- |
| `Dataset_DataRetail_LATAM_S01.csv` | Sesión 1: Diagnóstico y Calidad | 🛠️ En Proceso | Archivo inicial para evaluar la calidad integral del dataset e identificar nulos, duplicados y outliers. |
| `Dataset_DataRetail_LATAM_S02.csv` | Sesión 2: Limpieza de Datos | 🛠️ En Proceso | Contiene registros con problemas estructurales para aplicar técnicas de imputación y tratamiento estadístico. |

---

## 🐍 ¿Cómo consumir estos datasets en Python (Pandas)?

Para evitar la descarga manual de los archivos, puedes clonar el flujo de trabajo importando el dataset directamente mediante su URL en formato **Raw**.

```python
import pandas as pd

# Ruta base de tu repositorio en modo RAW
BASE_URL = '[https://raw.githubusercontent.com/JoseIbarraH/datasets-analitica-de-datos/refs/heads/main/](https://raw.githubusercontent.com/JoseIbarraH/datasets-analitica-de-datos/refs/heads/main/)'

# Cargar Dataset de la Sesión 1
df_s01 = pd.read_csv(BASE_URL + 'Dataset_DataRetail_LATAM_S01.csv')

# Cargar Dataset de la Sesión 2
df_s02 = pd.read_csv(BASE_URL + 'Dataset_DataRetail_LATAM_S02.csv')

# Verificar la carga exitosa (Ejemplo con S01)
print(f"Dimensiones del dataset S01: {df_s01.shape}")
display(df_s01.head())
