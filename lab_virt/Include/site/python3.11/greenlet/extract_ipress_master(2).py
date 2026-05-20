import os
import re
import time
import json
import requests
import pandas as pd

from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

# CONFIGURACIÓN GENERAL

BASE_URL = "http://app20.susalud.gob.pe:8080/registro-renipress-webapp"

SEARCH_URL = (
    BASE_URL
    + "/listadoEstablecimientosRegistrados.htm?action=mostrarBuscar"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )
}

TARGET_RAZON_SOCIAL = "DIR.SUB-REG.DE SALUD LUCIANO CASTILLO C."

OUTPUT_RAW = "raw/renipress/"
OUTPUT_ANALYTICS = "analytics/"

os.makedirs(OUTPUT_RAW, exist_ok=True)
os.makedirs(OUTPUT_ANALYTICS, exist_ok=True)

# SESIÓN

session = requests.Session()
session.headers.update(HEADERS)

# FUNCIÓN AUXILIAR

def clean_text(text):
    if text is None:
        return None

    text = str(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# PASO 1
# OBTENER PÁGINA PRINCIPAL

print("=" * 60)
print("CONECTANDO A RENIPRESS...")
print("=" * 60)

response = session.get(SEARCH_URL)

if response.status_code != 200:
    raise Exception(
        f"Error al conectar con RENIPRESS: {response.status_code}"
    )

print("Conexión exitosa.")

# PASO 2
# GUARDAR HTML RAW

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

raw_html_path = (
    OUTPUT_RAW + f"renipress_search_page_{timestamp}.html"
)

with open(raw_html_path, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"HTML RAW guardado en: {raw_html_path}")

# PASO 3
# PARSEAR HTML

soup = BeautifulSoup(response.text, "lxml")

print("=" * 60)
print("ANALIZANDO FORMULARIOS...")
print("=" * 60)

forms = soup.find_all("form")

print(f"Formularios encontrados: {len(forms)}")

# PASO 4
# IDENTIFICAR INPUTS

all_inputs = soup.find_all(["input", "select"])

for inp in all_inputs:
    name = inp.get("name")
    input_type = inp.get("type")

    if name:
        print(f"[INPUT] {name} ({input_type})")

# PASO 5
# CONSTRUCCIÓN DE PAYLOAD

payload = {
    "razonSocial": TARGET_RAZON_SOCIAL
}

print("=" * 60)
print("PAYLOAD DE BÚSQUEDA")
print("=" * 60)

print(json.dumps(payload, indent=4, ensure_ascii=False))

# PASO 6
# INTENTO DE CONSULTA

print("=" * 60)
print("REALIZANDO CONSULTA...")
print("=" * 60)

try:

    search_response = session.post(
        SEARCH_URL,
        data=payload,
        timeout=60
    )

    print("STATUS:", search_response.status_code)

    result_html = search_response.text

    result_path = (
        OUTPUT_RAW + f"renipress_result_{timestamp}.html"
    )

    with open(result_path, "w", encoding="utf-8") as f:
        f.write(result_html)

    print(f"Resultado guardado: {result_path}")

except Exception as e:
    print("ERROR EN CONSULTA:")
    print(e)

    raise

# PASO 7
# PARSEAR RESULTADOS

print("=" * 60)
print("EXTRAYENDO TABLAS...")
print("=" * 60)

tables = pd.read_html(result_html)

print(f"Tablas encontradas: {len(tables)}")

# PASO 8
# IDENTIFICAR TABLA PRINCIPAL

target_df = None

for idx, df in enumerate(tables):

    print("=" * 40)
    print(f"TABLA {idx}")
    print("=" * 40)

    print(df.head())

    cols = [str(c).lower() for c in df.columns]

    if any("ipress" in c for c in cols):
        target_df = df.copy()

# PASO 9
# VALIDAR

if target_df is None:
    print("No se encontró tabla IPRESS.")
    print("Revisar HTML manualmente.")
    exit()

print("=" * 60)
print("TABLA PRINCIPAL IDENTIFICADA")
print("=" * 60)

print(target_df.head())

# PASO 10
# LIMPIEZA

target_df.columns = [
    clean_text(c)
    for c in target_df.columns
]

for col in target_df.columns:
    target_df[col] = target_df[col].astype(str).apply(clean_text)

# PASO 11
# FILTRO DSRSLCC

cols_lower = {
    c: c.lower()
    for c in target_df.columns
}

razon_cols = [
    c for c in target_df.columns
    if "razon" in cols_lower[c]
]

if razon_cols:

    razon_col = razon_cols[0]

    target_df = target_df[
        target_df[razon_col]
        .str.contains(
            TARGET_RAZON_SOCIAL,
            case=False,
            na=False
        )
    ]

# PASO 12
# GENERAR node_id

target_df = target_df.reset_index(drop=True)

target_df["node_id"] = (
    target_df.index + 1
)

# PASO 13
# EXPORTAR RAW

raw_csv = (
    OUTPUT_RAW
    + f"raw_renipress_dsrslcc_{timestamp}.csv"
)

target_df.to_csv(raw_csv, index=False)

print(f"RAW CSV exportado: {raw_csv}")

# PASO 14
# CONSTRUIR nodes_master_sullana.csv

nodes = pd.DataFrame()

column_mapping = {
    "Código IPRESS": "ipress_id",
    "Nombre IPRESS": "nombre_eess",
    "Categoría": "categoria",
    "Departamento": "departamento",
    "Provincia": "provincia",
    "Distrito": "distrito",
    "Dirección": "direccion"
}

for src, dst in column_mapping.items():

    if src in target_df.columns:
        nodes[dst] = target_df[src]

nodes["node_id"] = target_df["node_id"]

# PASO 15
# EXPORT FINAL

final_csv = (
    OUTPUT_ANALYTICS
    + "nodes_master_sullana.csv"
)

nodes.to_csv(final_csv, index=False)

print("=" * 60)
print("EXPORTACIÓN COMPLETADA")
print("=" * 60)

print(f"Archivo final: {final_csv}")

print("=" * 60)
print("RESUMEN")
print("=" * 60)

print(f"Total EE.SS.: {len(nodes)}")

print(nodes.head())

print("=" * 60)
print("PIPELINE FINALIZADO")
print("=" * 60)