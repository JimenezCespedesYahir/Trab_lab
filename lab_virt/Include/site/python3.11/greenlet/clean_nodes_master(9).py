import pandas as pd
import numpy as np
import re
import os

# CONFIG

INPUT_FILE = "analytics/nodes_master_sullana.csv"

OUTPUT_DIR = "analytics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# LOAD

print("=" * 60)
print("CARGANDO DATASET...")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"Registros originales: {len(df)}")

# COPIA

clean = df.copy()

# NORMALIZAR COLUMNAS

clean.columns = [
    c.strip().lower()
    for c in clean.columns
]

# LIMPIEZA TEXTO

def normalize_text(x):

    if pd.isna(x):
        return np.nan

    x = str(x)

    x = re.sub(r"\s+", " ", x)

    x = x.strip()

    return x

for col in clean.columns:

    clean[col] = clean[col].apply(normalize_text)

# DIRECCIONES DUPLICADAS

def clean_address(addr):

    if pd.isna(addr):
        return np.nan

    words = addr.split()

    half = len(words) // 2

    first_half = " ".join(words[:half])
    second_half = " ".join(words[half:])

    # detectar duplicación aproximada
    if first_half[:50] == second_half[:50]:
        return first_half

    return addr

clean["direccion"] = clean["direccion"].apply(clean_address)

# NORMALIZAR VACÍOS

clean.replace(
    ["", " ", "nan", "None", "NULL"],
    np.nan,
    inplace=True
)

# ELIMINAR DUPLICADOS

before = len(clean)

clean = clean.drop_duplicates(
    subset=["codigounico"]
)

after = len(clean)

print("=" * 60)
print("DUPLICADOS ELIMINADOS")
print("=" * 60)

print(before - after)

# VALIDAR COLUMNAS CRÍTICAS

critical_cols = [
    "codigounico",
    "nombrerazonsocial",
    "direccion",
    "categoria",
    "distrito"
]

print("=" * 60)
print("MISSING CRÍTICOS")
print("=" * 60)

for col in critical_cols:

    missing = clean[col].isna().sum()

    pct = missing / len(clean) * 100

    print(f"{col}: {missing} ({pct:.2f}%)")

# ESTADO OPERATIVO

print("=" * 60)
print("ESTADOS")
print("=" * 60)

if "estado" in clean.columns:

    print(
        clean["estado"]
        .value_counts(dropna=False)
    )

# EXPORT

output_file = (
    OUTPUT_DIR
    + "/nodes_clean_stage1.csv"
)

clean.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("EXPORTADO")
print("=" * 60)

print(output_file)

print("=" * 60)
print(clean.head())
print("=" * 60)