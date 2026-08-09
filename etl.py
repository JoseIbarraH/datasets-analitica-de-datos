# -*- coding: utf-8 -*-
"""
ETL automatizado · Observatorio de contratación de Cartagena
------------------------------------------------------------
Extrae los contratos del SECOP II (Cartagena/Bolívar) desde la API Socrata de
datos.gov.co, los limpia y guarda 'secop2_limpio.parquet' listo para la app.

IMPORTANTE — diferencia con el notebook:
El notebook limpiaba un CSV exportado con formato colombiano ("$18.214.500",
fechas MM/DD/YYYY). La API Socrata devuelve los datos en formato NATIVO:
números planos (18214500) y fechas ISO (2024-05-15T00:00:00.000). Por eso aquí
el parseo es distinto (to_numeric / to_datetime directos). La corrección de los
2 contratos mal digitados se conserva (va indexada por 'ID Contrato').

Uso:
    python etl.py            # ejecuta el ETL completo y guarda el parquet
    python etl.py --inspect  # imprime los campos reales de la API (para verificar el mapeo)
"""

import sys
import time
import urllib.parse
import urllib.request
import json

import numpy as np
import pandas as pd

# =========================================================================== #
# CONFIGURACIÓN  ── revisa estos valores una vez contra el dataset real
# =========================================================================== #
DOMINIO = "www.datos.gov.co"
RESOURCE_ID = "jbjy-vk9h"          # SECOP II - Contratos Electrónicos (confirmado)

# Filtro de ubicación (SoQL). Confirmado: en el campo 'ciudad' Cartagena
# aparece como 'Cartagena' (101.936 contratos).
LOCATION_WHERE = "ciudad='Cartagena'"

# Estados que NO representan gasto real (procesos que no llegaron a suscribirse).
# Se excluyen del análisis: son la causa de los valores imposibles (billones
# falsos) que aparecían en el dataset. Comparación en minúsculas por seguridad,
# porque la fuente mezcla mayúsculas/minúsculas ('terminado', 'Cancelado', ...).
ESTADOS_EXCLUIDOS = {"borrador", "cancelado"}

# App token de Socrata (opcional pero recomendado: sube el límite de requests).
# En GitHub Actions se inyecta como variable de entorno SOCRATA_APP_TOKEN.
import os
APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN", "").strip()

PAGE = 50000                        # filas por página (SODA admite grandes con token)
SALIDA = "secop2_limpio.parquet"

# Mapeo  campo_API(snake_case) -> Nombre bonito que usa la app/notebook.
# Son los nombres MÁS PROBABLES; confírmalos con `python etl.py --inspect`.
RENAME_MAP = {
    "id_contrato": "ID Contrato",
    "referencia_del_contrato": "Referencia del Contrato",
    "nombre_entidad": "Nombre Entidad",
    "nit_entidad": "Nit Entidad",
    "departamento": "Departamento",
    "ciudad": "Ciudad",
    "orden": "Orden",
    "sector": "Sector",
    "rama": "Rama",
    "estado_contrato": "Estado Contrato",
    "duraci_n_del_contrato": "Duracion del Contrato",
    "tipo_de_contrato": "Tipo de Contrato",
    "modalidad_de_contratacion": "Modalidad de Contratacion",
    "proveedor_adjudicado": "Proveedor Adjudicado",
    "es_pyme": "Es Pyme",
    "es_grupo": "Es Grupo",
    "habilita_pago_adelantado": "Habilita Pago Adelantado",
    "valor_del_contrato": "Valor del Contrato",
    "valor_pagado": "Valor Pagado",
    "valor_pendiente_de_ejecucion": "Valor Pendiente de Ejecucion",
    "fecha_de_firma": "Fecha de Firma",
    "fecha_de_inicio_del_contrato": "Fecha de Inicio del Contrato",
    "fecha_de_fin_del_contrato": "Fecha de Fin del Contrato",
    "dias_adicionados": "Dias adicionados",
}

# Columnas imprescindibles para que la app funcione. Si falta alguna, el ETL
# se detiene con un mensaje claro (probablemente un nombre de campo cambió).
CRITICAS = [
    "ID Contrato", "Valor del Contrato", "Fecha de Firma",
    "Fecha de Inicio del Contrato", "Fecha de Fin del Contrato",
    "Modalidad de Contratacion", "Dias adicionados", "Es Pyme",
    "Nombre Entidad", "Proveedor Adjudicado", "Valor Pagado",
    "Valor Pendiente de Ejecucion", "Referencia del Contrato", "Nit Entidad",
    "Estado Contrato",
]

LIMITE_SANO = 1e12  # 1 billón: techo imposible a nivel municipal (control de calidad)


