# Validación espacial y separación de calidad geográfica
# Proyecto:
# HVRPTW farmacéutico - DIRESA Luciano Castillo Colonna


import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

import os

os.makedirs(
    "analytics",
    exist_ok=True
)

# CONFIGURACIÓN

INPUT_FILE = "analytics/nodes_geocoded_nominatim.csv"

OUTPUT_DIR = "analytics"

OUTPUT_HIGH_MEDIUM = (
    f"{OUTPUT_DIR}/nodes_high_medium.csv"
)

OUTPUT_LOW = (
    f"{OUTPUT_DIR}/nodes_low_confidence.csv"
)

OUTPUT_DUPLICATES = (
    f"{OUTPUT_DIR}/nodes_duplicate_coordinates.csv"
)

OUTPUT_SUSPICIOUS = (
    f"{OUTPUT_DIR}/nodes_suspicious_nodes.csv"
)

# tolerancia para detectar coordenadas iguales
ROUND_DECIMALS = 5

# CARGA DE DATOS

print("\n========================================")
print("CARGANDO DATASET")
print("========================================")

df = pd.read_csv(INPUT_FILE)

print(f"Total registros: {len(df)}")

# =========================================================
# NORMALIZACIÓN
# =========================================================

print("\n========================================")
print("NORMALIZANDO VARIABLES")
print("========================================")

# nombres esperados
expected_cols = [
    "latitude",
    "longitude",
    "geocode_confidence",
    "geocode_level",
    "geocode_status",
    "geocode_type"
]

for col in expected_cols:
    if col not in df.columns:
        raise ValueError(f"Falta columna requerida: {col}")

# convertir coordenadas
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# VALIDACIÓN BÁSICA

print("\n========================================")
print("VALIDACIÓN BÁSICA")
print("========================================")

# coordenadas nulas
null_coords = df[
    df["latitude"].isna() |
    df["longitude"].isna()
]

print(f"Nodos sin coordenadas: {len(null_coords)}")

# DETECCIÓN DE COORDENADAS DUPLICADAS

print("\n========================================")
print("DETECTANDO COORDENADAS DUPLICADAS")
print("========================================")

df["lat_round"] = df["latitude"].round(ROUND_DECIMALS)
df["lon_round"] = df["longitude"].round(ROUND_DECIMALS)

duplicate_groups = (
    df.groupby(["lat_round", "lon_round"])
      .size()
      .reset_index(name="count")
)

duplicates = duplicate_groups[duplicate_groups["count"] > 1]

print(f"Grupos duplicados encontrados: {len(duplicates)}")

# unir con dataset original
duplicate_nodes = df.merge(
    duplicates,
    on=["lat_round", "lon_round"],
    how="inner"
)

duplicate_nodes.to_csv(
    OUTPUT_DUPLICATES,
    index=False,
    encoding="utf-8-sig"
)

print(f"Archivo generado: {OUTPUT_DUPLICATES}")

# NODOS SOSPECHOSOS

print("\n========================================")
print("DETECTANDO NODOS SOSPECHOSOS")
print("========================================")

suspicious_conditions = (
    (df["geocode_confidence"].isin(["LOW"])) |
    (df["geocode_type"].isin([
        "administrative",
        "city",
        "town",
        "village"
    ]))
)

suspicious_nodes = df[suspicious_conditions]

print(f"Nodos sospechosos: {len(suspicious_nodes)}")

suspicious_nodes.to_csv(
    OUTPUT_SUSPICIOUS,
    index=False,
    encoding="utf-8-sig"
)

print(f"Archivo generado: {OUTPUT_SUSPICIOUS}")

# SEPARACIÓN PRINCIPAL

print("\n========================================")
print("SEPARANDO DATASETS")
print("========================================")

# Dataset A:
# HIGH + MEDIUM

high_medium = df[
    df["geocode_confidence"].isin(
        ["HIGH", "MEDIUM"]
    )
].copy()

# opcional:
# excluir administrativos

high_medium = high_medium[
    ~high_medium["geocode_type"].isin([
        "administrative",
        "city",
        "town",
        "village"
    ])
]

# Dataset B:
# LOW

low_confidence = df[
    df["geocode_confidence"] == "LOW"
].copy()

# EXPORTACIÓN

high_medium.to_csv(
    OUTPUT_HIGH_MEDIUM,
    index=False,
    encoding="utf-8-sig"
)

low_confidence.to_csv(
    OUTPUT_LOW,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nArchivo generado: {OUTPUT_HIGH_MEDIUM}")
print(f"Archivo generado: {OUTPUT_LOW}")

# RESUMEN FINAL

print("\n========================================")
print("RESUMEN FINAL")
print("========================================")

print(f"Dataset original: {len(df)}")
print(f"High + Medium: {len(high_medium)}")
print(f"Low confidence: {len(low_confidence)}")
print(f"Duplicados: {len(duplicate_nodes)}")
print(f"Sospechosos: {len(suspicious_nodes)}")

print("\nVALIDACIÓN ESPACIAL COMPLETADA")