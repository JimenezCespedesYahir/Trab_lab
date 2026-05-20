import requests
import pandas as pd
import os
from urllib.parse import urlencode

# CONFIG

BASE_URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
)

AJAX_URL = (
    BASE_URL
    + "listadoEstablecimientosRegistrados.htm"
)

OUTPUT_DIR = "analytics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

# PARÁMETROS

params = {
    "action": "cargarEstablecimientos",

    # búsqueda libre
    "txt_filtrar": "DIR.SUB-REG.DE SALUD LUCIANO CASTILLO C.",

    # filtros vacíos
    "cmb_departamento": "0",
    "cmb_provincia": "0",
    "cmb_distrito": "0",
    "cmb_red": "0",
    "cmb_microRed": "0",
    "cmb_categoria": "0",

    # DataTables
    "iDisplayStart": "0",
    "iDisplayLength": "1000",

    # control
    "sEcho": "1"
}

# REQUEST

print("=" * 60)
print("CONSULTANDO ENDPOINT AJAX...")
print("=" * 60)

response = requests.get(
    AJAX_URL,
    params=params,
    headers=HEADERS,
    timeout=120
)

print("STATUS:", response.status_code)

# GUARDAR RAW

raw_path = "raw_ajax_response.txt"

with open(raw_path, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"RAW guardado: {raw_path}")

# INTENTAR JSON

try:

    data = response.json()

    print("=" * 60)
    print("JSON DETECTADO")
    print("=" * 60)

    print(data.keys())

except Exception as e:

    print("=" * 60)
    print("NO ES JSON")
    print("=" * 60)

    print(e)

    exit()

# DETECTAR DATASET

possible_keys = [
    "aaData",
    "data",
    "items"
]

dataset = None

for k in possible_keys:

    if k in data:

        dataset = data[k]

        print(f"Dataset encontrado en: {k}")

        break

if dataset is None:

    print("NO SE ENCONTRÓ DATASET")

    exit()

# DATAFRAME

df = pd.DataFrame(dataset)

print("=" * 60)
print("COLUMNAS DETECTADAS")
print("=" * 60)

print(df.columns.tolist())

print("=" * 60)
print("TOTAL REGISTROS")
print("=" * 60)

print(len(df))

# EXPORTAR

output_path = (
    OUTPUT_DIR
    + "/nodes_master_sullana.csv"
)

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("EXPORTADO")
print("=" * 60)

print(output_path)

print("=" * 60)
print(df.head())
print("=" * 60)