# =========================================================================== #
# 1) EXTRACCIÓN desde Socrata (paginada)
# =========================================================================== #
def _url(offset, limit, select=None, where=None):
    params = {"$limit": limit, "$offset": offset}
    if where:
        params["$where"] = where
    if select:
        params["$select"] = select
    if APP_TOKEN:
        params["$$app_token"] = APP_TOKEN
    return f"https://{DOMINIO}/resource/{RESOURCE_ID}.json?" + urllib.parse.urlencode(params)


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "observatorio-cartagena/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def inspeccionar():
    """Imprime los campos reales y un conteo, para verificar el mapeo/filtro."""
    print("Campos disponibles en la API (primer registro):")
    fila = _get(_url(0, 1))
    if not fila:
        print("  (sin datos: revisa RESOURCE_ID)")
        return
    for k in sorted(fila[0].keys()):
        print("  -", k)
    print("\nEjemplo de valores de ubicación (para ajustar LOCATION_WHERE):")
    muestra = _get(_url(0, 5, select="departamento,ciudad"))
    for m in muestra:
        print("  ", m)


def extraer():
    print(f"Extrayendo de {RESOURCE_ID} · filtro: {LOCATION_WHERE}")
    filas, offset = [], 0
    while True:
        lote = _get(_url(offset, PAGE, where=LOCATION_WHERE))
        if not lote:
            break
        filas.extend(lote)
        print(f"  {len(filas):,} filas…")
        offset += PAGE
        if len(lote) < PAGE:
            break
        time.sleep(0.5)
    df = pd.DataFrame.from_records(filas)
    print(f"Total extraído: {len(df):,} filas × {df.shape[1]} columnas")
    return df


# =========================================================================== #
# 2) TRANSFORMACIÓN (adaptada al formato nativo de la API)
# =========================================================================== #
def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=RENAME_MAP)

    faltan = [c for c in CRITICAS if c not in df.columns]
    if faltan:
        print("\n[ERROR] Faltan columnas críticas tras el renombrado:")
        for c in faltan:
            print("   -", c)
        print("\nColumnas presentes:", sorted(df.columns.tolist()))
        print("Ajusta RENAME_MAP con los nombres reales (ver `python etl.py --inspect`).")
        sys.exit(1)

    # --- Fechas: la API entrega ISO 8601 -> to_datetime directo ---
    for col in ["Fecha de Firma", "Fecha de Inicio del Contrato",
                "Fecha de Fin del Contrato"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # --- Valores: la API entrega números planos -> to_numeric directo ---
    for col in ["Valor del Contrato", "Valor Pagado", "Valor Pendiente de Ejecucion"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Excluir procesos que NO son gasto real (Borrador/Cancelado) ---
    # Estos concentran valores imposibles (billones falsos digitados en borradores
    # o procesos abortados). No se corrigen: se descartan, porque no representan
    # contratación efectiva. Comparación en minúsculas por la fuente inconsistente.
    antes = len(df)
    estado_norm = df["Estado Contrato"].astype(str).str.strip().str.lower()
    df = df[~estado_norm.isin(ESTADOS_EXCLUIDOS)].copy()
    print(f"[filtro] Excluidos {antes - len(df):,} contratos en estado "
          f"{sorted(ESTADOS_EXCLUIDOS)} (no representan gasto real).")

    # --- Control de calidad: no deberían quedar valores imposibles ---
    n = int((df["Valor del Contrato"] > LIMITE_SANO).sum())
    if n:
        print(f"[AVISO] Quedan {n} contratos con valor > 1 billón pese al filtro. "
              f"Revísalos: podría haber un estado nuevo con datos sucios.")
    else:
        print("[ok] Sin valores imposibles (> 1 billón) tras el filtro.")

    # --- Días adicionados: numérico; si viene con decimales = separador de miles ---
    dias = pd.to_numeric(df["Dias adicionados"], errors="coerce")
    dec = (dias % 1 != 0) & dias.notna()
    dias.loc[dec] = dias.loc[dec] * 1000
    df["Dias adicionados"] = dias.round().astype("Int64")

    # --- Booleanos (Si/No -> True/False; otros -> <NA>) ---
    mapa_bool = {"Si": True, "Sí": True, "SI": True, "No": False, "NO": False,
                 "true": True, "false": False, "True": True, "False": False}
    for col in ["Es Pyme", "Es Grupo", "Habilita Pago Adelantado"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().map(mapa_bool).astype("boolean")

    # --- Categorías (ahorran memoria) ---
    for col in ["Departamento", "Ciudad", "Orden", "Sector", "Rama",
                "Estado Contrato", "Tipo de Contrato", "Modalidad de Contratacion"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


# =========================================================================== #
# 3) CARGA
# =========================================================================== #
def main():
    if "--inspect" in sys.argv:
        inspeccionar()
        return
    df = extraer()
    if df.empty:
        print("[ERROR] La extracción vino vacía. Revisa LOCATION_WHERE y RESOURCE_ID.")
        sys.exit(1)
    df = limpiar(df)
    df.to_parquet(SALIDA, index=False)
    total = df["Valor del Contrato"].sum()
    print(f"\n✓ Guardado {SALIDA}: {len(df):,} filas · "
          f"valor total ${total/1e12:.2f} B · "
          f"{df['Fecha de Firma'].min()} → {df['Fecha de Firma'].max()}")


if __name__ == "__main__":
    main()