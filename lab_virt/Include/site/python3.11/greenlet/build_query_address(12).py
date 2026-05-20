import pandas as pd
import numpy as np
import re
import os

# CONFIG

INPUT_FILE = "analytics/nodes_clean_stage1.csv"

OUTPUT_DIR = "analytics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR
    + "/nodes_geocoding_input.csv"
)

# LOAD

print("=" * 60)
print("CARGANDO DATASET...")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"Registros: {len(df)}")

# COPY

geo = df.copy()

# CLEAN TEXT

def clean_text(x):

    if pd.isna(x):
        return ""

    x = str(x).upper()

    x = re.sub(r"\s+", " ", x)

    x = x.strip()

    return x

# NORMALIZAR VARIABLES

cols_to_clean = [
    "nombrerazonsocial",
    "direccion",
    "distrito",
    "provincia",
    "departamento"
]

for col in cols_to_clean:

    geo[col] = geo[col].apply(clean_text)

# QUERY PRINCIPAL

def build_primary_query(row):

    parts = [

        row["nombrerazonsocial"],
        row["distrito"],
        row["provincia"],
        row["departamento"],
        "PERU"
    ]

    parts = [
        p for p in parts
        if p and p != "NAN"
    ]

    return ", ".join(parts)

geo["query_primary"] = geo.apply(
    build_primary_query,
    axis=1
)

# QUERY SECUNDARIA

def build_secondary_query(row):

    parts = [

        row["direccion"],
        row["distrito"],
        row["provincia"],
        row["departamento"],
        "PERU"
    ]

    parts = [
        p for p in parts
        if p and p != "NAN"
    ]

    return ", ".join(parts)

geo["query_secondary"] = geo.apply(
    build_secondary_query,
    axis=1
)

# QUERY FALLBACK

def build_fallback_query(row):

    parts = [

        row["distrito"],
        row["provincia"],
        row["departamento"],
        "PERU"
    ]

    parts = [
        p for p in parts
        if p and p != "NAN"
    ]

    return ", ".join(parts)

geo["query_fallback"] = geo.apply(
    build_fallback_query,
    axis=1
)

# VARIABLES GEO

geo["latitude"] = np.nan
geo["longitude"] = np.nan

geo["geocode_source"] = np.nan
geo["geocode_confidence"] = np.nan
geo["geocode_level"] = np.nan
geo["geocode_status"] = "PENDING"

geo["geocode_notes"] = np.nan

# PRIORIDAD

geo["geocode_priority"] = "PRIMARY"

# VALIDACIÓN

print("=" * 60)
print("VALIDANDO QUERIES...")
print("=" * 60)

print(
    geo[
        [
            "codigounico",
            "nombrerazonsocial",
            "query_primary"
        ]
    ].head(10)
)

# EXPORT

geo.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("ARCHIVO EXPORTADO")
print("=" * 60)

print(OUTPUT_FILE)

print("=" * 60)
print("TOTAL REGISTROS")
print("=" * 60)

print(len(geo))

print("=" * 60)
print("COLUMNAS")
print("=" * 60)

print(geo.columns.tolist())

print("=" * 60)
print("FINALIZADO")
print("=" * 60)