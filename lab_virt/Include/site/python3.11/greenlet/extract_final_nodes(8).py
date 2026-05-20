from playwright.sync_api import sync_playwright
import requests
import pandas as pd
import json
import os
import time
from urllib.parse import parse_qs

# CONFIG

URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
    "?action=mostrarBuscar"
)

AJAX_URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
)

SEARCH_TERM = "DIR.SUB-REG.DE SALUD LUCIANO CASTILLO C."

os.makedirs("analytics", exist_ok=True)

# PLAYWRIGHT SOLO PARA SESIÓN

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    print("=" * 60)
    print("ABRIENDO RENIPRESS...")
    print("=" * 60)

    page.goto(URL, timeout=120000)

    time.sleep(5)

    cookies = page.context.cookies()

    browser.close()

# SESSION

session = requests.Session()

for c in cookies:

    session.cookies.set(
        c["name"],
        c["value"]
    )

# HEADERS

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": URL,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

# PAYLOAD REAL

payload = {
    "draw": 1,

    "start": 0,
    "length": 1000,

    "search[value]": "",
    "search[regex]": "false",

    "txt_filtrar": SEARCH_TERM,

    "cmb_estado": 1,
    "cmb_departamento": 0,
    "cmb_provincia": 0,
    "cmb_distrito": 0,
    "cmb_institucion": 0,
    "cmb_tipo_establecimiento": 0,
    "cmb_clasificacion": 0,
    "cmb_categoria": 0,
    "cmb_unidadEjecutora": 0,
    "cmb_servicio": 0,
    "cmb_autoridadSanitaria": 0,
    "cmb_red": 0,
    "cmb_microRed": 0,
    "cmb_clas": 0,
    "cmb_colegio": 0,
    "cmb_especialidad": 0,
    "cmb_quintil": 0,
    "cmb_telesalud": 0,

    "ra_reg": "on"
}

# COLUMNAS DATATABLES

columns = [
    "codigounico",
    "nombrerazonsocial",
    "departamento",
    "provincia",
    "distrito",
    "direccion",
    "estado",
    "situacion",
    "condicion",
    "inspecion",
    "clasificacion",
    "tipo",
    "idautosanit",
    "idred",
    "idmicrored",
    "disa",
    "red",
    "microred",
    "idunidadejec",
    "unidadejec",
    "categoria",
    "telefeno",
    "tipoDocumentoCategoria",
    "numeroCategoria",
    "inicioActividad",
    "horaAtencion",
    "responsable",
    "fecha_inspecion",
    "id",
    "institucion",
    "codigounico2",
    "ubigeo"
]

for idx, col in enumerate(columns):

    payload[f"columns[{idx}][data]"] = col
    payload[f"columns[{idx}][name]"] = ""
    payload[f"columns[{idx}][searchable]"] = "true"
    payload[f"columns[{idx}][orderable]"] = "true"
    payload[f"columns[{idx}][search][value]"] = ""
    payload[f"columns[{idx}][search][regex]"] = "false"

payload["order[0][column]"] = 0
payload["order[0][dir]"] = "asc"

# REQUEST

print("=" * 60)
print("CONSULTANDO BACKEND...")
print("=" * 60)

response = session.post(
    AJAX_URL +
    "?action=cargarEstablecimientos"
    "&txt_filtrar=" + SEARCH_TERM.replace(" ", "+"),
    data=payload,
    headers=headers,
    timeout=120
)

print("STATUS:", response.status_code)

# RAW

with open(
    "response_backend.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(response.text)

print("RAW guardado.")

# JSON

data = response.json()

print("=" * 60)
print("KEYS")
print("=" * 60)

print(data.keys())

# DATASET

df = pd.DataFrame(data["data"])

print("=" * 60)
print("TOTAL REGISTROS")
print("=" * 60)

print(len(df))

print("=" * 60)
print("COLUMNAS")
print("=" * 60)

print(df.columns.tolist())

# EXPORT

output_path = (
    "analytics/nodes_master_sullana.csv"
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